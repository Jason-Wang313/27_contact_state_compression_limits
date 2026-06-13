"""Run contact-state compression experiments and generate figures."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Sequence

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contact_compression import (  # noqa: E402
    ContactMode,
    action_grid,
    bits_for_groups,
    build_groups,
    choose_group_action,
    cone_signature_key,
    feasible,
    feasible_mask,
    make_modes,
    progress,
    representation_builders,
    task_grid,
    unit,
)


RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"
DATA = ROOT / "data"


def ensure_dirs() -> None:
    for path in [RESULTS, FIGURES, DOCS, DATA]:
        path.mkdir(exist_ok=True)


def evaluate_representation(
    name: str,
    groups: Dict[str, List[ContactMode]],
    modes: Sequence[ContactMode],
    actions: Sequence[float],
    tasks: Sequence[float],
) -> Dict[str, object]:
    mode_to_group = {}
    for key, group_modes in groups.items():
        for mode in group_modes:
            mode_to_group[mode.mode_id] = key

    group_task_cache = {}
    destroyed_group_tasks = 0
    alias_group_tasks = 0
    policy_rows = []
    for group_key, group_modes in groups.items():
        for tidx, task in enumerate(tasks):
            action_idx, robust, controllable_count, group_size = choose_group_action(group_modes, task, actions)
            group_task_cache[(group_key, tidx)] = (action_idx, robust, controllable_count, group_size)
            if group_size > 1 and controllable_count > 1:
                alias_group_tasks += 1
                if not robust:
                    destroyed_group_tasks += 1
            policy_rows.append(
                {
                    "representation": name,
                    "group": group_key,
                    "task_index": tidx,
                    "task_angle": task,
                    "action_index": action_idx,
                    "action_angle": actions[action_idx],
                    "robust_common_action": robust,
                    "controllable_modes_in_group": controllable_count,
                    "group_size": group_size,
                }
            )

    success = 0
    total = 0
    raw_success_possible = 0
    destroyed_episodes = 0
    regret_values = []
    episode_rows = []
    for mode in modes:
        for tidx, task in enumerate(tasks):
            raw_mask = feasible_mask(mode, task, actions)
            raw_possible = bool(np.any(raw_mask))
            if not raw_possible:
                continue
            raw_success_possible += 1
            group_key = mode_to_group[mode.mode_id]
            action_idx, robust, controllable_count, group_size = group_task_cache[(group_key, tidx)]
            ok = feasible(mode, task, actions[action_idx])
            if ok:
                success += 1
            total += 1
            if group_size > 1 and controllable_count > 1 and not robust:
                destroyed_episodes += 1
            best_progress = max(progress(mode, task, a) for a in actions)
            chosen_progress = progress(mode, task, actions[action_idx])
            regret_values.append(max(0.0, best_progress - chosen_progress))
            episode_rows.append(
                {
                    "representation": name,
                    "mode_id": mode.mode_id,
                    "normal_angle": mode.normal_angle,
                    "mu": mode.mu,
                    "task_index": tidx,
                    "task_angle": task,
                    "group": group_key,
                    "action_index": action_idx,
                    "action_angle": actions[action_idx],
                    "raw_possible": raw_possible,
                    "robust_common_action": robust,
                    "success": ok,
                    "best_progress": best_progress,
                    "chosen_progress": chosen_progress,
                    "regret": max(0.0, best_progress - chosen_progress),
                }
            )

    group_sizes = [len(v) for v in groups.values()]
    return {
        "name": name,
        "groups": len(groups),
        "bits": bits_for_groups(len(groups)),
        "mean_group_size": float(np.mean(group_sizes)),
        "max_group_size": int(np.max(group_sizes)),
        "success_rate": float(success / total) if total else 0.0,
        "raw_possible_cases": raw_success_possible,
        "destroyed_episode_rate": float(destroyed_episodes / total) if total else 0.0,
        "empty_intersection_rate": float(destroyed_group_tasks / alias_group_tasks) if alias_group_tasks else 0.0,
        "mean_regret": float(np.mean(regret_values)) if regret_values else 0.0,
        "episode_rows": episode_rows,
        "policy_rows": policy_rows,
    }


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_success(summary_rows: List[Dict[str, object]]) -> None:
    ordered = sorted(summary_rows, key=lambda r: (int(r["bits"]), str(r["representation"])))
    colors = ["#334155", "#0f766e", "#b45309", "#7c2d12", "#1d4ed8", "#be123c", "#15803d", "#581c87"]
    plt.figure(figsize=(7.2, 4.3))
    for idx, row in enumerate(ordered):
        marker = "D" if row["representation"] == "cone_signature_repair" else "o"
        plt.scatter(int(row["bits"]), float(row["success_rate"]), s=85, marker=marker, color=colors[idx % len(colors)])
        plt.text(
            int(row["bits"]) + 0.04,
            float(row["success_rate"]) + 0.005,
            str(row["representation"]).replace("_", " "),
            fontsize=8,
        )
    plt.xlabel("Compressed contact-state bits")
    plt.ylabel("Success on raw-controllable local tasks")
    plt.ylim(0.0, 1.05)
    plt.grid(True, alpha=0.28)
    plt.tight_layout()
    plt.savefig(FIGURES / "success_vs_bits.pdf")
    plt.savefig(FIGURES / "success_vs_bits.png", dpi=220)
    plt.close()


def plot_empty_intersections(summary_rows: List[Dict[str, object]]) -> None:
    names = [str(r["representation"]).replace("_", "\n") for r in summary_rows]
    vals = [float(r["empty_intersection_rate"]) for r in summary_rows]
    plt.figure(figsize=(8.0, 4.2))
    bars = plt.bar(range(len(vals)), vals, color=["#475569", "#0f766e", "#b45309", "#1d4ed8", "#be123c", "#15803d", "#581c87", "#334155"])
    for bar, val in zip(bars, vals):
        plt.text(bar.get_x() + bar.get_width() / 2.0, val + 0.015, f"{val:.2f}", ha="center", va="bottom", fontsize=8)
    plt.xticks(range(len(vals)), names, fontsize=8)
    plt.ylabel("Alias group/task empty-intersection rate")
    plt.ylim(0.0, min(1.0, max(vals) + 0.18))
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "empty_intersection_rate.pdf")
    plt.savefig(FIGURES / "empty_intersection_rate.png", dpi=220)
    plt.close()


def plot_aliasing_heatmap(policy_rows: List[Dict[str, object]], tasks: Sequence[float]) -> None:
    reps = []
    for row in policy_rows:
        rep = str(row["representation"])
        if rep not in reps:
            reps.append(rep)
    matrix = np.zeros((len(reps), len(tasks)), dtype=float)
    counts = np.zeros_like(matrix)
    for row in policy_rows:
        ridx = reps.index(str(row["representation"]))
        tidx = int(row["task_index"])
        if int(row["group_size"]) > 1 and int(row["controllable_modes_in_group"]) > 1:
            counts[ridx, tidx] += 1.0
            if str(row["robust_common_action"]) == "False" or row["robust_common_action"] is False:
                matrix[ridx, tidx] += 1.0
    matrix = np.divide(matrix, np.maximum(counts, 1.0))
    plt.figure(figsize=(8.0, 3.8))
    plt.imshow(matrix, aspect="auto", cmap="magma", vmin=0.0, vmax=1.0)
    plt.colorbar(label="Fraction of alias groups with no common action")
    plt.yticks(range(len(reps)), [r.replace("_", " ") for r in reps], fontsize=8)
    plt.xticks(range(0, len(tasks), 3), [str(i) for i in range(0, len(tasks), 3)], fontsize=8)
    plt.xlabel("Task direction index")
    plt.tight_layout()
    plt.savefig(FIGURES / "aliasing_heatmap.pdf")
    plt.savefig(FIGURES / "aliasing_heatmap.png", dpi=220)
    plt.close()


def plot_contact_cones(modes: Sequence[ContactMode], actions: Sequence[float], tasks: Sequence[float]) -> None:
    task = tasks[0]
    # Pick two modes whose normals are far apart but each can solve the task.
    candidates = []
    for m1 in modes:
        if not np.any(feasible_mask(m1, task, actions)):
            continue
        for m2 in modes:
            if m1.mode_id >= m2.mode_id:
                continue
            if not np.any(feasible_mask(m2, task, actions)):
                continue
            mask1 = feasible_mask(m1, task, actions)
            mask2 = feasible_mask(m2, task, actions)
            if not np.any(mask1 & mask2):
                sep = abs(math.atan2(math.sin(m1.normal_angle - m2.normal_angle), math.cos(m1.normal_angle - m2.normal_angle)))
                candidates.append((sep, m1, m2, mask1, mask2))
    if not candidates:
        return
    _, m1, m2, mask1, mask2 = sorted(candidates, key=lambda x: x[0], reverse=True)[0]
    fig = plt.figure(figsize=(5.2, 5.0))
    ax = plt.subplot(111, projection="polar")
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)
    radii1 = np.where(mask1, 1.0, np.nan)
    radii2 = np.where(mask2, 0.78, np.nan)
    ax.scatter(actions, radii1, s=12, color="#0f766e", label=f"mode {m1.mode_id} feasible actions")
    ax.scatter(actions, radii2, s=12, color="#be123c", label=f"mode {m2.mode_id} feasible actions")
    ax.arrow(task, 0.0, 0.0, 1.1, width=0.015, color="#1d4ed8", alpha=0.85, length_includes_head=True)
    ax.arrow(m1.normal_angle, 0.0, 0.0, 0.55, width=0.012, color="#0f766e", alpha=0.65, length_includes_head=True)
    ax.arrow(m2.normal_angle, 0.0, 0.0, 0.48, width=0.012, color="#be123c", alpha=0.65, length_includes_head=True)
    ax.set_yticklabels([])
    ax.set_title("Aliased contact modes can require disjoint actions", fontsize=10)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "contact_cones_alias.pdf", bbox_inches="tight")
    plt.savefig(FIGURES / "contact_cones_alias.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_report(summary_rows: List[Dict[str, object]], stress_rows: List[Dict[str, object]]) -> None:
    lines = [
        "# Experiment Report",
        "",
        "## Setup",
        "- 64 local frictional contact modes with different contact normals and friction coefficients.",
        "- 180 action directions and 24 task-progress directions.",
        "- Evaluation is conditioned on raw-mode controllability, so failures are due to compression rather than impossible tasks.",
        "- A compressed controller chooses one action for every mode in an alias class; success requires that action to satisfy the true mode's contact and task cone.",
        "",
        "## Summary",
        "| Representation | Groups | Bits | Success | Empty-intersection rate | Destroyed episode rate | Mean regret |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['representation']} | {row['groups']} | {row['bits']} | {float(row['success_rate']):.3f} | "
            f"{float(row['empty_intersection_rate']):.3f} | {float(row['destroyed_episode_rate']):.3f} | {float(row['mean_regret']):.3f} |"
        )
    lines += [
        "",
        "## V2 Signature-Budget Stress",
        "",
        "The submission-hardening stress test reruns the CCSC repair with fewer probe tasks and coarser action sectors. It shows that CCSC is conditional on a sufficiently rich action/task signature, not a free compression guarantee.",
        "",
        "| Signature budget | Probe tasks | Action sectors | Groups | Bits | Success | Empty-intersection rate | Mean regret |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in stress_rows:
        lines.append(
            f"| {row['budget']} | {row['probe_tasks']} | {row['action_sectors']} | {row['groups']} | {row['bits']} | "
            f"{float(row['success_rate']):.3f} | {float(row['empty_intersection_rate']):.3f} | {float(row['mean_regret']):.3f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "Contact-count compression merges all local modes and frequently leaves no action that is feasible for every possible true contact. Coarser normal bins reduce but do not remove the problem. The cone-signature repair splits modes only when their feasible-action signatures differ, which recovers most raw-mode success without using exact mode identity. The v2 stress test also exposes the repair's own boundary: a low-budget signature under-separates control cones and leaves many empty aliases.",
        "",
        "## Generated Artifacts",
        "- `results/summary.json`",
        "- `results/summary.csv`",
        "- `results/episode_results.csv`",
        "- `results/policy_results.csv`",
        "- `results/signature_budget_stress.csv`",
        "- `results/signature_budget_stress_table.tex`",
        "- `figures/success_vs_bits.pdf`",
        "- `figures/empty_intersection_rate.pdf`",
        "- `figures/aliasing_heatmap.pdf`",
        "- `figures/contact_cones_alias.pdf`",
    ]
    (DOCS / "experiment_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_signature_budget_stress(
    modes: Sequence[ContactMode],
    actions: Sequence[float],
    tasks: Sequence[float],
    summary_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    budgets = [
        ("one_task_two_sectors", 24, 2),
        ("one_task_four_sectors", 24, 4),
        ("two_tasks_two_sectors", 12, 2),
        ("two_tasks_four_sectors", 12, 4),
    ]
    rows: List[Dict[str, object]] = []
    for label, task_stride, action_sectors in budgets:
        probe_tasks = list(tasks[::task_stride])
        groups = build_groups(
            modes,
            lambda mode, probe_tasks=probe_tasks, action_sectors=action_sectors: cone_signature_key(
                mode,
                probe_tasks,
                actions,
                action_sectors=action_sectors,
            ),
        )
        result = evaluate_representation(label, groups, modes, actions, tasks)
        rows.append(
            {
                "budget": label,
                "probe_tasks": len(probe_tasks),
                "action_sectors": action_sectors,
                "groups": result["groups"],
                "bits": result["bits"],
                "success_rate": result["success_rate"],
                "empty_intersection_rate": result["empty_intersection_rate"],
                "destroyed_episode_rate": result["destroyed_episode_rate"],
                "mean_regret": result["mean_regret"],
            }
        )
    repair = next((row for row in summary_rows if row["representation"] == "cone_signature_repair"), None)
    if repair is not None:
        rows.append(
            {
                "budget": "v1_six_tasks_eight_sectors",
                "probe_tasks": 6,
                "action_sectors": 8,
                "groups": repair["groups"],
                "bits": repair["bits"],
                "success_rate": repair["success_rate"],
                "empty_intersection_rate": repair["empty_intersection_rate"],
                "destroyed_episode_rate": repair["destroyed_episode_rate"],
                "mean_regret": repair["mean_regret"],
            }
        )
    write_csv(RESULTS / "signature_budget_stress.csv", rows)
    lines = [
        "\\begin{tabular}{lrrrrr}",
        "\\toprule",
        "Signature budget & Groups & Bits & Success & Empty alias & Regret \\\\",
        "\\midrule",
    ]
    for row in rows:
        label = str(row["budget"]).replace("_", " ")
        lines.append(
            f"{tex_label(label)} & {int(row['groups'])} & {int(row['bits'])} & "
            f"{float(row['success_rate']):.3f} & {float(row['empty_intersection_rate']):.3f} & "
            f"{float(row['mean_regret']):.3f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (RESULTS / "signature_budget_stress_table.tex").write_text("\n".join(lines), encoding="utf-8")
    return rows


def tex_label(label: str) -> str:
    return label.replace("&", r"\&").replace("_", r"\_")


def main() -> int:
    ensure_dirs()
    status_path = DATA / "experiment_status.json"
    try:
        modes = make_modes(count=64, seed=27)
        actions = action_grid(180)
        tasks = task_grid(24)
        summaries = []
        all_episodes = []
        all_policies = []
        for name, groups in representation_builders(modes, actions, tasks):
            result = evaluate_representation(name, groups, modes, actions, tasks)
            row = {
                "representation": result["name"],
                "groups": result["groups"],
                "bits": result["bits"],
                "mean_group_size": result["mean_group_size"],
                "max_group_size": result["max_group_size"],
                "success_rate": result["success_rate"],
                "raw_possible_cases": result["raw_possible_cases"],
                "destroyed_episode_rate": result["destroyed_episode_rate"],
                "empty_intersection_rate": result["empty_intersection_rate"],
                "mean_regret": result["mean_regret"],
            }
            summaries.append(row)
            all_episodes.extend(result["episode_rows"])
            all_policies.extend(result["policy_rows"])
            print(f"evaluated {name}: success={float(result['success_rate']):.3f} bits={result['bits']}")
        write_csv(RESULTS / "summary.csv", summaries)
        write_csv(RESULTS / "episode_results.csv", all_episodes)
        write_csv(RESULTS / "policy_results.csv", all_policies)
        (RESULTS / "summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
        plot_success(summaries)
        plot_empty_intersections(summaries)
        plot_aliasing_heatmap(all_policies, tasks)
        plot_contact_cones(modes, actions, tasks)
        stress_rows = run_signature_budget_stress(modes, actions, tasks, summaries)
        write_report(summaries, stress_rows)
        status_path.write_text(
            json.dumps(
                {
                    "status": "complete",
                    "summary_rows": len(summaries),
                    "signature_budget_stress_rows": len(stress_rows),
                    "episode_rows": len(all_episodes),
                    "policy_rows": len(all_policies),
                    "figures": sorted(p.name for p in FIGURES.glob("*")),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        status_path.write_text(json.dumps({"status": "failed", "error": str(exc)}, indent=2), encoding="utf-8")
        print(f"experiments failed but recorded status: {exc}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
