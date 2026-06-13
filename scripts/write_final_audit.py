"""Write the required final audit from run artifacts."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"
RESULTS = ROOT / "results"

DOWNLOADS_PDF = "C:/Users/wangz/Downloads/27.pdf"
DESKTOP_PDFS = [
    "C:/Users/wangz/OneDrive/Desktop/27.pdf",
    "C:/Users/wangz/Desktop/27.pdf",
]
LOCAL_PDF = ROOT / "paper" / "main.pdf"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def row_by_key(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    for row in rows:
        if row.get(key) == value:
            return row
    return {}


def remote_url() -> str:
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return ""


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    lit = load_json(DATA / "literature_summary.json")
    build = load_json(DATA / "build_status.json")
    template = load_json(DATA / "template_status.json")
    publish = load_json(DATA / "git_push_status.json")
    summary = load_json(RESULTS / "summary.json")
    stress = load_csv(RESULTS / "signature_budget_stress.csv")
    github_url = publish.get("github_url") or remote_url() or "push not completed"
    downloads_path = Path(DOWNLOADS_PDF)
    downloads_status = "missing"
    if downloads_path.exists():
        downloads_status = f"exists, size={downloads_path.stat().st_size} bytes"
    existing_desktops = [path for path in DESKTOP_PDFS if Path(path).exists()]
    if existing_desktops:
        desktop_status = "unexpected file(s) present: " + ", ".join(existing_desktops)
    else:
        desktop_status = "absent at checked Desktop paths (expected; canonical PDF is Downloads only)"
    local_pdf_status = "absent (expected after Downloads copy)"
    if LOCAL_PDF.exists():
        local_pdf_status = f"unexpected local file exists at {LOCAL_PDF}"

    repair_success = "unknown"
    count_success = "unknown"
    raw_success = "unknown"
    if isinstance(summary, list):
        by_name = {row.get("representation"): row for row in summary}
        if "cone_signature_repair" in by_name:
            repair_success = f"{float(by_name['cone_signature_repair'].get('success_rate', 0.0)):.3f}"
        if "contact_count" in by_name:
            count_success = f"{float(by_name['contact_count'].get('success_rate', 0.0)):.3f}"
        if "raw_mode" in by_name:
            raw_success = f"{float(by_name['raw_mode'].get('success_rate', 0.0)):.3f}"

    low_budget = row_by_key(stress, "budget", "one_task_two_sectors")
    full_budget = row_by_key(stress, "budget", "v1_six_tasks_eight_sectors")
    low_success = "unknown"
    low_empty = "unknown"
    low_regret = "unknown"
    full_empty = "unknown"
    if low_budget:
        low_success = f"{float(low_budget.get('success_rate', 0.0)):.3f}"
        low_empty = f"{float(low_budget.get('empty_intersection_rate', 0.0)):.3f}"
        low_regret = f"{float(low_budget.get('mean_regret', 0.0)):.3f}"
    if full_budget:
        full_empty = f"{float(full_budget.get('empty_intersection_rate', 0.0)):.3f}"

    lines = [
        "# Final Audit",
        "",
        "1. Chosen thesis: Compressed contact state can destroy controllability when it aliases contact modes whose task-feasible action sets have empty intersection; repairing the representation requires retaining control-cone signatures, not merely better prediction.",
        "",
        "2. Field assumption broken: The run challenges the assumption that compact contact labels, contact counts, or prediction-trained latents preserve the action distinctions a robot controller needs.",
        "",
        "3. New central mechanism: Control-cone separating compression. Alias classes are evaluated by the robust intersection of feasible action sets, and the repair splits only aliases with different action-cone signatures.",
        "",
        "4. Genuine novelty: The paper is not a new planner, verifier, uncertainty wrapper, or benchmark. Its novelty is a contact-specific representation criterion and impossibility certificate tied to feasible-action intersections.",
        "",
        "5. Closest hostile prior work: Planar pushing controllability, complementarity/contact-implicit optimization, tactile contact-state estimation, and MDP/bisimulation abstraction. The hostile set is documented in `docs/hostile_prior_work.md`.",
        "",
        f"6. Literature coverage: landscape={lit.get('landscape_count', 'unknown')}, serious_skim={lit.get('serious_skim_count', 'unknown')}, deep_read={lit.get('deep_read_count', 'unknown')}, hostile={lit.get('hostile_count', 'unknown')}. Matrix: `docs/related_work_matrix.csv`.",
        "",
        "7. Proof/formal-claim status: The empty-intersection obstruction is formally proved as a one-step/local theorem. The broader claim that real learned robot world models suffer this failure is not proved.",
        "",
        f"8. Strongest evidence: Runnable friction-cone experiment. Contact-count success={count_success}, cone-signature repair success={repair_success}, raw-mode success={raw_success}. V2 signature-budget stress: one probe task/two action sectors gives success={low_success}, empty-alias={low_empty}, mean regret={low_regret}; the six-probe/eight-sector CCSC setting has empty-alias={full_empty}. Figures and CSVs are in `figures/` and `results/`.",
        "",
        "9. Biggest weaknesses: Local toy contact model, no hardware validation, deterministic one-step theorem, repair assumes access to action-feasibility labels or a contact model, and signatures depend on task/action discretization.",
        "",
        "10. Paper-readiness judgment: workshop-only / strong-revise. The mechanism is sharp and runnable, but an ICLR main-track submission would need stronger real-robot or high-fidelity simulation evidence.",
        "",
        f"11. Exact Downloads PDF path: `{DOWNLOADS_PDF}` ({downloads_status}). Build status: `{build.get('status', 'unknown')}`; copied flag: `{build.get('copied', False)}`.",
        "",
        f"12. GitHub URL: `{github_url}`. Publish status: `{publish.get('status', 'unknown')}`.",
        "",
        f"13. Visible Desktop PDF copy: {desktop_status}.",
        "",
        f"14. Local repo PDF copy: {local_pdf_status}.",
        "",
        "Additional audit notes:",
        f"- ICLR template status: `{template.get('status', 'unknown')}`.",
        f"- Git publish details: {publish.get('message', publish.get('error', 'none recorded'))}.",
    ]
    (DOCS / "final_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("final audit written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
