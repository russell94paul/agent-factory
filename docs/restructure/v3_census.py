"""Census of v3-introduced terms over the working tree.

BASELINE NOTE: the table published in 09_RESEARCH_MANIFEST_V3_RECONCILIATION.md section 5 was
measured at 998 files, BEFORE Gate P0-B surfaced the canonical ontology and converted three
binaries into docs/raw_research/. A run today scans ~1003 files and returns higher counts for
terms those documents contain. That is the gate working, not drift. Post-P0-B measurements are
per-source, in 14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md sections 5 and 6.

Excludes docs/restructure/ (this Phase 1 pass's own writing -- including it counted
our own output as evidence of the project's design state on a previous run) and
docs/research/DESIGN_DELTA_SINCE_SIHRE_QUEUE.md for the same reason.
Also reports separately whether each term appears in factory/ code.
"""
import os
import re
import sys

ROOT = "."
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".worktrees", ".venv", "venv"}
SKIP_PREFIX = (
    os.path.join("docs", "restructure"),
    # The three ingested manifests. They are the SOURCE of the vocabulary being censused; counting
    # them would report the proposal as evidence of the repository's design state -- the same error
    # that including docs/restructure/ produced on the first Phase 1 run.
    os.path.join("docs", "raw_research", "CELL_OS_Research_Manifest_v3_Repo_Ingestion_Pack"),
)
SKIP_FILES = {
    os.path.join("docs", "research", "DESIGN_DELTA_SINCE_SIHRE_QUEUE.md"),
}
TEXT_EXT = {
    ".md", ".txt", ".py", ".yaml", ".yml", ".json", ".html", ".css", ".js",
    ".ts", ".tsx", ".toml", ".cfg", ".ini", ".sh", ".ps1", ".sql", ".jsonl",
}

TERMS = [
    "Operative Kernel",
    "Operative Cell",
    "Mission Compiler",
    "Mission Contract",
    "Claims-Evidence Graph",
    "Claims–Evidence Graph",
    "Capability Graph",
    "Causal World Model",
    "Shadow Execution Twin",
    "Shadow Twin",
    "Temporal Executive",
    "Earned Authority",
    "Operative Immune System",
    "Cognitive Economics",
    "Experience-to-Doctrine",
    "Domain Plane",
    "Domain Genome",
    "Domain Compiler",
    "Domain Fabric",
    "Domain Data Plane",
    "MESA",
    "Recursive Operative Genesis",
    "CELL-Q",
    "CELL ADAPT",
    "CELL Foundry",
    "HyperMESH",
    "Link Fabric",
    "Link Contract",
    "Link Type Registry",
    "CellBus",
    "C-MESH",
    "T-MESH",
    "OS-MESH",
    "Mission Hypergraph",
    "Morphogenetic",
    "Stigmergic",
    "Temporal Echelon",
    "Evolution Chamber",
    "Capability Lab",
    "ORCA",
    "Cell Studio",
    "Mission Control",
    "Briefing Room",
    "SIHRE",
    "OPC",
    "Org-IR",
    "Organizational Compiler",
    "Cell Blueprint",
    "Cell Genome",
    "Configuration Genome",
    "Cell Mesh",
    "Mesh Gradient",
    "Regime-Adaptive",
    "NERVE",
    "Operative Canonical Layered Model",
    "capability envelope",
]

pats = [(t, re.compile(re.escape(t), re.I)) for t in TERMS]
hits = {t: [0, set(), 0] for t in TERMS}  # occurrences, files, code_occurrences

nfiles = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        p = os.path.normpath(os.path.join(dirpath, fn))
        rel = p[2:] if p.startswith("." + os.sep) else p
        if rel.startswith(SKIP_PREFIX) or rel in SKIP_FILES:
            continue
        if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
            continue
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        nfiles += 1
        in_code = rel.startswith("factory" + os.sep) or rel.startswith("evaluator_service" + os.sep)
        for t, pat in pats:
            n = len(pat.findall(text))
            if n:
                hits[t][0] += n
                hits[t][1].add(rel)
                if in_code:
                    hits[t][2] += n

print("scanned_text_files:", nfiles)
print()
print("| Term | Occurrences | Files | In factory/ code |")
print("|---|---:|---:|---:|")
for t in TERMS:
    o, f, c = hits[t]
    print("| {} | {} | {} | {} |".format(t, o, len(f), c))
