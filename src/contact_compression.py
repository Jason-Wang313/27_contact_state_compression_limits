"""Local contact-cone model for contact state compression experiments."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class ContactMode:
    """A local point contact mode.

    normal_angle is the direction in which the robot must push to maintain the
    contact. mu controls the tangential action that can be transmitted without
    losing the contact. gain is a small mode-dependent transmission scale.
    """

    mode_id: int
    normal_angle: float
    mu: float
    gain: float


def wrap_angle(angle: float) -> float:
    return angle % (2.0 * math.pi)


def unit(angle: float) -> np.ndarray:
    return np.array([math.cos(angle), math.sin(angle)], dtype=float)


def tangent_from_normal(normal_angle: float) -> np.ndarray:
    return np.array([-math.sin(normal_angle), math.cos(normal_angle)], dtype=float)


def make_modes(count: int = 64, seed: int = 7) -> List[ContactMode]:
    """Create a deterministic library of contact modes.

    The modes cover the full contact-normal circle and vary friction. This
    makes contact-count compression pathological while leaving room for
    action-cone signatures to merge mechanically similar modes.
    """

    rng = np.random.default_rng(seed)
    modes: List[ContactMode] = []
    for idx in range(count):
        base = 2.0 * math.pi * idx / count
        jitter = rng.normal(0.0, 0.045)
        normal = wrap_angle(base + jitter)
        # Repeat a small number of friction regimes so the repair can merge
        # states that are truly close in action-cone behavior.
        mu_regime = [0.28, 0.42, 0.62, 0.86][idx % 4]
        mu = float(max(0.18, mu_regime + rng.normal(0.0, 0.025)))
        gain = float(0.92 + 0.16 * rng.random())
        modes.append(ContactMode(idx, normal, mu, gain))
    return modes


def transmitted_velocity(mode: ContactMode, action_angle: float) -> np.ndarray:
    """Map a unit action direction to an object/task velocity.

    This is a deliberately local approximation: the action must have a positive
    component into the contact normal; tangential transmission is saturated by a
    Coulomb-like friction cone. It is not a full simulator. It is the smallest
    model needed to test whether two contact modes share a safe task action.
    """

    n = unit(mode.normal_angle)
    t = tangent_from_normal(mode.normal_angle)
    u = unit(action_angle)
    normal_push = float(np.dot(u, n))
    if normal_push <= 0.0:
        return np.zeros(2)
    tangent_cmd = float(np.dot(u, t))
    tangent_limit = mode.mu * normal_push
    tangent_transmitted = float(np.clip(tangent_cmd, -tangent_limit, tangent_limit))
    slip_loss = 1.0 if abs(tangent_cmd) <= tangent_limit else 0.58
    return mode.gain * (normal_push * n + 0.72 * slip_loss * tangent_transmitted * t)


def feasible(
    mode: ContactMode,
    task_angle: float,
    action_angle: float,
    progress_margin: float = 0.16,
    contact_margin: float = 0.08,
) -> bool:
    n = unit(mode.normal_angle)
    u = unit(action_angle)
    if float(np.dot(u, n)) < contact_margin:
        return False
    v = transmitted_velocity(mode, action_angle)
    return float(np.dot(v, unit(task_angle))) >= progress_margin


def progress(mode: ContactMode, task_angle: float, action_angle: float) -> float:
    v = transmitted_velocity(mode, action_angle)
    return float(np.dot(v, unit(task_angle)))


def feasible_mask(mode: ContactMode, task_angle: float, actions: Sequence[float]) -> np.ndarray:
    return np.array([feasible(mode, task_angle, a) for a in actions], dtype=bool)


def action_grid(count: int = 180) -> np.ndarray:
    return np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)


def task_grid(count: int = 24) -> np.ndarray:
    return np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)


def normal_bin_key(mode: ContactMode, bins: int) -> str:
    idx = int(math.floor(wrap_angle(mode.normal_angle) / (2.0 * math.pi) * bins)) % bins
    return f"normal{bins}_{idx}"


def normal_friction_key(mode: ContactMode, normal_bins: int = 8, friction_bins: int = 2) -> str:
    nkey = normal_bin_key(mode, normal_bins)
    fidx = min(friction_bins - 1, int(mode.mu * friction_bins))
    return f"{nkey}_mu{fidx}"


def cone_signature_key(
    mode: ContactMode,
    probe_tasks: Sequence[float],
    actions: Sequence[float],
    action_sectors: int = 12,
) -> str:
    """A compact control-cone signature.

    For each probe task direction, record the coarse action sectors that contain
    at least one feasible action. Modes with the same signature are merged.
    """

    parts: List[str] = []
    sector_width = len(actions) / float(action_sectors)
    for task in probe_tasks:
        mask = feasible_mask(mode, task, actions)
        bits = 0
        if np.any(mask):
            for action_index, ok in enumerate(mask):
                if ok:
                    sector = int(action_index / sector_width)
                    bits |= 1 << min(action_sectors - 1, sector)
        parts.append(format(bits, "03x"))
    return "sig_" + "_".join(parts)


def build_groups(modes: Sequence[ContactMode], key_fn: Callable[[ContactMode], str]) -> Dict[str, List[ContactMode]]:
    groups: Dict[str, List[ContactMode]] = {}
    for mode in modes:
        groups.setdefault(key_fn(mode), []).append(mode)
    return groups


def representation_builders(
    modes: Sequence[ContactMode],
    actions: Sequence[float],
    tasks: Sequence[float],
) -> List[Tuple[str, Dict[str, List[ContactMode]]]]:
    probe_tasks = list(tasks[::4])
    return [
        ("contact_count", build_groups(modes, lambda m: "one_contact")),
        ("normal_2", build_groups(modes, lambda m: normal_bin_key(m, 2))),
        ("normal_4", build_groups(modes, lambda m: normal_bin_key(m, 4))),
        ("normal_8", build_groups(modes, lambda m: normal_bin_key(m, 8))),
        ("normal_16", build_groups(modes, lambda m: normal_bin_key(m, 16))),
        ("normal8_mu2", build_groups(modes, lambda m: normal_friction_key(m, 8, 2))),
        (
            "cone_signature_repair",
            build_groups(modes, lambda m: cone_signature_key(m, probe_tasks, actions, action_sectors=8)),
        ),
        ("raw_mode", build_groups(modes, lambda m: f"mode_{m.mode_id}")),
    ]


def choose_group_action(
    group_modes: Sequence[ContactMode],
    task_angle: float,
    actions: Sequence[float],
) -> Tuple[int, bool, int, int]:
    """Choose an action using only the group identity.

    Returns action index, whether a robust common action existed, number of
    individually controllable modes, and group size.
    """

    masks = [feasible_mask(mode, task_angle, actions) for mode in group_modes]
    controllable = [idx for idx, mask in enumerate(masks) if bool(np.any(mask))]
    if not controllable:
        return 0, True, 0, len(group_modes)
    intersection = np.ones(len(actions), dtype=bool)
    for idx in controllable:
        intersection &= masks[idx]
    if bool(np.any(intersection)):
        candidate_indices = np.flatnonzero(intersection)
        scores = []
        for aidx in candidate_indices:
            values = [progress(group_modes[midx], task_angle, actions[aidx]) for midx in controllable]
            scores.append(min(values))
        best = int(candidate_indices[int(np.argmax(scores))])
        return best, True, len(controllable), len(group_modes)

    # Non-robust fallback: choose the action with best average progress. This is
    # what a compressed controller would do if it did not know which mode inside
    # the alias class is active.
    avg_scores = []
    for action_angle in actions:
        vals = [progress(group_modes[midx], task_angle, action_angle) for midx in controllable]
        avg_scores.append(float(np.mean(vals)))
    return int(np.argmax(avg_scores)), False, len(controllable), len(group_modes)


def bits_for_groups(group_count: int) -> int:
    if group_count <= 1:
        return 0
    return int(math.ceil(math.log(group_count, 2)))
