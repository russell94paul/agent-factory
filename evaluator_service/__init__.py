"""The evaluator, run as its own principal.

Deliberately a sibling of ``factory/`` and not a module inside it. The package boundary is the
cheap part; what it documents is the intent — this tree is the one that should end up deployed
somewhere the graded agent holds no credential for, and it imports ``factory`` rather than the
other way round, so lifting it out is a packaging change and not a refactor.

    python -m evaluator_service --port 8787
"""
