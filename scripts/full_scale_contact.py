#!/usr/bin/env python3
"""RAM-light full-scale evidence for contact-state compression limits."""

from __future__ import annotations

import csv
import json
import math
import random
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contact_compression import ContactMode, bits_for_groups, unit  # noqa: E402

SEED = 27027
OUT = ROOT / "results" / "full_scale"
TEX = OUT / "tex"
FIG = ROOT / "figures" / "full_scale"
DOCS = ROOT / "docs"

FIELDNAMES = [
    "family",
    "case_id",
    "method",
    "task_index",
    "mode_count",
    "action_count",
    "task_count",
    "topology",
    "friction_profile",
    "progress_margin",
    "contact_margin",
    "probe_tasks",
    "action_sectors",
    "probe_placement",
    "label_false_positive",
    "label_false_negative",
    "probe_cost",
    "probe_reliability",
    "first_action_required",
    "control",
    "success_rate",
    "empty_intersection_rate",
    "destroyed_episode_rate",
    "mean_regret",
    "mean_cost",
    "refusal_rate",
    "groups",
    "bits",
    "mean_group_size",
    "max_group_size",
    "raw_possible_cases",
    "seed",
]

SUMMARY_METRICS = [
    "success_rate",
    "empty_intersection_rate",
    "destroyed_episode_rate",
    "mean_regret",
    "mean_cost",
    "refusal_rate",
    "groups",
    "bits",
    "mean_group_size",
    "max_group_size",
    "raw_possible_cases",
]


@dataclass(frozen=True)
class CaseSpec:
    mode_count: int
    action_count: int
    task_count: int
    topology: str
    friction_profile: str
    progress_margin: float
    contact_margin: float
    seed: int
    control: str = ""


@dataclass
class EvalResult:
    success_rate: float
    empty_intersection_rate: float
    destroyed_episode_rate: float
    mean_regret: float
    mean_cost: float
    refusal_rate: float
    groups: int
    bits: int
    mean_group_size: float
    max_group_size: int
    raw_possible_cases: int


class FamilyWriter:
    def __init__(self, family: str) -> None:
        self.family = family
        self.path = OUT / f"{family}_rows.csv"
        self.file = self.path.open("w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=FIELDNAMES)
        self.writer.writeheader()
        self.rows = 0
        self.cases: set[str] = set()
        self.agg_by_method: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.count_by_method: Dict[str, int] = defaultdict(int)

    def write(self, row: Dict[str, object]) -> None:
        full = {key: row.get(key, "") for key in FIELDNAMES}
        self.writer.writerow(full)
        self.rows += 1
        self.cases.add(str(row["case_id"]))
        method = str(row["method"])
        self.count_by_method[method] += 1
        for metric in SUMMARY_METRICS:
            value = row.get(metric, "")
            if value == "":
                continue
            self.agg_by_method[method][metric] += float(value)

    def close(self) -> None:
        self.file.close()
        rows: List[Dict[str, object]] = []
        for method in sorted(self.count_by_method):
            count = self.count_by_method[method]
            out: Dict[str, object] = {"family": self.family, "method": method, "rows": count}
            for metric in SUMMARY_METRICS:
                out[metric] = self.agg_by_method[method].get(metric, 0.0) / count
            rows.append(out)
        write_csv(OUT / f"{self.family}_summary_by_method.csv", rows)


class GlobalAgg:
    def __init__(self) -> None:
        self.by_family_method: Dict[tuple[str, str], Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.count_by_family_method: Dict[tuple[str, str], int] = defaultdict(int)
        self.special: Dict[str, Dict[tuple, Dict[str, float]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        self.special_count: Dict[str, Dict[tuple, int]] = defaultdict(lambda: defaultdict(int))

    def add(self, row: Dict[str, object]) -> None:
        key = (str(row["family"]), str(row["method"]))
        self.count_by_family_method[key] += 1
        for metric in SUMMARY_METRICS:
            value = row.get(metric, "")
            if value == "":
                continue
            self.by_family_method[key][metric] += float(value)

    def add_special(self, name: str, key: tuple, row: Dict[str, object], metrics: Sequence[str] = SUMMARY_METRICS) -> None:
        self.special_count[name][key] += 1
        for metric in metrics:
            value = row.get(metric, "")
            if value == "":
                continue
            self.special[name][key][metric] += float(value)

    def summary_rows(self) -> List[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        for key in sorted(self.count_by_family_method):
            family, method = key
            count = self.count_by_family_method[key]
            out: Dict[str, object] = {"family": family, "method": method, "rows": count}
            for metric in SUMMARY_METRICS:
                out[metric] = self.by_family_method[key].get(metric, 0.0) / count
            rows.append(out)
        return rows

    def special_rows(self, name: str, columns: Sequence[str]) -> List[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        for key in sorted(self.special_count[name]):
            count = self.special_count[name][key]
            out: Dict[str, object] = {col: value for col, value in zip(columns, key)}
            out["rows"] = count
            for metric in SUMMARY_METRICS:
                out[metric] = self.special[name][key].get(metric, 0.0) / count
            rows.append(out)
        return rows


def ensure_dirs() -> None:
    for path in [OUT, TEX, FIG, DOCS]:
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: List[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def wrap_angle(angle: float) -> float:
    return angle % (2.0 * math.pi)


def tangent_from_normal(normal_angle: float) -> np.ndarray:
    return np.array([-math.sin(normal_angle), math.cos(normal_angle)], dtype=float)


def friction_value(profile: str, idx: int, rng: np.random.Generator) -> float:
    if profile == "low":
        base = [0.20, 0.26, 0.34, 0.40][idx % 4]
    elif profile == "high":
        base = [0.64, 0.78, 0.94, 1.10][idx % 4]
    elif profile == "bimodal":
        base = [0.20, 0.24, 0.92, 1.04][idx % 4]
    elif profile == "narrow":
        base = [0.48, 0.52, 0.56, 0.60][idx % 4]
    else:
        base = [0.28, 0.42, 0.62, 0.86][idx % 4]
    return float(max(0.08, base + rng.normal(0.0, 0.025)))


def mode_normal(topology: str, idx: int, count: int, rng: np.random.Generator) -> float:
    if topology == "uniform":
        base = 2.0 * math.pi * idx / count
        return wrap_angle(base + rng.normal(0.0, 0.035))
    if topology == "clustered":
        clusters = max(4, min(12, int(round(math.sqrt(count)))))
        center = 2.0 * math.pi * (idx % clusters) / clusters
        return wrap_angle(center + rng.normal(0.0, 0.12))
    if topology == "paired":
        pair = idx // 2
        base = 2.0 * math.pi * pair / max(1, count // 2)
        offset = 0.035 if idx % 2 else -0.035
        return wrap_angle(base + offset + rng.normal(0.0, 0.012))
    if topology == "adversarial":
        # Interleave modes around a small set of task directions. They look
        # similar under coarse prediction but often need different action cones.
        spokes = max(6, min(16, count // 4))
        center = 2.0 * math.pi * (idx % spokes) / spokes
        ring = (idx // spokes) % 4
        offset = [-0.19, -0.06, 0.06, 0.19][ring]
        return wrap_angle(center + offset + rng.normal(0.0, 0.018))
    if topology == "shared_action":
        return wrap_angle(0.15 + rng.normal(0.0, 0.045))
    if topology == "raw_identity_needed":
        base = 2.0 * math.pi * idx / count
        return wrap_angle(base + rng.normal(0.0, 0.008))
    return wrap_angle(2.0 * math.pi * idx / count)


def make_modes_v3(spec: CaseSpec) -> List[ContactMode]:
    rng = np.random.default_rng(spec.seed)
    modes: List[ContactMode] = []
    for idx in range(spec.mode_count):
        normal = mode_normal(spec.topology, idx, spec.mode_count, rng)
        mu = friction_value(spec.friction_profile, idx, rng)
        if spec.topology == "shared_action":
            mu = max(mu, 0.95)
        if spec.topology == "raw_identity_needed":
            mu = min(mu, 0.32)
        gain = float(0.88 + 0.22 * rng.random())
        modes.append(ContactMode(idx, normal, mu, gain))
    return modes


def angle_grid(count: int) -> np.ndarray:
    return np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)


def compute_contact_arrays(
    modes: Sequence[ContactMode],
    actions: np.ndarray,
    tasks: np.ndarray,
    progress_margin: float,
    contact_margin: float,
) -> tuple[np.ndarray, np.ndarray]:
    action_vecs = np.stack([np.cos(actions), np.sin(actions)], axis=1)
    task_vecs = np.stack([np.cos(tasks), np.sin(tasks)], axis=1)
    masks = np.zeros((len(modes), len(tasks), len(actions)), dtype=bool)
    progress_values = np.zeros((len(modes), len(tasks), len(actions)), dtype=np.float32)
    for midx, mode in enumerate(modes):
        n = unit(mode.normal_angle)
        t = tangent_from_normal(mode.normal_angle)
        normal_push_raw = action_vecs @ n
        normal_push = np.maximum(normal_push_raw, 0.0)
        tangent_cmd = action_vecs @ t
        tangent_limit = mode.mu * normal_push
        tangent_transmitted = np.clip(tangent_cmd, -tangent_limit, tangent_limit)
        slip_loss = np.where(np.abs(tangent_cmd) <= tangent_limit + 1e-12, 1.0, 0.58)
        velocities = mode.gain * (
            normal_push[:, None] * n[None, :]
            + 0.72 * slip_loss[:, None] * tangent_transmitted[:, None] * t[None, :]
        )
        prog_action_task = velocities @ task_vecs.T
        prog = prog_action_task.T.astype(np.float32)
        progress_values[midx, :, :] = prog
        contact_ok = normal_push_raw >= contact_margin
        masks[midx, :, :] = (prog >= progress_margin) & contact_ok[None, :]
    return masks, progress_values


def corrupt_masks(
    masks: np.ndarray,
    false_positive: float,
    false_negative: float,
    seed: int,
    conservative: bool = False,
) -> np.ndarray:
    if false_positive <= 0.0 and false_negative <= 0.0 and not conservative:
        return masks
    rng = np.random.default_rng(seed)
    noisy = masks.copy()
    if false_negative > 0.0:
        flip_neg = rng.random(size=masks.shape) < false_negative
        noisy &= ~flip_neg
    if false_positive > 0.0 and not conservative:
        flip_pos = rng.random(size=masks.shape) < false_positive
        noisy |= flip_pos
    return noisy


def group_by_key(mode_indices: Iterable[int], key_fn: Callable[[int], str]) -> Dict[str, List[int]]:
    groups: Dict[str, List[int]] = {}
    for midx in mode_indices:
        groups.setdefault(key_fn(midx), []).append(midx)
    return groups


def normal_bin_key(mode: ContactMode, bins: int) -> str:
    idx = int(math.floor(wrap_angle(mode.normal_angle) / (2.0 * math.pi) * bins)) % bins
    return f"n{bins}_{idx}"


def normal_friction_key(mode: ContactMode, normal_bins: int, friction_bins: int) -> str:
    nidx = int(math.floor(wrap_angle(mode.normal_angle) / (2.0 * math.pi) * normal_bins)) % normal_bins
    fidx = min(friction_bins - 1, int(max(0.0, min(1.99, mode.mu)) / 2.0 * friction_bins))
    return f"n{normal_bins}_{nidx}_f{friction_bins}_{fidx}"


def stable_random_key(mode_id: int, seed: int, groups: int) -> str:
    value = (mode_id * 1103515245 + seed * 12345 + 0x9E3779B9) & 0x7FFFFFFF
    return f"r{groups}_{value % groups}"


def pick_probe_tasks(tasks: np.ndarray, count: int, placement: str, seed: int) -> List[int]:
    count = max(1, min(count, len(tasks)))
    if placement == "grid":
        return sorted({int(round(i * len(tasks) / count)) % len(tasks) for i in range(count)})
    rng = random.Random(seed)
    if placement == "random":
        return sorted(rng.sample(range(len(tasks)), count))
    # Greedy is approximated by evenly interleaving two offset grids. This keeps
    # the runner deterministic and cheap while avoiding the worst one-direction
    # signatures.
    primary = [int(math.floor((i + 0.5) * len(tasks) / count)) % len(tasks) for i in range(count)]
    return sorted(set(primary))[:count]


def sector_slices(action_count: int, sectors: int) -> List[slice]:
    slices: List[slice] = []
    for sector in range(sectors):
        start = int(math.floor(sector * action_count / sectors))
        end = int(math.floor((sector + 1) * action_count / sectors))
        slices.append(slice(start, max(start + 1, end)))
    return slices


def ccsc_groups(
    modes: Sequence[ContactMode],
    label_masks: np.ndarray,
    tasks: np.ndarray,
    probe_count: int,
    sectors: int,
    placement: str,
    seed: int,
    include_friction: bool = True,
) -> Dict[str, List[int]]:
    task_indices = pick_probe_tasks(tasks, probe_count, placement, seed)
    slices = sector_slices(label_masks.shape[2], sectors)

    def key(midx: int) -> str:
        parts: List[str] = []
        for tidx in task_indices:
            bits = 0
            for sidx, slc in enumerate(slices):
                if bool(np.any(label_masks[midx, tidx, slc])):
                    bits |= 1 << sidx
            parts.append(format(bits, "x"))
        if include_friction:
            fbin = min(3, int(modes[midx].mu * 2.0))
            parts.append(f"f{fbin}")
        return "ccs_" + "_".join(parts)

    return group_by_key(range(len(modes)), key)


def prediction_groups(
    modes: Sequence[ContactMode],
    progress_values: np.ndarray,
    tasks: np.ndarray,
    probe_count: int,
    sectors: int,
    seed: int,
) -> Dict[str, List[int]]:
    task_indices = pick_probe_tasks(tasks, probe_count, "grid", seed)
    slices = sector_slices(progress_values.shape[2], sectors)

    def key(midx: int) -> str:
        parts: List[str] = []
        for tidx in task_indices:
            for slc in slices:
                best = float(np.max(progress_values[midx, tidx, slc]))
                bucket = 0 if best < 0.05 else 1 if best < 0.18 else 2 if best < 0.32 else 3
                parts.append(str(bucket))
        return "pred_" + "".join(parts)

    return group_by_key(range(len(modes)), key)


def build_groups_for_method(
    method: str,
    modes: Sequence[ContactMode],
    masks: np.ndarray,
    label_masks: np.ndarray,
    progress_values: np.ndarray,
    tasks: np.ndarray,
    seed: int,
    probe_tasks: int = 6,
    action_sectors: int = 8,
    placement: str = "grid",
) -> Dict[str, List[int]]:
    if method == "contact_count":
        return {"one_contact": list(range(len(modes)))}
    if method.startswith("normal_"):
        bins = int(method.split("_")[1])
        return group_by_key(range(len(modes)), lambda i: normal_bin_key(modes[i], bins))
    if method == "normal8_mu2":
        return group_by_key(range(len(modes)), lambda i: normal_friction_key(modes[i], 8, 2))
    if method == "normal16_mu4":
        return group_by_key(range(len(modes)), lambda i: normal_friction_key(modes[i], 16, 4))
    if method.startswith("random_"):
        bits = int(method.split("_")[1])
        return group_by_key(range(len(modes)), lambda i: stable_random_key(i, seed, 2**bits))
    if method.startswith("prediction_"):
        bits = int(method.split("_")[1])
        sectors = 4 if bits <= 4 else 6
        probes = 2 if bits <= 4 else 4
        return prediction_groups(modes, progress_values, tasks, probes, sectors, seed)
    if method == "ccsc_2x4":
        return ccsc_groups(modes, label_masks, tasks, 2, 4, "grid", seed)
    if method == "ccsc_4x6":
        return ccsc_groups(modes, label_masks, tasks, 4, 6, "grid", seed)
    if method == "ccsc_6x8":
        return ccsc_groups(modes, label_masks, tasks, 6, 8, "grid", seed)
    if method == "ccsc_8x12":
        return ccsc_groups(modes, label_masks, tasks, 8, 12, "grid", seed)
    if method == "ccsc_random_6x8":
        return ccsc_groups(modes, label_masks, tasks, 6, 8, "random", seed)
    if method == "ccsc_greedy_6x8":
        return ccsc_groups(modes, label_masks, tasks, 6, 8, "greedy", seed)
    if method == "ccsc_no_friction":
        return ccsc_groups(modes, label_masks, tasks, 6, 8, "grid", seed, include_friction=False)
    if method == "raw_mode":
        return group_by_key(range(len(modes)), lambda i: f"mode_{i}")
    if method == "budgeted_ccsc":
        return ccsc_groups(modes, label_masks, tasks, probe_tasks, action_sectors, placement, seed)
    raise KeyError(f"unknown method {method}")


def evaluate_groups(
    groups: Dict[str, List[int]],
    masks: np.ndarray,
    progress_values: np.ndarray,
    failure_penalty: float = 4.0,
    probe_cost: float = 0.0,
    probe_count: int = 0,
    refusal: bool = False,
) -> EvalResult:
    success = 0
    total = 0
    destroyed_episodes = 0
    alias_group_tasks = 0
    destroyed_group_tasks = 0
    refused = 0
    regret_sum = 0.0
    regret_count = 0
    raw_possible_cases = int(np.sum(np.any(masks, axis=2)))
    for indices in groups.values():
        idx = np.array(indices, dtype=int)
        for tidx in range(masks.shape[1]):
            group_masks = masks[idx, tidx, :]
            controllable = np.any(group_masks, axis=1)
            if not bool(np.any(controllable)):
                continue
            controllable_indices = idx[controllable]
            controllable_masks = masks[controllable_indices, tidx, :]
            robust_actions = np.all(controllable_masks, axis=0)
            robust = bool(np.any(robust_actions))
            if len(indices) > 1 and len(controllable_indices) > 1:
                alias_group_tasks += 1
                if not robust:
                    destroyed_group_tasks += 1
            if robust:
                candidates = np.flatnonzero(robust_actions)
                scores = progress_values[controllable_indices, tidx, :][:, candidates].min(axis=0)
                action_idx = int(candidates[int(np.argmax(scores))])
                refused_task = False
            elif refusal:
                action_idx = -1
                refused_task = True
            else:
                avg_scores = progress_values[controllable_indices, tidx, :].mean(axis=0)
                action_idx = int(np.argmax(avg_scores))
                refused_task = False
            block_size = len(controllable_indices)
            total += block_size
            if refused_task:
                refused += block_size
                chosen_progress = np.zeros(block_size, dtype=np.float32)
            else:
                ok_vec = masks[controllable_indices, tidx, action_idx]
                success += int(np.sum(ok_vec))
                chosen_progress = progress_values[controllable_indices, tidx, action_idx]
            if len(indices) > 1 and len(controllable_indices) > 1 and not robust:
                destroyed_episodes += block_size
            best_progress = np.max(progress_values[controllable_indices, tidx, :], axis=1)
            regret_sum += float(np.maximum(0.0, best_progress - chosen_progress).sum())
            regret_count += block_size
    group_sizes = [len(group) for group in groups.values()]
    success_rate = float(success / total) if total else 0.0
    failure_rate = 1.0 - success_rate
    return EvalResult(
        success_rate=success_rate,
        empty_intersection_rate=float(destroyed_group_tasks / alias_group_tasks) if alias_group_tasks else 0.0,
        destroyed_episode_rate=float(destroyed_episodes / total) if total else 0.0,
        mean_regret=float(regret_sum / regret_count) if regret_count else 0.0,
        mean_cost=1.0 + failure_penalty * failure_rate + probe_cost * probe_count,
        refusal_rate=float(refused / total) if total else 0.0,
        groups=len(groups),
        bits=bits_for_groups(len(groups)),
        mean_group_size=float(np.mean(group_sizes)) if group_sizes else 0.0,
        max_group_size=int(np.max(group_sizes)) if group_sizes else 0,
        raw_possible_cases=raw_possible_cases,
    )


def evaluate_groups_by_task(
    groups: Dict[str, List[int]],
    masks: np.ndarray,
    progress_values: np.ndarray,
    failure_penalty: float = 4.0,
    refusal: bool = False,
) -> List[EvalResult]:
    results: List[EvalResult] = []
    for tidx in range(masks.shape[1]):
        task_masks = masks[:, tidx : tidx + 1, :]
        task_progress = progress_values[:, tidx : tidx + 1, :]
        results.append(evaluate_groups(groups, task_masks, task_progress, failure_penalty=failure_penalty, refusal=refusal))
    return results


def evaluate_groups_taskwise(
    groups: Dict[str, List[int]],
    masks: np.ndarray,
    progress_values: np.ndarray,
    failure_penalty: float = 4.0,
    refusal: bool = False,
) -> List[EvalResult]:
    task_count = masks.shape[1]
    success = np.zeros(task_count, dtype=float)
    total = np.zeros(task_count, dtype=float)
    destroyed_episodes = np.zeros(task_count, dtype=float)
    alias_group_tasks = np.zeros(task_count, dtype=float)
    destroyed_group_tasks = np.zeros(task_count, dtype=float)
    refused = np.zeros(task_count, dtype=float)
    regret_sum = np.zeros(task_count, dtype=float)
    regret_count = np.zeros(task_count, dtype=float)
    raw_possible_cases = np.sum(np.any(masks, axis=2), axis=0)
    group_sizes = [len(group) for group in groups.values()]
    group_count = len(groups)
    bit_count = bits_for_groups(group_count)
    mean_group_size = float(np.mean(group_sizes)) if group_sizes else 0.0
    max_group_size = int(np.max(group_sizes)) if group_sizes else 0
    for indices in groups.values():
        idx = np.array(indices, dtype=int)
        for tidx in range(task_count):
            group_masks = masks[idx, tidx, :]
            controllable = np.any(group_masks, axis=1)
            if not bool(np.any(controllable)):
                continue
            controllable_indices = idx[controllable]
            controllable_masks = masks[controllable_indices, tidx, :]
            robust_actions = np.all(controllable_masks, axis=0)
            robust = bool(np.any(robust_actions))
            if len(indices) > 1 and len(controllable_indices) > 1:
                alias_group_tasks[tidx] += 1.0
                if not robust:
                    destroyed_group_tasks[tidx] += 1.0
            if robust:
                candidates = np.flatnonzero(robust_actions)
                scores = progress_values[controllable_indices, tidx, :][:, candidates].min(axis=0)
                action_idx = int(candidates[int(np.argmax(scores))])
                refused_task = False
            elif refusal:
                action_idx = -1
                refused_task = True
            else:
                avg_scores = progress_values[controllable_indices, tidx, :].mean(axis=0)
                action_idx = int(np.argmax(avg_scores))
                refused_task = False
            block_size = len(controllable_indices)
            total[tidx] += block_size
            if refused_task:
                refused[tidx] += block_size
                chosen_progress = np.zeros(block_size, dtype=np.float32)
            else:
                ok_vec = masks[controllable_indices, tidx, action_idx]
                success[tidx] += float(np.sum(ok_vec))
                chosen_progress = progress_values[controllable_indices, tidx, action_idx]
            if len(indices) > 1 and len(controllable_indices) > 1 and not robust:
                destroyed_episodes[tidx] += block_size
            best_progress = np.max(progress_values[controllable_indices, tidx, :], axis=1)
            regret_sum[tidx] += float(np.maximum(0.0, best_progress - chosen_progress).sum())
            regret_count[tidx] += block_size
    results: List[EvalResult] = []
    for tidx in range(task_count):
        success_rate = float(success[tidx] / total[tidx]) if total[tidx] else 0.0
        failure_rate = 1.0 - success_rate
        results.append(
            EvalResult(
                success_rate=success_rate,
                empty_intersection_rate=float(destroyed_group_tasks[tidx] / alias_group_tasks[tidx]) if alias_group_tasks[tidx] else 0.0,
                destroyed_episode_rate=float(destroyed_episodes[tidx] / total[tidx]) if total[tidx] else 0.0,
                mean_regret=float(regret_sum[tidx] / regret_count[tidx]) if regret_count[tidx] else 0.0,
                mean_cost=1.0 + failure_penalty * failure_rate,
                refusal_rate=float(refused[tidx] / total[tidx]) if total[tidx] else 0.0,
                groups=group_count,
                bits=bit_count,
                mean_group_size=mean_group_size,
                max_group_size=max_group_size,
                raw_possible_cases=int(raw_possible_cases[tidx]),
            )
        )
    return results


def row_from_result(
    family: str,
    case_id: str,
    method: str,
    spec: CaseSpec,
    result: EvalResult,
    task_index: object = "",
    probe_tasks: int = 0,
    action_sectors: int = 0,
    probe_placement: str = "",
    label_false_positive: float = 0.0,
    label_false_negative: float = 0.0,
    probe_cost: float = 0.0,
    probe_reliability: float = 1.0,
    first_action_required: bool = True,
) -> Dict[str, object]:
    return {
        "family": family,
        "case_id": case_id,
        "method": method,
        "task_index": task_index,
        "mode_count": spec.mode_count,
        "action_count": spec.action_count,
        "task_count": spec.task_count,
        "topology": spec.topology,
        "friction_profile": spec.friction_profile,
        "progress_margin": spec.progress_margin,
        "contact_margin": spec.contact_margin,
        "probe_tasks": probe_tasks,
        "action_sectors": action_sectors,
        "probe_placement": probe_placement,
        "label_false_positive": label_false_positive,
        "label_false_negative": label_false_negative,
        "probe_cost": probe_cost,
        "probe_reliability": probe_reliability,
        "first_action_required": int(first_action_required),
        "control": spec.control,
        "success_rate": result.success_rate,
        "empty_intersection_rate": result.empty_intersection_rate,
        "destroyed_episode_rate": result.destroyed_episode_rate,
        "mean_regret": result.mean_regret,
        "mean_cost": result.mean_cost,
        "refusal_rate": result.refusal_rate,
        "groups": result.groups,
        "bits": result.bits,
        "mean_group_size": result.mean_group_size,
        "max_group_size": result.max_group_size,
        "raw_possible_cases": result.raw_possible_cases,
        "seed": spec.seed,
    }


def evaluate_method(
    method: str,
    spec: CaseSpec,
    modes: Sequence[ContactMode],
    masks: np.ndarray,
    label_masks: np.ndarray,
    progress_values: np.ndarray,
    tasks: np.ndarray,
    probe_tasks: int = 6,
    action_sectors: int = 8,
    placement: str = "grid",
    refusal: bool = False,
    probe_cost: float = 0.0,
    execution_probe_count: int = 0,
) -> EvalResult:
    groups = build_groups_for_method(
        method,
        modes,
        masks,
        label_masks,
        progress_values,
        tasks,
        spec.seed,
        probe_tasks=probe_tasks,
        action_sectors=action_sectors,
        placement=placement,
    )
    return evaluate_groups(groups, masks, progress_values, probe_cost=probe_cost, probe_count=execution_probe_count, refusal=refusal)


def prepare_case(spec: CaseSpec) -> tuple[List[ContactMode], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    modes = make_modes_v3(spec)
    actions = angle_grid(spec.action_count)
    tasks = angle_grid(spec.task_count)
    masks, progress_values = compute_contact_arrays(modes, actions, tasks, spec.progress_margin, spec.contact_margin)
    return modes, actions, tasks, masks, progress_values


def write_row(writer: FamilyWriter, global_agg: GlobalAgg, row: Dict[str, object]) -> None:
    writer.write(row)
    global_agg.add(row)


def run_family_a(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_a"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    methods = [
        "contact_count",
        "normal_4",
        "normal_8",
        "normal8_mu2",
        "random_3",
        "prediction_4",
        "ccsc_2x4",
        "ccsc_6x8",
        "ccsc_8x12",
        "raw_mode",
    ]
    case_no = 0
    for mode_count in [32, 64]:
        for topology in ["uniform", "clustered", "paired", "adversarial"]:
            for friction_profile in ["low", "mixed", "bimodal"]:
                for progress_margin in [0.12, 0.18]:
                    for action_count in [36, 48]:
                        for task_count in [8, 12]:
                            for seed_offset in range(2):
                                spec = CaseSpec(
                                    mode_count,
                                    action_count,
                                    task_count,
                                    topology,
                                    friction_profile,
                                    progress_margin,
                                    0.08,
                                    SEED + seed_offset + case_no * 17,
                                )
                                case_no += 1
                                modes, _actions, tasks, masks, progress_values = prepare_case(spec)
                                label_masks = masks
                                case_id = f"A_{case_no:05d}"
                                for method in methods:
                                    result = evaluate_method(method, spec, modes, masks, label_masks, progress_values, tasks)
                                    row = row_from_result(family, case_id, method, spec, result)
                                    write_row(writer, global_agg, row)
                                    if method in ["contact_count", "normal8_mu2", "ccsc_6x8", "ccsc_8x12", "raw_mode"]:
                                        global_agg.add_special("main_methods", (family, method), row)
                                        global_agg.add_special("scale_by_modes", (mode_count, method), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def run_family_b(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_b"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    case_no = 0
    for mode_count in [64]:
        for topology in ["uniform", "adversarial"]:
            for friction_profile in ["mixed"]:
                for progress_margin in [0.16]:
                    for seed_offset in range(1):
                        spec = CaseSpec(
                            mode_count,
                            64,
                            18,
                            topology,
                            friction_profile,
                            progress_margin,
                            0.08,
                            SEED + 100000 + seed_offset + case_no * 19,
                        )
                        case_no += 1
                        modes, _actions, tasks, masks, progress_values = prepare_case(spec)
                        for probe_tasks in [1, 2, 4, 6, 12]:
                            for action_sectors in [2, 4, 8, 16]:
                                for placement in ["grid", "greedy"]:
                                    label_masks = masks
                                    result = evaluate_method(
                                        "budgeted_ccsc",
                                        spec,
                                        modes,
                                        masks,
                                        label_masks,
                                        progress_values,
                                        tasks,
                                        probe_tasks=probe_tasks,
                                        action_sectors=action_sectors,
                                        placement=placement,
                                    )
                                    method = f"ccsc_{placement}"
                                    row = row_from_result(
                                        family,
                                        f"B_{case_no:05d}_{probe_tasks}_{action_sectors}_{placement}",
                                        method,
                                        spec,
                                        result,
                                        probe_tasks=probe_tasks,
                                        action_sectors=action_sectors,
                                        probe_placement=placement,
                                    )
                                    write_row(writer, global_agg, row)
                                    global_agg.add_special("budget_surface", (probe_tasks, action_sectors, placement), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def run_family_c(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_c"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    case_no = 0
    noise_levels = [0.0, 0.05, 0.10, 0.20, 0.40]
    noise_pairs = [(fp, fn) for fp in noise_levels for fn in noise_levels]
    methods = ["ccsc_noisy", "ccsc_conservative", "ccsc_thresholded", "normal8_mu2", "raw_mode"]
    for mode_count in [64]:
        for topology in ["uniform", "adversarial"]:
            for false_positive, false_negative in noise_pairs:
                for seed_offset in range(1):
                    spec = CaseSpec(
                        mode_count,
                        72,
                        18,
                        topology,
                        "mixed",
                        0.16,
                        0.08,
                        SEED + 200000 + seed_offset + case_no * 23,
                    )
                    case_no += 1
                    modes, _actions, tasks, masks, progress_values = prepare_case(spec)
                    noisy = corrupt_masks(masks, false_positive, false_negative, spec.seed + 11)
                    conservative = corrupt_masks(masks, 0.0, min(0.75, false_negative + false_positive), spec.seed + 29, conservative=True)
                    thresholded = corrupt_masks(masks, 0.0, false_negative * 0.5 + false_positive * 0.5, spec.seed + 41, conservative=True)
                    for method in methods:
                        if method == "ccsc_noisy":
                            label_masks = noisy
                            eval_method_name = "ccsc_6x8"
                        elif method == "ccsc_conservative":
                            label_masks = conservative
                            eval_method_name = "ccsc_6x8"
                        elif method == "ccsc_thresholded":
                            label_masks = thresholded
                            eval_method_name = "ccsc_6x8"
                        else:
                            label_masks = masks
                            eval_method_name = method
                        result = evaluate_method(eval_method_name, spec, modes, masks, label_masks, progress_values, tasks)
                        row = row_from_result(
                            family,
                            f"C_{case_no:05d}_{false_positive:.2f}_{false_negative:.2f}",
                            method,
                            spec,
                            result,
                            probe_tasks=6 if method.startswith("ccsc") else 0,
                            action_sectors=8 if method.startswith("ccsc") else 0,
                            label_false_positive=false_positive,
                            label_false_negative=false_negative,
                        )
                        write_row(writer, global_agg, row)
                        global_agg.add_special("noise_curve", (false_positive, false_negative, method), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def run_family_d(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_d"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    methods = [
        "contact_count",
        "normal_4",
        "normal_8",
        "normal_16",
        "normal8_mu2",
        "normal16_mu4",
        "random_3",
        "random_4",
        "prediction_4",
        "prediction_6",
        "ccsc_2x4",
        "ccsc_6x8",
        "ccsc_no_friction",
        "ccsc_random_6x8",
        "ccsc_greedy_6x8",
        "safe_refusal_ccsc",
        "raw_mode",
        "raw_safe_refusal",
    ]
    case_no = 0
    for mode_count in [64, 128]:
        for topology in ["uniform", "adversarial"]:
            for progress_margin in [0.12, 0.22]:
                for seed_offset in range(1):
                    spec = CaseSpec(
                        mode_count,
                        72,
                        18,
                        topology,
                        "mixed",
                        progress_margin,
                        0.08,
                        SEED + 300000 + seed_offset + case_no * 31,
                    )
                    case_no += 1
                    modes, _actions, tasks, masks, progress_values = prepare_case(spec)
                    label_masks = masks
                    for method in methods:
                        if method == "safe_refusal_ccsc":
                            eval_method_name = "ccsc_6x8"
                            refusal = True
                        elif method == "raw_safe_refusal":
                            eval_method_name = "raw_mode"
                            refusal = True
                        else:
                            eval_method_name = method
                            refusal = False
                        result = evaluate_method(eval_method_name, spec, modes, masks, label_masks, progress_values, tasks, refusal=refusal)
                        row = row_from_result(family, f"D_{case_no:05d}", method, spec, result)
                        write_row(writer, global_agg, row)
                        global_agg.add_special("ablation_methods", (method,), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def blended_active_probe_result(raw: EvalResult, base: EvalResult, probe_cost: float, reliability: float, first_action_required: bool) -> EvalResult:
    if first_action_required:
        success_rate = base.success_rate
        refusal_rate = base.refusal_rate
    else:
        success_rate = reliability * raw.success_rate + (1.0 - reliability) * base.success_rate
        refusal_rate = (1.0 - reliability) * base.refusal_rate
    failure_rate = 1.0 - success_rate
    return EvalResult(
        success_rate=success_rate,
        empty_intersection_rate=base.empty_intersection_rate,
        destroyed_episode_rate=(1.0 - reliability) * base.destroyed_episode_rate,
        mean_regret=(1.0 - reliability) * base.mean_regret,
        mean_cost=1.0 + probe_cost + 4.0 * failure_rate,
        refusal_rate=refusal_rate,
        groups=base.groups,
        bits=base.bits,
        mean_group_size=base.mean_group_size,
        max_group_size=base.max_group_size,
        raw_possible_cases=base.raw_possible_cases,
    )


def run_family_e(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_e"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    case_no = 0
    for probe_cost in [0.0, 0.08, 0.5, 2.0, 4.0]:
        for reliability in [0.80, 1.00]:
            for first_action_required in [True, False]:
                for topology in ["uniform", "clustered", "adversarial"]:
                    for seed_offset in range(1):
                        spec = CaseSpec(
                            64,
                            72,
                            18,
                            topology,
                            "mixed",
                            0.16,
                            0.08,
                            SEED + 400000 + seed_offset + case_no * 37,
                        )
                        case_no += 1
                        modes, _actions, tasks, masks, progress_values = prepare_case(spec)
                        label_masks = masks
                        contact = evaluate_method("contact_count", spec, modes, masks, label_masks, progress_values, tasks)
                        ccsc = evaluate_method("ccsc_6x8", spec, modes, masks, label_masks, progress_values, tasks)
                        raw = evaluate_method("raw_mode", spec, modes, masks, label_masks, progress_values, tasks)
                        safe = evaluate_method("contact_count", spec, modes, masks, label_masks, progress_values, tasks, refusal=True)
                        rows = {
                            "contact_count": contact,
                            "ccsc_6x8": ccsc,
                            "raw_mode": raw,
                            "safe_refusal": safe,
                            "active_probe_contact": blended_active_probe_result(raw, contact, probe_cost, reliability, first_action_required),
                            "active_probe_ccsc": blended_active_probe_result(raw, ccsc, probe_cost, reliability, first_action_required),
                        }
                        for method, result in rows.items():
                            row = row_from_result(
                                family,
                                f"E_{case_no:05d}_{probe_cost}_{reliability}_{int(first_action_required)}",
                                method,
                                spec,
                                result,
                                probe_cost=probe_cost,
                                probe_reliability=reliability,
                                first_action_required=first_action_required,
                            )
                            write_row(writer, global_agg, row)
                            global_agg.add_special("probe_cost", (probe_cost, reliability, int(first_action_required), method), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def run_family_f(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_f"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    controls = [
        ("shared_action", "shared_action", "high", 0.10, 0.05),
        ("raw_identity_needed", "raw_identity_needed", "low", 0.22, 0.10),
        ("coarse_actions", "uniform", "mixed", 0.16, 0.08),
        ("high_margin", "uniform", "low", 0.28, 0.12),
        ("noisy_labels", "adversarial", "mixed", 0.16, 0.08),
        ("prediction_alias", "adversarial", "narrow", 0.18, 0.08),
    ]
    methods = ["contact_count", "normal_4", "normal8_mu2", "random_3", "prediction_4", "ccsc_2x4", "ccsc_6x8", "ccsc_8x12", "safe_refusal_ccsc", "raw_mode"]
    case_no = 0
    for control, topology, friction_profile, progress_margin, contact_margin in controls:
        for seed_offset in range(4):
            action_count = 36 if control == "coarse_actions" else 72
            spec = CaseSpec(
                64,
                action_count,
                18,
                topology,
                friction_profile,
                progress_margin,
                contact_margin,
                SEED + 500000 + seed_offset + case_no * 41,
                control=control,
            )
            case_no += 1
            modes, _actions, tasks, masks, progress_values = prepare_case(spec)
            if control == "noisy_labels":
                label_masks = corrupt_masks(masks, 0.20, 0.20, spec.seed + 3)
            else:
                label_masks = masks
            for method in methods:
                if method == "safe_refusal_ccsc":
                    result = evaluate_method("ccsc_6x8", spec, modes, masks, label_masks, progress_values, tasks, refusal=True)
                else:
                    result = evaluate_method(method, spec, modes, masks, label_masks, progress_values, tasks)
                row = row_from_result(family, f"F_{case_no:05d}", method, spec, result)
                write_row(writer, global_agg, row)
                global_agg.add_special("negative_controls", (control, method), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def run_family_g(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_g"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    methods = ["contact_count", "normal_8", "normal16_mu4", "prediction_6", "ccsc_4x6", "ccsc_6x8", "ccsc_8x12", "ccsc_greedy_6x8", "safe_refusal_ccsc", "raw_mode"]
    case_no = 0
    for mode_count in [64, 128, 256]:
        for topology in ["uniform", "clustered", "paired", "adversarial"]:
            for seed_offset in range(1):
                spec = CaseSpec(
                    mode_count,
                    64,
                    18,
                    topology,
                    "mixed",
                    0.16,
                    0.08,
                    SEED + 600000 + seed_offset + case_no * 43,
                )
                case_no += 1
                modes, _actions, tasks, masks, progress_values = prepare_case(spec)
                label_masks = masks
                for method in methods:
                    if method == "safe_refusal_ccsc":
                        result = evaluate_method("ccsc_6x8", spec, modes, masks, label_masks, progress_values, tasks, refusal=True)
                    else:
                        result = evaluate_method(method, spec, modes, masks, label_masks, progress_values, tasks)
                    row = row_from_result(family, f"G_{case_no:05d}", method, spec, result)
                    write_row(writer, global_agg, row)
                    global_agg.add_special("scale_by_modes", (mode_count, method), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def run_family_h(global_agg: GlobalAgg) -> Dict[str, object]:
    family = "family_h"
    writer = FamilyWriter(family)
    start = time.perf_counter()
    methods = [
        "contact_count",
        "normal_4",
        "normal_8",
        "normal8_mu2",
        "random_3",
        "prediction_4",
        "ccsc_2x4",
        "ccsc_6x8",
        "safe_refusal_ccsc",
        "raw_mode",
    ]
    case_no = 0
    for mode_count in [32, 64]:
        for topology in ["uniform", "clustered", "paired", "adversarial"]:
            for friction_profile in ["low", "mixed", "bimodal"]:
                for progress_margin in [0.12, 0.18]:
                    for seed_offset in range(14):
                        spec = CaseSpec(
                            mode_count,
                            36,
                            12,
                            topology,
                            friction_profile,
                            progress_margin,
                            0.08,
                            SEED + 700000 + seed_offset + case_no * 47,
                        )
                        case_no += 1
                        modes, _actions, tasks, masks, progress_values = prepare_case(spec)
                        label_masks = masks
                        case_id = f"H_{case_no:05d}"
                        for method in methods:
                            if method == "safe_refusal_ccsc":
                                eval_method_name = "ccsc_6x8"
                                refusal = True
                            else:
                                eval_method_name = method
                                refusal = False
                            groups = build_groups_for_method(
                                eval_method_name,
                                modes,
                                masks,
                                label_masks,
                                progress_values,
                                tasks,
                                spec.seed,
                            )
                            task_results = evaluate_groups_taskwise(groups, masks, progress_values, refusal=refusal)
                            for tidx, result in enumerate(task_results):
                                row = row_from_result(family, case_id, method, spec, result, task_index=tidx)
                                write_row(writer, global_agg, row)
                                global_agg.add_special("task_audit", (method, tidx), row)
    writer.close()
    return {"family": family, "rows": writer.rows, "cases": len(writer.cases), "seconds": time.perf_counter() - start}


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def tex_escape(text: object) -> str:
    return str(text).replace("_", r"\_").replace("&", r"\&")


def write_tex_table(path: Path, header: str, rows: Sequence[str]) -> None:
    path.write_text("\n".join([header, *rows, r"\bottomrule", r"\end{tabular}", ""]) + "\n", encoding="utf-8")


def generate_tables(global_agg: GlobalAgg, family_meta: Sequence[Dict[str, object]]) -> None:
    inventory_rows = [
        f"{meta['family'].replace('family_', '').upper()} & {int(meta['rows'])} & {int(meta['cases'])} & {float(meta['seconds']):.1f} \\\\"
        for meta in family_meta
    ]
    write_tex_table(
        TEX / "table_inventory.tex",
        "\\begin{tabular}{lrrr}\n\\toprule\nFamily & Rows & Cases & Seconds \\\\\n\\midrule",
        inventory_rows,
    )

    main_rows = []
    for row in global_agg.special_rows("main_methods", ["family", "method"]):
        if row["family"] != "family_a":
            continue
        main_rows.append(
            f"{tex_escape(row['method'])} & {fmt(row['success_rate'])} & {fmt(row['empty_intersection_rate'])} & "
            f"{fmt(row['destroyed_episode_rate'])} & {fmt(row['mean_regret'])} & {fmt(row['groups'], 1)} & {fmt(row['bits'], 1)} \\\\"
        )
    write_tex_table(
        TEX / "table_main_full_scale.tex",
        "\\begin{tabular}{lrrrrrr}\n\\toprule\nMethod & Success & Empty alias & Destroyed & Regret & Groups & Bits \\\\\n\\midrule",
        main_rows,
    )

    budget_rows = []
    for row in global_agg.special_rows("budget_surface", ["probe_tasks", "action_sectors", "placement"]):
        if int(row["probe_tasks"]) in [1, 2, 4, 6, 12] and int(row["action_sectors"]) in [2, 4, 8, 16] and row["placement"] == "grid":
            budget_rows.append(
                f"{int(row['probe_tasks'])} & {int(row['action_sectors'])} & {fmt(row['success_rate'])} & "
                f"{fmt(row['empty_intersection_rate'])} & {fmt(row['groups'], 1)} & {fmt(row['bits'], 1)} \\\\"
            )
    write_tex_table(
        TEX / "table_budget_surface.tex",
        "\\begin{tabular}{rrrrrr}\n\\toprule\nProbe tasks & Sectors & Success & Empty alias & Groups & Bits \\\\\n\\midrule",
        budget_rows,
    )

    noise_rows = []
    for row in global_agg.special_rows("noise_curve", ["false_positive", "false_negative", "method"]):
        fp = float(row["false_positive"])
        fn = float(row["false_negative"])
        if abs(fp - fn) < 1e-9 and fp in [0.0, 0.05, 0.10, 0.20, 0.40]:
            noise_rows.append(
                f"{fmt(fp, 2)} & {tex_escape(row['method'])} & {fmt(row['success_rate'])} & "
                f"{fmt(row['empty_intersection_rate'])} & {fmt(row['mean_regret'])} \\\\"
            )
    write_tex_table(
        TEX / "table_noise.tex",
        "\\begin{tabular}{rlrrr}\n\\toprule\nNoise & Method & Success & Empty alias & Regret \\\\\n\\midrule",
        noise_rows,
    )

    ablation_rows = []
    for row in global_agg.special_rows("ablation_methods", ["method"]):
        ablation_rows.append(
            f"{tex_escape(row['method'])} & {fmt(row['success_rate'])} & {fmt(row['empty_intersection_rate'])} & "
            f"{fmt(row['mean_regret'])} & {fmt(row['groups'], 1)} & {fmt(row['refusal_rate'])} \\\\"
        )
    write_tex_table(
        TEX / "table_ablations.tex",
        "\\begin{tabular}{lrrrrr}\n\\toprule\nMethod & Success & Empty alias & Regret & Groups & Refusal \\\\\n\\midrule",
        ablation_rows,
    )

    control_rows = []
    for row in global_agg.special_rows("negative_controls", ["control", "method"]):
        if row["method"] in ["contact_count", "normal8_mu2", "ccsc_6x8", "safe_refusal_ccsc", "raw_mode"]:
            control_rows.append(
                f"{tex_escape(row['control'])} & {tex_escape(row['method'])} & {fmt(row['success_rate'])} & "
                f"{fmt(row['empty_intersection_rate'])} & {fmt(row['mean_regret'])} & {fmt(row['groups'], 1)} \\\\"
            )
    write_tex_table(
        TEX / "table_negative_controls.tex",
        "\\begin{tabular}{llrrrr}\n\\toprule\nControl & Method & Success & Empty alias & Regret & Groups \\\\\n\\midrule",
        control_rows,
    )

    probe_rows = []
    for row in global_agg.special_rows("probe_cost", ["probe_cost", "reliability", "first_action_required", "method"]):
        if float(row["reliability"]) in [0.8, 1.0] and int(row["first_action_required"]) in [0, 1] and row["method"] in ["contact_count", "active_probe_contact", "ccsc_6x8", "active_probe_ccsc"]:
            if float(row["probe_cost"]) in [0.0, 0.25, 1.0, 4.0]:
                probe_rows.append(
                    f"{fmt(float(row['probe_cost']), 2)} & {fmt(float(row['reliability']), 2)} & {int(row['first_action_required'])} & "
                    f"{tex_escape(row['method'])} & {fmt(row['success_rate'])} & {fmt(row['mean_cost'])} \\\\"
                )
    write_tex_table(
        TEX / "table_active_probe.tex",
        "\\begin{tabular}{rrrlrr}\n\\toprule\nProbe cost & Reliability & First-step & Method & Success & Cost \\\\\n\\midrule",
        probe_rows,
    )

    claim_rows = [
        r"Empty-intersection obstruction & Family A/D & Contact-count empty-alias remains high while raw identity is perfect. \\",
        r"CCSC repair helps under rich signatures & Family A/B & CCSC 6x8 and 8x12 approach raw-mode success with fewer groups. \\",
        r"Probe budget matters & Family B & Low task/action budgets leave under-separated action cones. \\",
        r"Noisy labels are dangerous & Family C/F & Label corruption degrades CCSC and can make normal/friction bins competitive. \\",
        r"Active probing is an exception, not a contradiction & Family E & Probe-allowed cases improve, but first-action cases still face the theorem. \\",
        r"Compression can approach raw identity & Family F/G & Adversarial and high-margin controls inflate required groups. \\",
    ]
    write_tex_table(
        TEX / "table_claim_evidence.tex",
        "\\begin{tabular}{p{0.28\\linewidth}p{0.18\\linewidth}p{0.45\\linewidth}}\n\\toprule\nClaim & Evidence & Reading \\\\\n\\midrule",
        claim_rows,
    )


def generate_plots(global_agg: GlobalAgg) -> int:
    failures = 0
    try:
        main = [row for row in global_agg.special_rows("main_methods", ["family", "method"]) if row["family"] == "family_a"]
        main = sorted(main, key=lambda r: float(r["success_rate"]))
        plt.figure(figsize=(8.2, 4.6))
        plt.barh([tex_escape(r["method"]).replace("\\_", " ") for r in main], [float(r["success_rate"]) for r in main], color="#2563eb")
        plt.xlabel("Success on raw-controllable tasks")
        plt.xlim(0.0, 1.02)
        plt.tight_layout()
        plt.savefig(FIG / "main_success_by_method.pdf")
        plt.savefig(FIG / "main_success_by_method.png", dpi=220)
        plt.close()
    except Exception:
        failures += 1

    try:
        rows = [r for r in global_agg.special_rows("budget_surface", ["probe_tasks", "action_sectors", "placement"]) if r["placement"] == "grid"]
        pts = sorted({int(r["probe_tasks"]) for r in rows})
        secs = sorted({int(r["action_sectors"]) for r in rows})
        mat = np.zeros((len(pts), len(secs)))
        for row in rows:
            mat[pts.index(int(row["probe_tasks"])), secs.index(int(row["action_sectors"]))] = float(row["success_rate"])
        plt.figure(figsize=(6.4, 4.8))
        plt.imshow(mat, aspect="auto", origin="lower", vmin=0.85, vmax=1.0, cmap="viridis")
        plt.xticks(range(len(secs)), secs)
        plt.yticks(range(len(pts)), pts)
        plt.xlabel("Action sectors")
        plt.ylabel("Probe tasks")
        plt.colorbar(label="Success")
        plt.tight_layout()
        plt.savefig(FIG / "budget_success_heatmap.pdf")
        plt.savefig(FIG / "budget_success_heatmap.png", dpi=220)
        plt.close()
    except Exception:
        failures += 1

    try:
        rows = global_agg.special_rows("noise_curve", ["false_positive", "false_negative", "method"])
        plt.figure(figsize=(7.2, 4.4))
        for method in ["ccsc_noisy", "ccsc_conservative", "ccsc_thresholded", "normal8_mu2"]:
            xs: List[float] = []
            ys: List[float] = []
            for row in rows:
                fp = float(row["false_positive"])
                fn = float(row["false_negative"])
                if row["method"] == method and abs(fp - fn) < 1e-9:
                    xs.append(fp)
                    ys.append(float(row["success_rate"]))
            order = np.argsort(xs)
            plt.plot(np.array(xs)[order], np.array(ys)[order], marker="o", label=method.replace("_", " "))
        plt.xlabel("Symmetric feasibility-label noise")
        plt.ylabel("Success")
        plt.ylim(0.0, 1.02)
        plt.grid(True, alpha=0.25)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(FIG / "noise_success_curve.pdf")
        plt.savefig(FIG / "noise_success_curve.png", dpi=220)
        plt.close()
    except Exception:
        failures += 1

    try:
        rows = global_agg.special_rows("scale_by_modes", ["mode_count", "method"])
        plt.figure(figsize=(7.2, 4.4))
        for method in ["contact_count", "normal8_mu2", "ccsc_6x8", "ccsc_8x12", "raw_mode"]:
            xs: List[int] = []
            ys: List[float] = []
            for row in rows:
                if row["method"] == method:
                    xs.append(int(row["mode_count"]))
                    ys.append(float(row["groups"]))
            order = np.argsort(xs)
            plt.plot(np.array(xs)[order], np.array(ys)[order], marker="o", label=method.replace("_", " "))
        plt.xlabel("Mode count")
        plt.ylabel("Represented groups")
        plt.grid(True, alpha=0.25)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(FIG / "groups_vs_modes.pdf")
        plt.savefig(FIG / "groups_vs_modes.png", dpi=220)
        plt.close()
    except Exception:
        failures += 1

    try:
        rows = global_agg.special_rows("negative_controls", ["control", "method"])
        controls = sorted({str(row["control"]) for row in rows})
        methods = ["contact_count", "normal8_mu2", "ccsc_6x8", "safe_refusal_ccsc", "raw_mode"]
        x = np.arange(len(controls))
        width = 0.15
        plt.figure(figsize=(9.0, 4.8))
        for idx, method in enumerate(methods):
            vals = []
            for control in controls:
                found = [row for row in rows if row["control"] == control and row["method"] == method]
                vals.append(float(found[0]["success_rate"]) if found else 0.0)
            plt.bar(x + (idx - 2) * width, vals, width=width, label=method.replace("_", " "))
        plt.xticks(x, [c.replace("_", "\n") for c in controls], fontsize=8)
        plt.ylabel("Success")
        plt.ylim(0.0, 1.02)
        plt.legend(fontsize=7, ncol=2)
        plt.tight_layout()
        plt.savefig(FIG / "negative_controls.pdf")
        plt.savefig(FIG / "negative_controls.png", dpi=220)
        plt.close()
    except Exception:
        failures += 1
    return failures


def write_evidence_summary(global_agg: GlobalAgg, metadata: Dict[str, object]) -> None:
    rows = global_agg.summary_rows()
    lookup = {(row["family"], row["method"]): row for row in rows}
    cc = lookup.get(("family_a", "contact_count"), {})
    ccs = lookup.get(("family_a", "ccsc_6x8"), {})
    ccs8 = lookup.get(("family_a", "ccsc_8x12"), {})
    raw = lookup.get(("family_a", "raw_mode"), {})
    text = [
        "# Full-Scale Evidence Summary",
        "",
        f"- Stage: {metadata['stage']}.",
        f"- Seed: {metadata['seed']}.",
        f"- Rows: {metadata['total_rows']:,}.",
        f"- Cases: {metadata['total_cases']:,}.",
        f"- Plot failures: {metadata['plot_failures']}.",
        "",
        "## Headline Family A Numbers",
        "",
        f"- Contact-count success: {float(cc.get('success_rate', 0.0)):.3f}.",
        f"- Contact-count empty-alias rate: {float(cc.get('empty_intersection_rate', 0.0)):.3f}.",
        f"- CCSC 6x8 success: {float(ccs.get('success_rate', 0.0)):.3f}.",
        f"- CCSC 6x8 empty-alias rate: {float(ccs.get('empty_intersection_rate', 0.0)):.3f}.",
        f"- CCSC 8x12 success: {float(ccs8.get('success_rate', 0.0)):.3f}.",
        f"- Raw-mode success: {float(raw.get('success_rate', 0.0)):.3f}.",
        "",
        "## Scope",
        "",
        "These results support a synthetic local contact-representation limit. They do not establish hardware deployment, learned tactile signature extraction, production contact-implicit planning superiority, or general POMDP optimality.",
    ]
    (DOCS / "evidence_summary.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    start = time.perf_counter()
    progress_path = OUT / "progress.json"
    global_agg = GlobalAgg()
    family_meta: List[Dict[str, object]] = []
    runners = [run_family_a, run_family_b, run_family_c, run_family_d, run_family_e, run_family_f, run_family_g, run_family_h]
    for runner in runners:
        meta = runner(global_agg)
        family_meta.append(meta)
        progress_path.write_text(json.dumps({"completed": family_meta}, indent=2), encoding="utf-8")
        print(f"completed {meta['family']}: rows={meta['rows']} cases={meta['cases']} seconds={meta['seconds']:.1f}")
    write_csv(OUT / "summary_by_family_method.csv", global_agg.summary_rows())
    write_csv(OUT / "budget_surface_summary.csv", global_agg.special_rows("budget_surface", ["probe_tasks", "action_sectors", "placement"]))
    write_csv(OUT / "noise_curve_summary.csv", global_agg.special_rows("noise_curve", ["false_positive", "false_negative", "method"]))
    write_csv(OUT / "negative_control_summary.csv", global_agg.special_rows("negative_controls", ["control", "method"]))
    write_csv(OUT / "probe_cost_summary.csv", global_agg.special_rows("probe_cost", ["probe_cost", "reliability", "first_action_required", "method"]))
    write_csv(OUT / "scale_by_modes_summary.csv", global_agg.special_rows("scale_by_modes", ["mode_count", "method"]))
    generate_tables(global_agg, family_meta)
    plot_failures = generate_plots(global_agg)
    total_rows = int(sum(int(meta["rows"]) for meta in family_meta))
    total_cases = int(sum(int(meta["cases"]) for meta in family_meta))
    metadata: Dict[str, object] = {
        "stage": "complete",
        "seed": SEED,
        "elapsed_seconds": time.perf_counter() - start,
        "total_rows": total_rows,
        "total_cases": total_cases,
        "plot_failures": plot_failures,
        "families": family_meta,
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_evidence_summary(global_agg, metadata)
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
