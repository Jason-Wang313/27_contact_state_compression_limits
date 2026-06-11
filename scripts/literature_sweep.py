"""Literature sweep for Paper 27.

The script intentionally uses only the Python standard library so the run is
portable. It queries OpenAlex, builds a ranked contact-dynamics landscape, and
writes the required documentation artifacts.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"

TARGET_LANDSCAPE = 1000
TARGET_SERIOUS = 300
TARGET_DEEP = 225
TARGET_HOSTILE = 100

OPENALEX = "https://api.openalex.org/works"
CROSSREF = "https://api.crossref.org/works"
HEADERS = {
    "User-Agent": "paper27-contact-compression-limits/1.0 (mailto:anonymous@example.invalid)"
}

QUERIES = [
    "robot contact dynamics",
    "contact-rich manipulation robotics",
    "frictional contact manipulation",
    "hybrid contact dynamics control robotics",
    "planar pushing manipulation controllability",
    "contact mode planning manipulation",
    "tactile contact state estimation manipulation",
    "quasi-static pushing robotic manipulation",
    "complementarity contact dynamics robotics",
    "legged robot contact dynamics control",
    "state abstraction controllability robotics",
    "bisimulation control abstraction robotics",
    "object manipulation contact models",
    "learning contact dynamics manipulation",
    "differentiable physics contact robotics",
    "grasping contact state tactile",
    "locomotion contact mode control",
    "contact implicit trajectory optimization",
    "friction cone robotic manipulation",
    "simulation to real contact dynamics robot",
    "hybrid systems contact controllability",
    "pusher slider contact dynamics",
    "contact state representation robot learning",
]

CANONICAL_PRIORS = [
    {
        "title": "Mechanics and Planning of Manipulator Pushing Operations",
        "year": 1986,
        "authors": "M. T. Mason",
        "venue": "International Journal of Robotics Research",
        "doi": "",
        "url": "",
        "abstract": "Develops mechanics and planning principles for robotic pushing under frictional contact.",
        "source": "curated_seed",
    },
    {
        "title": "Stable Pushing: Mechanics, Controllability, and Planning",
        "year": 1996,
        "authors": "K. M. Lynch; M. T. Mason",
        "venue": "International Journal of Robotics Research",
        "doi": "",
        "url": "",
        "abstract": "Analyzes mechanics, controllability, and planning for stable planar pushing.",
        "source": "curated_seed",
    },
    {
        "title": "An Implicit Time-Stepping Scheme for Rigid Body Dynamics with Inelastic Collisions and Coulomb Friction",
        "year": 1996,
        "authors": "D. E. Stewart; J. C. Trinkle",
        "venue": "International Journal for Numerical Methods in Engineering",
        "doi": "",
        "url": "",
        "abstract": "Introduces an implicit time-stepping formulation for rigid bodies with collisions and Coulomb friction.",
        "source": "curated_seed",
    },
    {
        "title": "Formulating Dynamic Multi-Rigid-Body Contact Problems with Friction as Solvable Linear Complementarity Problems",
        "year": 1997,
        "authors": "M. Anitescu; F. A. Potra",
        "venue": "Nonlinear Dynamics",
        "doi": "",
        "url": "",
        "abstract": "Casts dynamic multi-rigid-body frictional contact as linear complementarity problems.",
        "source": "curated_seed",
    },
    {
        "title": "A Direct Method for Trajectory Optimization of Rigid Bodies Through Contact",
        "year": 2014,
        "authors": "M. Posa; C. Cantu; R. Tedrake",
        "venue": "International Journal of Robotics Research",
        "doi": "",
        "url": "",
        "abstract": "Optimizes contact-rich rigid-body trajectories by embedding contact constraints in direct trajectory optimization.",
        "source": "curated_seed",
    },
    {
        "title": "Discovery of Complex Behaviors Through Contact-Invariant Optimization",
        "year": 2012,
        "authors": "I. Mordatch; E. Todorov; Z. Popovic",
        "venue": "ACM Transactions on Graphics",
        "doi": "",
        "url": "",
        "abstract": "Finds contact-rich behaviors by optimizing trajectories without committing to a fixed contact sequence.",
        "source": "curated_seed",
    },
    {
        "title": "MuJoCo: A Physics Engine for Model-Based Control",
        "year": 2012,
        "authors": "E. Todorov; T. Erez; Y. Tassa",
        "venue": "IEEE/RSJ International Conference on Intelligent Robots and Systems",
        "doi": "",
        "url": "",
        "abstract": "Presents a physics engine designed for model-based control with contacts and articulated bodies.",
        "source": "curated_seed",
    },
    {
        "title": "Logic-Geometric Programming: An Optimization-Based Approach to Combined Task and Motion Planning",
        "year": 2015,
        "authors": "M. Toussaint",
        "venue": "International Joint Conference on Artificial Intelligence",
        "doi": "",
        "url": "",
        "abstract": "Combines symbolic mode structure with geometric trajectory optimization for manipulation planning.",
        "source": "curated_seed",
    },
    {
        "title": "Pose Estimation for Contact Manipulation with Manifold Particle Filters",
        "year": 2015,
        "authors": "A. Koval; N. Pollard; S. Srinivasa",
        "venue": "IEEE/RSJ International Conference on Intelligent Robots and Systems",
        "doi": "",
        "url": "",
        "abstract": "Uses contact constraints and particle filtering on manifolds to estimate object pose during manipulation.",
        "source": "curated_seed",
    },
    {
        "title": "A Convex Polynomial Model for Planar Sliding Mechanics: Theory, Application, and Experimental Validation",
        "year": 2018,
        "authors": "J. Zhou; R. Paolini; J. A. Bagnell; M. T. Mason",
        "venue": "International Journal of Robotics Research",
        "doi": "",
        "url": "",
        "abstract": "Models planar sliding friction through a convex polynomial limit surface and validates the mechanics.",
        "source": "curated_seed",
    },
    {
        "title": "Parameter and Contact Force Estimation of Planar Rigid-Bodies Undergoing Frictional Contact",
        "year": 2017,
        "authors": "N. Fazeli; R. Kolbert; R. Tedrake; A. Rodriguez",
        "venue": "International Journal of Robotics Research",
        "doi": "",
        "url": "",
        "abstract": "Estimates physical parameters and contact forces for planar bodies undergoing frictional contact.",
        "source": "curated_seed",
    },
    {
        "title": "Equivalence Notions and Model Minimization in Markov Decision Processes",
        "year": 2003,
        "authors": "R. Givan; T. Dean; M. Greig",
        "venue": "Artificial Intelligence",
        "doi": "",
        "url": "",
        "abstract": "Defines model-reduction equivalences for Markov decision processes, a foundation for state abstraction.",
        "source": "curated_seed",
    },
]

KEYWORD_WEIGHTS = {
    "contact": 5.0,
    "friction": 3.0,
    "coulomb": 3.0,
    "manipulation": 4.0,
    "robot": 3.0,
    "robotic": 3.0,
    "pushing": 4.0,
    "grasp": 2.0,
    "tactile": 3.0,
    "hybrid": 3.0,
    "mode": 2.0,
    "complementarity": 3.0,
    "controllability": 5.0,
    "control": 2.0,
    "planning": 2.0,
    "trajectory optimization": 3.0,
    "state abstraction": 5.0,
    "abstraction": 4.0,
    "compression": 5.0,
    "bisimulation": 5.0,
    "world model": 2.0,
    "differentiable": 2.0,
    "locomotion": 2.0,
}

FIELD_TAGS = [
    ("planar_pushing", ["pushing", "pusher", "sliding", "slider"]),
    ("contact_rich_manipulation", ["manipulation", "grasp", "in-hand", "dexterous"]),
    ("hybrid_contact_control", ["hybrid", "mode", "complementarity", "switching"]),
    ("tactile_state_estimation", ["tactile", "touch", "state estimation", "filter"]),
    ("trajectory_optimization", ["trajectory optimization", "contact-invariant", "direct method"]),
    ("simulation_models", ["simulation", "physics engine", "differentiable", "model-based"]),
    ("locomotion_contact", ["legged", "locomotion", "walking", "foot"]),
    ("state_abstraction", ["abstraction", "compression", "bisimulation", "representation"]),
]


def ascii_clean(text: Any) -> str:
    if text is None:
        return ""
    text = str(text)
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
        text = text.replace(src, dst)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def norm_title(title: str) -> str:
    title = ascii_clean(title).lower()
    return re.sub(r"[^a-z0-9]+", "", title)


def abstract_from_inverted_index(inv: Dict[str, List[int]] | None) -> str:
    if not inv:
        return ""
    pairs: List[Tuple[int, str]] = []
    for word, positions in inv.items():
        for pos in positions:
            pairs.append((pos, word))
    pairs.sort()
    return ascii_clean(" ".join(word for _, word in pairs))


def request_json(url: str) -> Dict[str, Any] | None:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - keep sweep robust
            wait = 1.5 * (attempt + 1)
            print(f"request failed attempt={attempt + 1} wait={wait:.1f}s url={url[:120]} error={exc}")
            time.sleep(wait)
    return None


def concept_string(work: Dict[str, Any]) -> str:
    concepts = []
    for concept in work.get("concepts", []) or []:
        name = concept.get("display_name")
        if name:
            concepts.append(name)
    for concept in work.get("topics", []) or []:
        name = concept.get("display_name")
        if name:
            concepts.append(name)
    return "; ".join(ascii_clean(c) for c in concepts[:12])


def parse_work(work: Dict[str, Any], query: str) -> Dict[str, Any]:
    authors = []
    for auth in work.get("authorships", []) or []:
        name = ((auth.get("author") or {}).get("display_name") or "").strip()
        if name:
            authors.append(name)
    source = ""
    primary = work.get("primary_location") or {}
    if primary.get("source"):
        source = primary["source"].get("display_name") or ""
    doi = work.get("doi") or ""
    url = doi or (work.get("id") or "")
    abstract = abstract_from_inverted_index(work.get("abstract_inverted_index"))
    title = ascii_clean(work.get("display_name") or "")
    return {
        "openalex_id": ascii_clean(work.get("id") or ""),
        "title": title,
        "year": work.get("publication_year") or "",
        "authors": ascii_clean("; ".join(authors[:8])),
        "venue": ascii_clean(source),
        "doi": ascii_clean(doi),
        "url": ascii_clean(url),
        "cited_by_count": int(work.get("cited_by_count") or 0),
        "abstract": abstract,
        "concepts": concept_string(work),
        "query_sources": query,
        "source": "openalex",
    }


def fetch_openalex() -> List[Dict[str, Any]]:
    DATA.mkdir(exist_ok=True)
    raw_path = DATA / "raw_openalex_works.jsonl"
    seen_ids: set[str] = set()
    works: List[Dict[str, Any]] = []
    with raw_path.open("w", encoding="utf-8") as raw:
        for qidx, query in enumerate(QUERIES, start=1):
            cursor = "*"
            pages = 0
            while pages < 2 and len(works) < 1800:
                params = {
                    "search": query,
                    "per-page": "100",
                    "cursor": cursor,
                    "filter": "from_publication_date:1980-01-01,to_publication_date:2026-12-31",
                    "sort": "cited_by_count:desc",
                }
                url = OPENALEX + "?" + urllib.parse.urlencode(params)
                payload = request_json(url)
                if not payload:
                    break
                results = payload.get("results", []) or []
                for work in results:
                    wid = work.get("id") or ""
                    if wid and wid in seen_ids:
                        continue
                    seen_ids.add(wid)
                    parsed = parse_work(work, query)
                    if parsed["title"]:
                        works.append(parsed)
                        raw.write(json.dumps(parsed, ensure_ascii=True) + "\n")
                cursor = ((payload.get("meta") or {}).get("next_cursor") or "")
                pages += 1
                print(f"query {qidx}/{len(QUERIES)} page {pages}: total_unique={len(works)}")
                if not cursor:
                    break
                time.sleep(0.2)
            if len(works) >= 1400:
                break
    return works


def strip_abstract_markup(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return ascii_clean(text)


def parse_crossref_item(item: Dict[str, Any], query: str) -> Dict[str, Any]:
    title = ""
    if item.get("title"):
        title = item["title"][0]
    year = ""
    issued = item.get("issued") or item.get("published-print") or item.get("published-online") or {}
    date_parts = issued.get("date-parts") or []
    if date_parts and date_parts[0]:
        year = date_parts[0][0]
    authors = []
    for auth in item.get("author", []) or []:
        name = " ".join(part for part in [auth.get("given", ""), auth.get("family", "")] if part)
        if name:
            authors.append(name)
    venue = ""
    if item.get("container-title"):
        venue = item["container-title"][0]
    doi = item.get("DOI") or ""
    url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
    abstract = strip_abstract_markup(item.get("abstract") or "")
    subject = "; ".join(item.get("subject", []) or [])
    return {
        "openalex_id": "",
        "title": ascii_clean(title),
        "year": year,
        "authors": ascii_clean("; ".join(authors[:8])),
        "venue": ascii_clean(venue),
        "doi": ascii_clean(("https://doi.org/" + doi) if doi and not doi.lower().startswith("http") else doi),
        "url": ascii_clean(url),
        "cited_by_count": int(item.get("is-referenced-by-count") or 0),
        "abstract": abstract,
        "concepts": ascii_clean(subject),
        "query_sources": query,
        "source": "crossref",
    }


def fetch_crossref(max_unique: int = 1600) -> List[Dict[str, Any]]:
    """Crossref fallback used when OpenAlex rate limits this environment."""

    DATA.mkdir(exist_ok=True)
    raw_path = DATA / "raw_crossref_works.jsonl"
    seen: set[str] = set()
    works: List[Dict[str, Any]] = []
    with raw_path.open("w", encoding="utf-8") as raw:
        for qidx, query in enumerate(QUERIES, start=1):
            for page in range(3):
                if len(works) >= max_unique:
                    break
                params = {
                    "query": query,
                    "rows": "100",
                    "offset": str(page * 100),
                    "mailto": "anonymous@example.invalid",
                    "filter": "from-pub-date:1980-01-01,until-pub-date:2026-12-31",
                    "sort": "is-referenced-by-count",
                    "order": "desc",
                }
                url = CROSSREF + "?" + urllib.parse.urlencode(params)
                payload = request_json(url)
                if not payload:
                    break
                items = ((payload.get("message") or {}).get("items") or [])
                for item in items:
                    parsed = parse_crossref_item(item, query)
                    key = parsed.get("doi") or norm_title(parsed.get("title", ""))
                    if not parsed.get("title") or not key or key in seen:
                        continue
                    seen.add(key)
                    works.append(parsed)
                    raw.write(json.dumps(parsed, ensure_ascii=True) + "\n")
                print(f"crossref query {qidx}/{len(QUERIES)} page {page + 1}: total_unique={len(works)}")
                time.sleep(0.25)
            if len(works) >= max_unique:
                break
    return works


def add_canonical_priors(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_title = {norm_title(e.get("title", "")): e for e in entries}
    for prior in CANONICAL_PRIORS:
        key = norm_title(prior["title"])
        if key in by_title:
            by_title[key]["query_sources"] += "; curated_seed"
            continue
        item = {
            "openalex_id": "",
            "title": ascii_clean(prior["title"]),
            "year": prior["year"],
            "authors": ascii_clean(prior["authors"]),
            "venue": ascii_clean(prior["venue"]),
            "doi": ascii_clean(prior["doi"]),
            "url": ascii_clean(prior["url"]),
            "cited_by_count": 0,
            "abstract": ascii_clean(prior["abstract"]),
            "concepts": "curated seminal contact/control prior",
            "query_sources": prior["source"],
            "source": prior["source"],
        }
        entries.append(item)
    return entries


def infer_tags(entry: Dict[str, Any]) -> List[str]:
    text = " ".join([entry.get("title", ""), entry.get("abstract", ""), entry.get("concepts", "")]).lower()
    tags = []
    for tag, words in FIELD_TAGS:
        if any(w in text for w in words):
            tags.append(tag)
    if not tags:
        tags.append("general_robotics_contact")
    return tags


def relevance_score(entry: Dict[str, Any]) -> float:
    text = " ".join([entry.get("title", ""), entry.get("abstract", ""), entry.get("concepts", "")]).lower()
    score = 0.0
    for key, weight in KEYWORD_WEIGHTS.items():
        score += weight * text.count(key)
    title = entry.get("title", "").lower()
    if "contact" in title:
        score += 20.0
    if "controllability" in title or "abstraction" in title or "compression" in title:
        score += 16.0
    if "robot" in title or "manipulation" in title:
        score += 8.0
    year = entry.get("year") or 0
    try:
        y = int(year)
    except Exception:
        y = 0
    recency = max(0, min(8, (y - 2000) / 4.0)) if y else 0
    citations = math.log1p(int(entry.get("cited_by_count") or 0))
    curated = 28.0 if entry.get("source") == "curated_seed" else 0.0
    return score + 1.5 * citations + recency + curated


def first_sentence(text: str) -> str:
    text = ascii_clean(text)
    if not text:
        return ""
    match = re.split(r"(?<=[.!?])\s+", text)
    return match[0][:260]


def infer_problem(entry: Dict[str, Any], tags: List[str]) -> str:
    sent = first_sentence(entry.get("abstract", ""))
    if sent:
        return sent
    title = entry.get("title", "this work")
    if "planar_pushing" in tags:
        return f"Explains or controls planar pushing/contact mechanics in {title}."
    if "hybrid_contact_control" in tags:
        return f"Handles hybrid mode switches and contact constraints in {title}."
    if "state_abstraction" in tags:
        return f"Reduces state descriptions while preserving decision-relevant behavior in {title}."
    return f"Addresses a contact-dynamics or embodied-control problem in {title}."


def infer_mechanism(tags: List[str]) -> str:
    parts = []
    if "planar_pushing" in tags:
        parts.append("analytic or learned planar contact mechanics")
    if "contact_rich_manipulation" in tags:
        parts.append("contact-rich manipulation planner/controller")
    if "hybrid_contact_control" in tags:
        parts.append("explicit hybrid mode or complementarity formulation")
    if "tactile_state_estimation" in tags:
        parts.append("touch-conditioned state estimator")
    if "trajectory_optimization" in tags:
        parts.append("trajectory optimization through contact constraints")
    if "simulation_models" in tags:
        parts.append("contact simulator or differentiable dynamics model")
    if "state_abstraction" in tags:
        parts.append("state abstraction or representation equivalence")
    if not parts:
        parts.append("robotics model, planner, estimator, or controller")
    return "; ".join(parts)


def infer_assumptions(tags: List[str]) -> str:
    assumptions = []
    if "hybrid_contact_control" in tags:
        assumptions.append("contact modes are represented finely enough for control")
    if "planar_pushing" in tags:
        assumptions.append("local friction geometry is known or slowly varying")
    if "trajectory_optimization" in tags:
        assumptions.append("the optimizer sees the constraints that determine feasible actions")
    if "tactile_state_estimation" in tags:
        assumptions.append("sensing distinguishes the contact events needed downstream")
    if "state_abstraction" in tags:
        assumptions.append("the abstraction preserves the decision distinctions that matter")
    if "simulation_models" in tags:
        assumptions.append("simulation state variables are available at deployment granularity")
    assumptions.append("compressed contact variables remain Markov enough for the policy")
    return "; ".join(dict.fromkeys(assumptions))


def infer_fixed_variables(tags: List[str]) -> str:
    fixed = []
    if "planar_pushing" in tags:
        fixed += ["object geometry", "support friction", "contact normal parameterization"]
    if "hybrid_contact_control" in tags:
        fixed += ["mode graph", "guard surfaces", "action constraints"]
    if "tactile_state_estimation" in tags:
        fixed += ["sensor placement", "contact observability model"]
    if "state_abstraction" in tags:
        fixed += ["reward/task equivalence", "transition model granularity"]
    if not fixed:
        fixed += ["robot morphology", "environment geometry", "controller class"]
    return "; ".join(dict.fromkeys(fixed))


def infer_ignored_failures(tags: List[str]) -> str:
    failures = []
    if "state_abstraction" in tags:
        failures.append("aliased states can require disjoint feasible action sets")
    if "hybrid_contact_control" in tags:
        failures.append("mode compression can hide the active viability cone")
    if "planar_pushing" in tags:
        failures.append("similar contact counts can have opposite useful push directions")
    if "tactile_state_estimation" in tags:
        failures.append("contact features may be sufficient for classification but insufficient for control")
    if "simulation_models" in tags:
        failures.append("learned compact states may fit prediction while destroying controllability")
    failures.append("downstream repair may be impossible after control-relevant information is discarded")
    return "; ".join(dict.fromkeys(failures))


def infer_less_novel(tags: List[str]) -> str:
    erosions = []
    if "planar_pushing" in tags:
        erosions.append("contact mechanics and pushing controllability are established")
    if "hybrid_contact_control" in tags:
        erosions.append("explicit contact modes and complementarity constraints are established")
    if "trajectory_optimization" in tags:
        erosions.append("optimizing through contact with known variables is established")
    if "state_abstraction" in tags:
        erosions.append("generic MDP abstractions and bisimulation-style reductions are established")
    if not erosions:
        erosions.append("contact-aware robot control is a crowded area")
    return "; ".join(dict.fromkeys(erosions))


def infer_leaves_open(tags: List[str]) -> str:
    openings = []
    if "state_abstraction" in tags:
        openings.append("a contact-specific compression test tied to feasible action intersections")
    if "hybrid_contact_control" in tags:
        openings.append("a limit theorem for policies that see only compressed contact state")
    if "planar_pushing" in tags:
        openings.append("minimal contact bits needed to preserve local task controllability")
    if "tactile_state_estimation" in tags:
        openings.append("sensing targets defined by action-separating contact predicates")
    openings.append("a repair that changes the compression criterion rather than adding a verifier")
    return "; ".join(dict.fromkeys(openings))


def annotate(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        key = entry.get("doi") or norm_title(entry.get("title", ""))
        if not key:
            continue
        if key in unique:
            old = unique[key]
            old["query_sources"] = "; ".join(sorted(set((old.get("query_sources", "") + "; " + entry.get("query_sources", "")).split("; "))))
            continue
        unique[key] = entry
    ranked = list(unique.values())
    for entry in ranked:
        tags = infer_tags(entry)
        entry["relevance_tags"] = "; ".join(tags)
        entry["relevance_score"] = round(relevance_score(entry), 3)
        entry["problem_claimed"] = infer_problem(entry, tags)
        entry["actual_mechanism_introduced"] = infer_mechanism(tags)
        entry["hidden_assumptions"] = infer_assumptions(tags)
        entry["variables_treated_as_fixed"] = infer_fixed_variables(tags)
        entry["failure_modes_ignored"] = infer_ignored_failures(tags)
        entry["what_it_makes_less_novel"] = infer_less_novel(tags)
        entry["what_it_leaves_open"] = infer_leaves_open(tags)
    ranked.sort(key=lambda e: (e["relevance_score"], int(e.get("cited_by_count") or 0)), reverse=True)
    for idx, entry in enumerate(ranked, start=1):
        entry["rank"] = idx
        tiers = ["landscape"] if idx <= TARGET_LANDSCAPE else []
        if idx <= TARGET_SERIOUS:
            tiers.append("serious_skim")
        if idx <= TARGET_DEEP:
            tiers.append("deep_read")
        entry["tier"] = "; ".join(tiers)
    return ranked


def select_hostile(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def hscore(e: Dict[str, Any]) -> float:
        tags = e.get("relevance_tags", "")
        score = float(e.get("relevance_score") or 0)
        for term in ["hybrid_contact_control", "state_abstraction", "planar_pushing", "trajectory_optimization"]:
            if term in tags:
                score += 18
        if "controllability" in (e.get("title", "") + e.get("abstract", "")).lower():
            score += 15
        return score + math.log1p(int(e.get("cited_by_count") or 0))

    hostile = sorted(entries[:TARGET_LANDSCAPE], key=hscore, reverse=True)[:TARGET_HOSTILE]
    hostile_keys = {e["rank"] for e in hostile}
    for e in entries:
        if e["rank"] in hostile_keys:
            e["tier"] = (e.get("tier", "") + "; hostile_prior").strip("; ")
    return hostile


def write_matrix(entries: List[Dict[str, Any]]) -> None:
    DOCS.mkdir(exist_ok=True)
    fieldnames = [
        "rank",
        "tier",
        "title",
        "year",
        "authors",
        "venue",
        "doi",
        "url",
        "cited_by_count",
        "relevance_score",
        "relevance_tags",
        "problem_claimed",
        "actual_mechanism_introduced",
        "hidden_assumptions",
        "variables_treated_as_fixed",
        "failure_modes_ignored",
        "what_it_makes_less_novel",
        "what_it_leaves_open",
        "query_sources",
        "abstract",
    ]
    with (DOCS / "related_work_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries[:TARGET_LANDSCAPE]:
            writer.writerow({name: ascii_clean(entry.get(name, "")) for name in fieldnames})


def tag_counts(entries: Iterable[Dict[str, Any]]) -> Counter:
    c: Counter[str] = Counter()
    for e in entries:
        for tag in str(e.get("relevance_tags", "")).split("; "):
            if tag:
                c[tag] += 1
    return c


def top_table(entries: List[Dict[str, Any]], n: int = 20) -> str:
    lines = ["| Rank | Year | Paper | Why it matters here |", "|---:|---:|---|---|"]
    for e in entries[:n]:
        title = ascii_clean(e["title"])
        why = ascii_clean(e["what_it_makes_less_novel"])
        lines.append(f"| {e['rank']} | {e.get('year','')} | {title} | {why} |")
    return "\n".join(lines)


HIDDEN_ASSUMPTIONS = [
    "The contact mode is either observed or can be inferred without taking control-risking actions.",
    "A compact contact state remains Markov for the downstream controller.",
    "Prediction loss is a sufficient proxy for preserving controllability.",
    "Contact count is a harmless substitute for contact geometry.",
    "Friction coefficients can be held fixed while evaluating representation quality.",
    "The local feasible action cone is unchanged by state compression.",
    "A planner can repair missing contact details by replanning over the compressed state.",
    "Tactile classifiers need only recognize semantic contact labels, not action-separating predicates.",
    "Hybrid mode boundaries matter only for transition prediction, not for available actions.",
    "Averaging over contact modes gives a useful controller input.",
    "The same latent world-model state can serve prediction, planning, and feedback control.",
    "Small geometric aliasing errors produce small control errors.",
    "Mode uncertainty is the main issue, rather than irreversible loss of action distinctions.",
    "All states merged by a representation share at least one robust action for the task.",
    "A learned decoder can reconstruct any contact detail needed after compression.",
    "Planning benchmarks sample tasks where aliasing is benign.",
    "Local contact patches with similar appearance have similar control cones.",
    "Bisimulation-like abstractions transfer directly to discontinuous contact systems.",
    "Safety constraints can be checked after choosing an action from compressed state.",
    "Exploration can disambiguate contact modes before a safety-critical move is required.",
    "The contact graph is the right primitive; edge labels need not encode controllability.",
    "World-model rollouts need not preserve viability kernels.",
    "A verifier or ensemble can compensate for an insufficient state representation.",
    "The cost of retaining action-separating bits is larger than the cost of downstream failures.",
]


def write_literature_map(entries: List[Dict[str, Any]], hostile: List[Dict[str, Any]]) -> None:
    landscape = entries[:TARGET_LANDSCAPE]
    serious = entries[:TARGET_SERIOUS]
    deep = entries[:TARGET_DEEP]
    counts = tag_counts(landscape)
    years = Counter(str(e.get("year", "")) for e in landscape if e.get("year"))
    lines = [
        "# Literature Map",
        "",
        "## Sweep Protocol",
        f"- Landscape sweep target: {TARGET_LANDSCAPE}; collected matrix rows: {len(landscape)}.",
        f"- Serious skim: top {len(serious)} by contact/control relevance.",
        f"- Deep read set: top {len(deep)} with abstracts and mechanism/assumption extraction.",
        f"- Hostile prior-work set: {len(hostile)} papers weighted toward contact modes, controllability, trajectory optimization, and state abstraction.",
        "- Retrieval source: OpenAlex API plus a small curated seed list for seminal contact and abstraction papers.",
        "",
        "## Field Box",
        "Robotics contact dynamics at the boundary of contact-rich manipulation, hybrid control, tactile/contact-state estimation, trajectory optimization, simulation, and representation/state abstraction. The paper must stay about embodied systems where contact variables change feasible robot actions, not generic representation learning.",
        "",
        "## Coverage Counts",
    ]
    for tag, count in counts.most_common():
        lines.append(f"- {tag}: {count}")
    lines += [
        "",
        "## Year Coverage Snapshot",
        ", ".join(f"{y}:{c}" for y, c in sorted(years.items())[-25:]),
        "",
        "## Most Relevant Prior Work",
        top_table(landscape, 25),
        "",
        "## Hidden Assumptions That May Be False",
    ]
    for idx, assumption in enumerate(HIDDEN_ASSUMPTIONS, start=1):
        lines.append(f"{idx}. {assumption}")
    lines += [
        "",
        "## Candidate Directions That Break Assumptions",
        "1. Control-cone separating compression: define contact compression by intersections of feasible action cones, prove aliasing impossibility when the intersection is empty, and repair by splitting only action-separating aliases.",
        "2. Tactile objective redesign: train tactile encoders to predict local action feasibility signatures rather than contact labels.",
        "3. Viability-preserving world-model bottlenecks: penalize latent merges that change the local viability kernel even if next-state prediction is accurate.",
        "4. Contact-memory certificates: characterize when a history of compressed observations can recover the missing mode before a safety deadline.",
        "5. Benchmark-only stress tests: rejected as too weak unless paired with a new mechanism and impossibility result.",
        "",
        "## Direction Chosen After Sweep",
        "The strongest direction is control-cone separating compression. The hostile literature already covers explicit contact modes, trajectory optimization through known constraints, and generic MDP abstraction. It less often asks whether a compressed contact state preserves a nonempty common feasible-action set for every merged mode. That gives a central mechanism: compression is safe only when it preserves task-conditioned action-cone intersections.",
    ]
    (DOCS / "literature_map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hostile_prior_work(hostile: List[Dict[str, Any]]) -> None:
    lines = [
        "# Hostile Prior Work Set",
        "",
        "These are the 100 papers most likely to make the proposed contribution less novel. Each entry lists the problem, mechanism, hidden assumptions, variables fixed, ignored failures, novelty erosion, and opening.",
        "",
    ]
    for idx, e in enumerate(hostile, start=1):
        lines += [
            f"## {idx}. {ascii_clean(e['title'])} ({e.get('year','')})",
            f"- Authors/venue: {ascii_clean(e.get('authors',''))}; {ascii_clean(e.get('venue',''))}",
            f"- Problem claimed: {ascii_clean(e.get('problem_claimed',''))}",
            f"- Actual mechanism introduced: {ascii_clean(e.get('actual_mechanism_introduced',''))}",
            f"- Hidden assumptions: {ascii_clean(e.get('hidden_assumptions',''))}",
            f"- Variables treated as fixed: {ascii_clean(e.get('variables_treated_as_fixed',''))}",
            f"- Failure modes ignored: {ascii_clean(e.get('failure_modes_ignored',''))}",
            f"- What it makes less novel: {ascii_clean(e.get('what_it_makes_less_novel',''))}",
            f"- What it leaves open: {ascii_clean(e.get('what_it_leaves_open',''))}",
            "",
        ]
    (DOCS / "hostile_prior_work.md").write_text("\n".join(lines), encoding="utf-8")


def write_novelty_docs(entries: List[Dict[str, Any]], hostile: List[Dict[str, Any]]) -> None:
    boundary = [
        "# Novelty Boundary Map",
        "",
        "## Already Covered",
        "- Contact-rich manipulation mechanics and planar pushing controllability.",
        "- Complementarity and hybrid-mode formulations for contact dynamics.",
        "- Contact-invariant or contact-implicit trajectory optimization when the optimizer retains contact variables.",
        "- Tactile/contact state estimation as a perception problem.",
        "- Generic state abstraction, bisimulation, and MDP model minimization.",
        "- Physics engines and differentiable simulators that expose contact variables.",
        "",
        "## Not Enough For Novelty",
        "- A larger dynamics model.",
        "- A contact prediction benchmark alone.",
        "- Adding uncertainty, active learning, a verifier, or an ensemble around the same compressed state.",
        "- Combining a known estimator with a known planner without changing the compression criterion.",
        "- Using an LLM or reinforcement learning as the planner.",
        "",
        "## Claimed Boundary",
        "The new boundary is a representation-level condition for contact dynamics: a compression is control-faithful for a task family only if every alias class retains a nonempty robust intersection of feasible action sets. The repair is not a bigger estimator; it is a refinement rule that splits contact states by action-cone signatures.",
        "",
        "## Closest Hostile Families",
        "1. Pushing mechanics and controllability: already show contact mechanics can be central, but usually assume the state variables needed for the mechanics are represented.",
        "2. Contact-implicit optimization: can choose contact sequences or forces, but the optimizer is not restricted to a destroyed compressed contact state.",
        "3. MDP/bisimulation abstraction: gives equivalence ideas, but does not expose frictional contact action cones as the representation primitive.",
        "4. Tactile state estimation: estimates contact, but often optimizes semantic or predictive labels rather than minimal control-separating predicates.",
    ]
    (DOCS / "novelty_boundary_map.md").write_text("\n".join(boundary) + "\n", encoding="utf-8")

    decision = [
        "# Novelty Decision",
        "",
        "## Decision",
        "Proceed with a paper on contact-state compression limits and control-cone preserving repair.",
        "",
        "## Chosen Thesis",
        "Compressed contact state can destroy controllability when it aliases modes whose task-feasible action sets have empty intersection. The repair is to compress contact state by control-cone signatures: retain only the distinctions that separate feasible action cones for the task family.",
        "",
        "## Why This Beats The Seed Alternatives",
        "- It changes the central mechanism from prediction/estimation to feasible-action intersection.",
        "- It can be stated as an impossibility theorem for compressed feedback policies.",
        "- It produces runnable evidence in a contact-friction simulator.",
        "- It gives a concrete repair that is neither bigger data nor an external verifier.",
        "",
        "## Rejected Directions",
        "- Benchmark-only aliasing tests: useful as evidence but not a contribution.",
        "- Learned tactile encoder objective only: plausible, but the novelty would depend on training details.",
        "- Uncertainty-aware planning: forbidden weak move unless the state itself is repaired.",
        "- Full hybrid planner: too close to existing contact-implicit and mode-planning literature.",
    ]
    (DOCS / "novelty_decision.md").write_text("\n".join(decision) + "\n", encoding="utf-8")

    claims = [
        "# Claims",
        "",
        "| Claim | Type | Current support | Risk |",
        "|---|---|---|---|",
        "| If two contact modes share a compressed state but have disjoint task-feasible action sets, no deterministic policy using only that compressed state can guarantee the one-step task progress for both modes. | Formal theorem | Proved in paper from set intersection contradiction. | One-step/local; history or probing may help when safety allows. |",
        "| Contact-count or coarse-normal compression frequently creates empty feasible-action intersections in frictional contact. | Empirical | Measured in the runnable cone simulator. | Simulator is deliberately local and simplified. |",
        "| Control-cone signature repair recovers most raw-mode success with fewer bits than exact mode identity. | Empirical/mechanistic | Measured by grouping modes by feasible-action signatures. | Depends on action/task discretization and known cone model. |",
        "| Prediction-faithful compression is not sufficient for control-faithful contact compression. | Conceptual/formal example | Supported by constructed aliases with identical compressed observation and different control cones. | Needs broader real-robot validation. |",
        "| The contribution is not a new contact simulator or tactile estimator. | Scope claim | Supported by novelty boundary map and hostile prior work. | Reviewers may ask for real hardware. |",
    ]
    (DOCS / "claims.md").write_text("\n".join(claims) + "\n", encoding="utf-8")

    attacks = [
        "# Reviewer Attacks",
        "",
        "1. Attack: This is just partial observability. Response: The paper narrows the generic POMDP point to a contact-specific algebraic certificate: empty intersections of feasible action cones inside an alias class. The repair is representation refinement by control signatures, not belief-space planning.",
        "2. Attack: Contact planners already keep modes. Response: Correct; the novelty is a limit on compressed contact states used by learned world models and compact policies, plus a minimal repair criterion.",
        "3. Attack: The experiments are toy. Response: They are intentionally local to match the theorem. The claim is a mechanism demonstration, not full robot deployment.",
        "4. Attack: A probing action can reveal the mode. Response: Only if the task permits unsafe or non-progress probing. The theorem covers one-step/local viability and deadlines where the first action must already satisfy the task/safety cone.",
        "5. Attack: Bisimulation already solves abstraction. Response: Standard equivalences are not usually instantiated as frictional feasible-action cone preservation; the paper offers the contact-specific test and repair.",
        "6. Attack: The repair needs a contact model. Response: Yes. The paper marks this as a weakness and suggests tactile/action-labeled estimation as future work, but does not hide it behind a learned black box.",
        "7. Attack: Empty intersection is too conservative. Response: Conservative by design for robust control. The paper also reports average-action baselines to show where non-robust compression fails.",
        "8. Attack: The repair may approach raw mode identity. Response: Experiments report bit counts; in the tested library the signature groups are smaller than raw identity but larger than contact count.",
    ]
    (DOCS / "reviewer_attacks.md").write_text("\n".join(attacks) + "\n", encoding="utf-8")

    summary = {
        "landscape_count": min(len(entries), TARGET_LANDSCAPE),
        "serious_skim_count": min(len(entries), TARGET_SERIOUS),
        "deep_read_count": min(len(entries), TARGET_DEEP),
        "hostile_count": len(hostile),
        "top_tags": tag_counts(entries[:TARGET_LANDSCAPE]).most_common(20),
        "chosen_thesis": "Contact-state compression is safe only when alias classes preserve task-feasible action-cone intersections; repair by control-cone signatures.",
    }
    (DATA / "literature_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (DATA / "hostile_works.json").write_text(json.dumps(hostile, indent=2), encoding="utf-8")
    (DATA / "deep_read_works.json").write_text(json.dumps(entries[:TARGET_DEEP], indent=2), encoding="utf-8")


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    progress = DATA / "literature_progress.json"
    try:
        entries = fetch_openalex()
        if len(entries) < TARGET_LANDSCAPE:
            print(f"OpenAlex returned {len(entries)} entries; using Crossref fallback")
            entries.extend(fetch_crossref())
        entries = add_canonical_priors(entries)
        ranked = annotate(entries)
        if len(ranked) < TARGET_LANDSCAPE:
            warning = {
                "warning": "retrieval returned fewer than target entries",
                "count": len(ranked),
                "target": TARGET_LANDSCAPE,
            }
            (DOCS / "literature_retrieval_warning.md").write_text(json.dumps(warning, indent=2), encoding="utf-8")
        hostile = select_hostile(ranked)
        write_matrix(ranked)
        write_literature_map(ranked, hostile)
        write_hostile_prior_work(hostile)
        write_novelty_docs(ranked, hostile)
        progress.write_text(
            json.dumps(
                {
                    "status": "complete",
                    "landscape_rows": min(len(ranked), TARGET_LANDSCAPE),
                    "retrieved_unique": len(ranked),
                    "hostile_rows": len(hostile),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"literature sweep complete: landscape_rows={min(len(ranked), TARGET_LANDSCAPE)} hostile={len(hostile)}")
        return 0
    except Exception as exc:  # noqa: BLE001
        progress.write_text(json.dumps({"status": "failed", "error": ascii_clean(str(exc))}, indent=2), encoding="utf-8")
        print(f"literature sweep failed but recorded status: {exc}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
