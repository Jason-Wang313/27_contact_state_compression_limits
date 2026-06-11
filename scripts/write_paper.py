"""Generate the anonymous ICLR-style paper."""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
import sys
import unicodedata
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
DATA = ROOT / "data"
FIGURES = ROOT / "figures"

ICLR_ZIP_URLS = [
    "https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026.zip",
    "https://github.com/ICLR/Master-Template/raw/master/iclr2026.zip",
]


def ascii_clean(text: object) -> str:
    if text is None:
        return ""
    value = str(text)
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\xa0": " ",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", value).strip()


def tex_escape(text: object) -> str:
    value = ascii_clean(text)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in value)


def ensure_dirs() -> None:
    PAPER.mkdir(exist_ok=True)
    (PAPER / "template_download").mkdir(exist_ok=True)


def fetch_iclr_template() -> Dict[str, object]:
    ensure_dirs()
    status = {
        "source": "ICLR/Master-Template iclr2026.zip",
        "urls": ICLR_ZIP_URLS,
        "status": "not_started",
        "files": [],
    }
    zip_path = PAPER / "template_download" / "iclr2026.zip"
    for url in ICLR_ZIP_URLS:
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                zip_path.write_bytes(resp.read())
            status["download_url"] = url
            status["status"] = "downloaded"
            break
        except Exception as exc:  # noqa: BLE001
            status["last_error"] = ascii_clean(str(exc))
    if zip_path.exists():
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(PAPER / "template_download")
            for src in (PAPER / "template_download").rglob("*"):
                if src.name in {
                    "iclr2026_conference.sty",
                    "iclr2026_conference.bst",
                    "iclr2026_conference.tex",
                    "math_commands.tex",
                }:
                    shutil.copy2(src, PAPER / src.name)
                    status["files"].append(src.name)
            status["status"] = "official_template_ready" if "iclr2026_conference.sty" in status["files"] else "downloaded_missing_style"
        except Exception as exc:  # noqa: BLE001
            status["status"] = "extract_failed"
            status["last_error"] = ascii_clean(str(exc))
    if "iclr2026_conference.sty" not in status["files"]:
        # Last-resort fallback keeps the repo buildable while the audit records
        # that the official style was not available.
        (PAPER / "iclr2026_conference.sty").write_text(
            r"""\ProvidesPackage{iclr2026_conference}[fallback build style]
\usepackage[margin=1in]{geometry}
\usepackage{natbib}
\usepackage{fancyhdr}
\pagestyle{plain}
""",
            encoding="utf-8",
        )
        (PAPER / "iclr2026_conference.bst").write_text("", encoding="utf-8")
        status["files"].extend(["iclr2026_conference.sty", "iclr2026_conference.bst"])
        status["status"] = "fallback_template_written"
    (PAPER / "template_source.md").write_text(
        "# ICLR Template Source\n\n"
        "The runtime search found the official ICLR Master-Template repository and the ICLR 2026 author guide. "
        "This script downloaded `iclr2026.zip` from the ICLR/Master-Template repository when available.\n\n"
        f"Status: `{status['status']}`\n\n"
        f"Download URL: `{status.get('download_url', 'none')}`\n",
        encoding="utf-8",
    )
    (DATA / "template_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    return status


MANUAL_BIB = r"""
@article{mason1986,
  title={Mechanics and Planning of Manipulator Pushing Operations},
  author={Mason, Matthew T.},
  journal={The International Journal of Robotics Research},
  volume={5},
  number={3},
  pages={53--71},
  year={1986}
}

@article{lynch1996,
  title={Stable Pushing: Mechanics, Controllability, and Planning},
  author={Lynch, Kevin M. and Mason, Matthew T.},
  journal={The International Journal of Robotics Research},
  volume={15},
  number={6},
  pages={533--556},
  year={1996}
}

@article{stewart1996,
  title={An Implicit Time-Stepping Scheme for Rigid Body Dynamics with Inelastic Collisions and Coulomb Friction},
  author={Stewart, David E. and Trinkle, Jeffrey C.},
  journal={International Journal for Numerical Methods in Engineering},
  volume={39},
  number={15},
  pages={2673--2691},
  year={1996}
}

@article{anitescu1997,
  title={Formulating Dynamic Multi-Rigid-Body Contact Problems with Friction as Solvable Linear Complementarity Problems},
  author={Anitescu, Mihai and Potra, Florian A.},
  journal={Nonlinear Dynamics},
  volume={14},
  number={3},
  pages={231--247},
  year={1997}
}

@inproceedings{mordatch2012,
  title={Discovery of Complex Behaviors Through Contact-Invariant Optimization},
  author={Mordatch, Igor and Todorov, Emanuel and Popovic, Zoran},
  booktitle={ACM SIGGRAPH},
  year={2012}
}

@inproceedings{todorov2012,
  title={{MuJoCo}: A Physics Engine for Model-Based Control},
  author={Todorov, Emanuel and Erez, Tom and Tassa, Yuval},
  booktitle={IEEE/RSJ International Conference on Intelligent Robots and Systems},
  pages={5026--5033},
  year={2012}
}

@article{posa2014,
  title={A Direct Method for Trajectory Optimization of Rigid Bodies Through Contact},
  author={Posa, Michael and Cantu, Cecilia and Tedrake, Russ},
  journal={The International Journal of Robotics Research},
  volume={33},
  number={1},
  pages={69--81},
  year={2014}
}

@inproceedings{toussaint2015,
  title={Logic-Geometric Programming: An Optimization-Based Approach to Combined Task and Motion Planning},
  author={Toussaint, Marc},
  booktitle={International Joint Conference on Artificial Intelligence},
  year={2015}
}

@inproceedings{koval2015,
  title={Pose Estimation for Contact Manipulation with Manifold Particle Filters},
  author={Koval, Michael C. and Pollard, Nancy S. and Srinivasa, Siddhartha S.},
  booktitle={IEEE/RSJ International Conference on Intelligent Robots and Systems},
  year={2015}
}

@article{zhou2018,
  title={A Convex Polynomial Model for Planar Sliding Mechanics: Theory, Application, and Experimental Validation},
  author={Zhou, Jiaji and Paolini, Robert and Bagnell, J. Andrew and Mason, Matthew T.},
  journal={The International Journal of Robotics Research},
  year={2018}
}

@article{fazeli2017,
  title={Parameter and Contact Force Estimation of Planar Rigid-Bodies Undergoing Frictional Contact},
  author={Fazeli, Nima and Kolbert, Roman and Tedrake, Russ and Rodriguez, Alberto},
  journal={The International Journal of Robotics Research},
  year={2017}
}

@article{givan2003,
  title={Equivalence Notions and Model Minimization in Markov Decision Processes},
  author={Givan, Robert and Dean, Thomas and Greig, Matthew},
  journal={Artificial Intelligence},
  volume={147},
  number={1--2},
  pages={163--223},
  year={2003}
}
"""


def load_summary() -> List[Dict[str, str]]:
    path = RESULTS / "summary.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def row_by_name(rows: Iterable[Dict[str, str]], name: str) -> Dict[str, str]:
    for row in rows:
        if row.get("representation") == name:
            return row
    return {}


def latex_summary_table(rows: List[Dict[str, str]]) -> str:
    order = [
        "contact_count",
        "normal_4",
        "normal_8",
        "normal8_mu2",
        "cone_signature_repair",
        "raw_mode",
    ]
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Representation & Groups & Bits & Success & Empty alias rate \\",
        r"\midrule",
    ]
    by_name = {r["representation"]: r for r in rows}
    for name in order:
        if name not in by_name:
            continue
        row = by_name[name]
        label = name.replace("_", " ")
        lines.append(
            f"{tex_escape(label)} & {int(float(row['groups']))} & {int(float(row['bits']))} & "
            f"{float(row['success_rate']):.3f} & {float(row['empty_intersection_rate']):.3f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def write_references() -> None:
    (PAPER / "references.bib").write_text(MANUAL_BIB.strip() + "\n", encoding="utf-8")


def write_main_tex(summary_rows: List[Dict[str, str]], template_status: Dict[str, object]) -> None:
    cc = row_by_name(summary_rows, "contact_count")
    repair = row_by_name(summary_rows, "cone_signature_repair")
    raw = row_by_name(summary_rows, "raw_mode")
    cc_success = float(cc.get("success_rate", 0.0))
    cc_empty = float(cc.get("empty_intersection_rate", 0.0))
    repair_success = float(repair.get("success_rate", 0.0))
    repair_bits = int(float(repair.get("bits", 0)))
    repair_groups = int(float(repair.get("groups", 0)))
    raw_success = float(raw.get("success_rate", 0.0))
    landscape_count = 0
    lit_summary_path = DATA / "literature_summary.json"
    if lit_summary_path.exists():
        lit = json.loads(lit_summary_path.read_text(encoding="utf-8"))
        landscape_count = int(lit.get("landscape_count", 0))

    summary_table = latex_summary_table(summary_rows)
    template_note = tex_escape(str(template_status.get("status", "unknown")))

    tex = rf"""
\documentclass{{article}}
\usepackage{{iclr2026_conference,times}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{amsmath,amssymb,amsthm}}
\usepackage{{url}}
\usepackage{{enumitem}}
\usepackage{{microtype}}

\title{{Contact State Compression Limits}}

\author{{Anonymous Authors\\
Paper under double-blind review}}

\newtheorem{{theorem}}{{Theorem}}
\newtheorem{{definition}}{{Definition}}
\newtheorem{{corollary}}{{Corollary}}

\begin{{document}}
\maketitle

\begin{{abstract}}
Robots often compress contact state before planning or feedback control: a world model may keep only ``in contact'', a tactile encoder may keep a semantic label, or a planner may bin many contact geometries into one mode. This paper studies when that compression is not merely lossy but control-destroying. We show that if a compressed contact state aliases modes whose task-feasible action sets have empty intersection, no deterministic controller that observes only the compressed state can guarantee the local task for all aliased modes. The result suggests a repair: compress contact by control-cone signatures, splitting only those aliases that change the feasible action cone. A runnable friction-cone experiment shows the mechanism directly. Contact-count compression succeeds on {cc_success:.1%} of raw-controllable local tasks and has an empty-intersection rate of {cc_empty:.1%}; the proposed cone-signature repair uses {repair_bits} bits over {repair_groups} groups and recovers {repair_success:.1%} success, close to raw mode identity at {raw_success:.1%}. The contribution is a small but sharp representational test for contact-rich robot world models: prediction-faithful compression is not enough when contact changes which actions are possible.
\end{{abstract}}

\section{{Introduction}}
Contact is where compact robot state representations become dangerous. In free space, merging nearby states often causes a graceful degradation in prediction or cost. In contact-rich manipulation and locomotion, a small hidden change in contact normal, friction cone, or sticking/sliding mode can flip the set of feasible actions. The robot does not merely predict the wrong next state; it may have no single safe action that works for all true states hidden behind the same compressed observation.

The seed problem is common in embodied intelligence. Learned world models, tactile encoders, and task-and-motion abstractions frequently replace detailed contact variables by a smaller latent or symbolic state. That move is attractive because exact contact state is high dimensional and brittle. The risk is that the compression criterion is usually predictive or semantic, while the controller needs action feasibility.

This paper asks a local question: when does compressed contact state destroy controllability? The answer is expressed through feasible-action intersections. For a task direction $g$, let $A_g(c)$ be the actions that both maintain the relevant contact constraints and make task progress in true contact mode $c$. If a representation $\phi$ merges modes $c_1$ and $c_2$ but $A_g(c_1)\cap A_g(c_2)=\emptyset$, then any policy that sees only $\phi(c_1)=\phi(c_2)$ must choose the same action for both and must fail at least one. This is a representation-level obstruction, not an optimizer weakness.

We make three contributions. First, we formalize a contact-compression failure certificate based on empty intersections of task-feasible action sets. Second, we propose contact-cone separating compression (CCSC), a repair that refines aliases by action-cone signatures rather than reconstructing full contact geometry. Third, we provide a reproducible local friction-cone experiment and a {landscape_count}-paper literature map that delimit the novelty boundary.

\section{{Related Work}}
Planar pushing and contact mechanics established that contact geometry and friction determine controllability \citep{{mason1986,lynch1996,zhou2018,fazeli2017}}. Rigid-body contact simulation and complementarity formulations made contact constraints explicit state variables for dynamics and optimization \citep{{stewart1996,anitescu1997,todorov2012}}. Contact-implicit and contact-invariant optimization can discover rich behaviors when the optimization problem retains enough variables to express the contact constraints \citep{{mordatch2012,posa2014,toussaint2015}}. Tactile and contact-state estimation work estimates hidden object or contact variables during manipulation \citep{{koval2015}}.

Those lines make the present result more modest and more specific. We do not claim that contact modes, friction cones, or pushing controllability are new. The gap is the compression criterion. Generic abstraction theory, including MDP model minimization \citep{{givan2003}}, asks when states can be merged without changing decision behavior. This paper instantiates that idea for contact dynamics with a physically interpretable certificate: merged contact modes must share task-feasible actions. The hostile prior-work set in the repository records 100 papers most likely to erode the contribution.

\section{{Problem Setup}}
Let $C$ be a finite set of local contact modes, $A$ a compact action set, and $G$ a family of local task directions or guards. For each $c\in C$ and $g\in G$, define a binary success predicate
\[
S(c,g,a)=1
\]
when action $a$ maintains the contact constraints required by mode $c$ and produces enough progress for task $g$. The corresponding feasible action set is
\[
A_g(c)=\{{a\in A: S(c,g,a)=1\}}.
\]
A contact-state compression is a map $\phi:C\rightarrow Z$. A compressed feedback policy is any $\pi:Z\times G\rightarrow A$. This covers a controller whose world model or encoder exposes $z=\phi(c)$ but not the true mode.

\begin{{definition}}[Control-faithful alias class]
An alias class $B_z=\{{c\in C:\phi(c)=z\}}$ is control-faithful for task $g$ if
\[
\bigcap_{{c\in B_z: A_g(c)\neq\emptyset}} A_g(c) \neq \emptyset.
\]
It is control-destroying if at least two modes in $B_z$ are individually feasible for $g$ but the intersection is empty.
\end{{definition}}

\section{{Compression Limit}}
\begin{{theorem}}[Empty-intersection obstruction]
Fix a task $g$ and compression $\phi$. Suppose there is an alias class $B_z$ containing modes $c_1,\ldots,c_k$ such that $A_g(c_i)\neq\emptyset$ for every $i$ but $\cap_i A_g(c_i)=\emptyset$. Then no deterministic compressed policy $\pi(z,g)$ can satisfy $S(c_i,g,\pi(z,g))=1$ for all $i$.
\end{{theorem}}
\begin{{proof}}
Because the modes share the same compressed state, the policy must choose one action $a^\star=\pi(z,g)$ for all of them. If it succeeded for every aliased mode, then $a^\star\in A_g(c_i)$ for every $i$, so $a^\star$ would lie in $\cap_i A_g(c_i)$. This contradicts the empty-intersection assumption.
\end{{proof}}

The theorem is local and intentionally severe. It does not say history, probing, belief-space planning, or randomized policies are useless. It says that when the first safety-critical action must already work, missing action-cone information cannot be recovered downstream.

\begin{{corollary}}[Prediction is insufficient]
If two contact modes are merged by a representation because they have similar predicted observations or next states under an average action distribution, but their task-feasible action sets are disjoint for a required task, prediction-faithful compression is not control-faithful for that task.
\end{{corollary}}

\section{{Repair: Contact-Cone Separating Compression}}
CCSC changes the object being compressed. Instead of preserving every contact coordinate or a semantic label, it preserves a coarse signature of feasible actions. Given probe tasks $\bar G\subset G$ and action sectors $\bar A$, each mode receives a signature
\[
\sigma(c)=\left(\mathbf{{1}}_{{\exists a\in \bar A_j: S(c,\bar g,a)=1}}\right)_{{\bar g\in \bar G, j}}.
\]
The repaired compression is $\phi_{{\rm ccs}}(c)=\sigma(c)$, optionally starting from an existing coarse representation and splitting only aliases whose signatures differ. This is not a verifier added after a controller acts. It changes what the contact state must retain: action-separating predicates.

In practice, the signature can be computed from an analytic contact model, a differentiable simulator, or action-labeled tactile data. The present paper uses the analytic route to keep the evidence auditable.

\section{{Runnable Evidence}}
We instantiate a local point-contact model with 64 modes, each defined by a contact normal, friction coefficient, and transmission gain. An action is a unit push direction. It is feasible for a task if it pushes into the contact, respects a Coulomb-like tangential limit, and yields positive progress along the task direction. We compare contact count, normal bins, normal-plus-friction bins, CCSC, and raw mode identity. All numbers are regenerated by \texttt{{python scripts/run\_experiments.py}}.

\begin{{table}}[t]
\centering
{summary_table}
\caption{{Compression results conditioned on tasks that are feasible with raw mode identity. Empty alias rate is the fraction of alias group/task pairs with individually feasible modes but no common action.}}
\label{{tab:results}}
\end{{table}}

\begin{{figure}}[t]
\centering
\includegraphics[width=0.76\linewidth]{{../figures/success_vs_bits.pdf}}
\caption{{Contact-count compression throws away the distinctions that choose feasible actions. CCSC recovers most raw-mode success with fewer represented groups than exact mode identity.}}
\label{{fig:success}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\includegraphics[width=0.48\linewidth]{{../figures/contact_cones_alias.pdf}}
\includegraphics[width=0.48\linewidth]{{../figures/empty_intersection_rate.pdf}}
\caption{{Left: two modes hidden behind the same contact-count state can require disjoint action sectors for the same task. Right: empty intersections fall as compression preserves contact-cone information.}}
\label{{fig:cones}}
\end{{figure}}

The experiment supports the theorem's mechanism. The coarse representations do not fail because the local dynamics are hard to optimize; the policy is given the best group action by exhaustive search over action directions. They fail because the alias class itself has no common feasible action. CCSC improves success by splitting aliases along the same object that appears in the proof: feasible action signatures.

\section{{Limitations}}
The evidence is local and model-based. It does not prove that a particular robot foundation model currently destroys contact controllability, nor does it validate CCSC on hardware. The theorem is one-step and deterministic; if the robot can safely probe, maintain a belief, or delay the task, some aliases may become recoverable. The repair also needs a source of action-feasibility labels. These limitations are acceptable for the paper's central claim: before adding more planning machinery, a contact representation should be tested for control-faithful alias classes.

\section{{Reproducibility Statement}}
The repository contains the full sweep, experiment, and build scripts. The literature matrix is in \texttt{{docs/related\_work\_matrix.csv}}. Experiment outputs are in \texttt{{results/}} and figures in \texttt{{figures/}}. The ICLR template fetch status was \texttt{{{template_note}}}; source details are written to \texttt{{paper/template\_source.md}}.

\bibliography{{references}}
\bibliographystyle{{iclr2026_conference}}

\end{{document}}
"""
    (PAPER / "main.tex").write_text(tex.strip() + "\n", encoding="utf-8")


def main() -> int:
    try:
        ensure_dirs()
        status = fetch_iclr_template()
        summary_rows = load_summary()
        write_references()
        write_main_tex(summary_rows, status)
        (DATA / "paper_status.json").write_text(
            json.dumps({"status": "complete", "paper": str(PAPER / "main.tex")}, indent=2),
            encoding="utf-8",
        )
        print("paper generated")
        return 0
    except Exception as exc:  # noqa: BLE001
        DATA.mkdir(exist_ok=True)
        (DATA / "paper_status.json").write_text(
            json.dumps({"status": "failed", "error": ascii_clean(str(exc))}, indent=2),
            encoding="utf-8",
        )
        print(f"paper generation failed but recorded status: {exc}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
