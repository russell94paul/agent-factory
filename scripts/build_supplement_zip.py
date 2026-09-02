"""Build agent-factory-architecture-supplement.zip — the 2026-09-02 review supplement.

Deterministic and re-runnable. Prints a manifest with sizes and a sha256 per entry so the
archive's contents are checkable without opening it.

    python scripts/build_supplement_zip.py
"""
from __future__ import annotations

import hashlib
import pathlib
import zipfile

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "agent-factory-architecture-supplement.zip"

#: (path relative to repo root, path inside the archive)
MEMBERS = [
    # the readme first, so an unzip lists it first
    ("docs/_index/SUPPLEMENT_README.md", "SUPPLEMENT_README.md"),
    # the substance of this pass
    ("docs/_index/agent_army_wave0_supplement.md",
     "docs/_index/agent_army_wave0_supplement.md"),
    # newly extracted DOCX material
    ("docs/raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md",
     "docs/raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md"),
    ("docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md",
     "docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md"),
    # the converter, so the extraction is reproducible rather than trusted
    ("scripts/docx_to_md.py", "scripts/docx_to_md.py"),
    # every canonical index this pass modified
    ("docs/_index/corpus_manifest.yaml", "docs/_index/corpus_manifest.yaml"),
    ("docs/_index/document_catalog.md", "docs/_index/document_catalog.md"),
    ("docs/_index/concept_index.yaml", "docs/_index/concept_index.yaml"),
    ("docs/_index/contradictions.md", "docs/_index/contradictions.md"),
    ("docs/_index/supersession_candidates.md", "docs/_index/supersession_candidates.md"),
    ("docs/_index/current_vs_proposed.md", "docs/_index/current_vs_proposed.md"),
    ("docs/_index/high_leverage_concepts.md", "docs/_index/high_leverage_concepts.md"),
    ("docs/_index/research_gap_candidates.md", "docs/_index/research_gap_candidates.md"),
    ("docs/research/backlog.yaml", "docs/research/backlog.yaml"),
    ("docs/research/dependency_graph.md", "docs/research/dependency_graph.md"),
]


def main() -> int:
    missing = [rel for rel, _ in MEMBERS if not (REPO / rel).is_file()]
    if missing:
        print("MISSING, refusing to build:")
        for m in missing:
            print("  ", m)
        return 1

    if OUT.exists():
        OUT.unlink()

    total = 0
    rows = []
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, arc in MEMBERS:
            data = (REPO / rel).read_bytes()
            # fixed timestamp so two builds of the same content are identical
            info = zipfile.ZipInfo(arc, date_time=(2026, 9, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
            total += len(data)
            rows.append((arc, len(data), hashlib.sha256(data).hexdigest()[:16]))

    print("%-72s %9s  %s" % ("entry", "bytes", "sha256[:16]"))
    for arc, n, h in rows:
        print("%-72s %9d  %s" % (arc, n, h))
    print("-" * 100)
    print("%d entries, %d bytes uncompressed, archive %d bytes"
          % (len(rows), total, OUT.stat().st_size))
    print("archive sha256: %s" % hashlib.sha256(OUT.read_bytes()).hexdigest())
    print("written: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
