"""The projection boundary — what is allowed to leave the Factory, per artifact type.

Extracted 2026-09-01 from :mod:`factory.client_review`, unchanged in behaviour, because a second
artifact type (:mod:`factory.case_study`) needs the same boundary and a boundary that exists twice
is a boundary that will diverge once.

**The rule this module exists to enforce: the boundary is an ALLOW-list, never a deny-list.**

On 2026-08-31 a deny-list over a credential file ("drop lines containing 'password'") let three
plaintext passwords through, because the vault stores them in markdown tables and the word
*password* is in the header row, never the data rows. A guard is only as wide as the relation it
derives over. So :func:`safe` copies the fields a table names, and everything else — every field a
future contributor adds, every field nobody thought about — is dropped by default.

⭐ **Adding a field to a view model does not publish it.** That is the whole design. It is also why
:func:`safe` raises on an unknown section rather than returning ``{}``: a typo'd section name that
silently emptied a panel would read as "nothing to report", which is the failure this repo keeps
paying for in other forms.

Each artifact type registers its own table. Two tables exist today and they are deliberately
different — a client review and an internal forensic case study have different audiences, and the
case study's table is the *narrower* of the two despite being the internal one, because it carries
our own failures and a client's commercial figures.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple


class ProjectionError(ValueError):
    """A projection was asked for something it has no allow-list for."""


class LeakError(ProjectionError):
    """A projected string carried something the deny-gate recognised.

    Reaching this exception means the allow-list already failed. It is a backstop, and a hit here
    is a defect to fix in the projection — never something to suppress at the call site.
    """


#: Substrings that must never appear in a projected string, whatever the allow-list says. This is a
#: second, independent gate — belt and braces — and it is explicitly NOT the primary control,
#: because a deny-list alone is what failed on 2026-08-31.
FORBIDDEN: Tuple[str, ...] = (
    "password", "passwd", "secret", "api_key", "apikey", "token=", "bearer ",
    "azure-kv:", "keyvault", "private_key", "-----begin",
)

#: artifact name -> {section -> allowed field names}
_TABLES: Dict[str, Dict[str, tuple]] = {}


def register(artifact: str, table: Dict[str, tuple]) -> None:
    """Register one artifact type's allow-list. Re-registration replaces, so import order cannot
    silently widen a boundary by merging two partial tables."""
    _TABLES[artifact] = dict(table)


def sections(artifact: str) -> tuple:
    if artifact not in _TABLES:
        raise ProjectionError(f"no projection registered for artifact {artifact!r}")
    return tuple(_TABLES[artifact])


def scan(value: Any, where: str) -> Any:
    """Backstop scan. Raises rather than redacting: a silent redaction hides a broken boundary."""
    if isinstance(value, str):
        low = value.lower()
        for bad in FORBIDDEN:
            if bad in low:
                raise LeakError(
                    f"{where}: projected string contains {bad!r}. The allow-list let this through, "
                    "which means the projection is wrong — fix the projection, do not redact here.")
    elif isinstance(value, dict):
        for k, v in value.items():
            scan(v, f"{where}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            scan(v, f"{where}[{i}]")
    return value


def safe(artifact: str, section: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """Project one row through `artifact`'s allow-list for `section`.

    Unknown artifact or unknown section raises. Both are the same argument: a surface with no
    declared boundary is not publishable by default, and that is the intended behaviour.
    """
    if artifact not in _TABLES:
        raise ProjectionError(
            f"no projection registered for artifact {artifact!r}. An artifact with no allow-list "
            "publishes nothing — register a table before projecting.")
    table = _TABLES[artifact]
    if section not in table:
        raise ProjectionError(
            f"{artifact}.{section!r} has no allow-list. Add one — a section with no allow-list is "
            "not publishable by default, and that is the intended behaviour.")
    out = {k: row[k] for k in table[section] if k in row}
    return scan(out, f"{artifact}.{section}")
