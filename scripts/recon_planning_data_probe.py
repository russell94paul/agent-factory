"""RECON / ECHELON 0 probe -- venture topic `leads`.

Measures the national planning-application open dataset at planning.data.gov.uk
against the four questions ECHELON 0 has to answer about it:

  1. COVERAGE   how many English LPAs actually appear, out of ~317
  2. IDENTITY   is there any personal data (address-text, uprn) -- i.e. is this
                a lead, or only a statistic
  3. FRESHNESS  newest entry-date / decision-date -- the wedge is "days earlier",
                so a stale feed kills the product regardless of everything else
  4. SIGNAL     how many records mention solar / heat pump / EV charging at all

Read-only. No spend. Streams the bulk CSV; nothing is written but the report.

Run:  python scripts/recon_planning_data_probe.py
"""

import collections
import csv
import io
import json
import re
import sys
import urllib.request

BULK = "https://files.planning.data.gov.uk/dataset/planning-application.csv"
DATASET_META = "https://www.planning.data.gov.uk/dataset/planning-application.json"

SIGNAL = {
    "solar": re.compile(r"solar|photovoltaic|\bpv\b", re.I),
    "heat_pump": re.compile(r"heat pump|ashp|gshp|air source|ground source", re.I),
    "ev_charging": re.compile(r"ev charg|electric vehicle charg|charging point|charge point", re.I),
    "battery": re.compile(r"battery storage|batteries|bess", re.I),
}

# Columns whose fill rate decides whether a record can become a contactable lead.
IDENTITY_COLS = ["address-text", "uprn", "point", "geometry", "documentation-url"]
# Columns that decide whether the record can be filtered/timed at all.
USABILITY_COLS = ["planning-application-type", "planning-application-status",
                  "planning-decision", "decision-date", "development-classification"]


def fetch_meta():
    with urllib.request.urlopen(DATASET_META, timeout=60) as r:
        return json.load(r)


def main():
    meta = fetch_meta()

    rows = 0
    orgs = collections.Counter()
    filled = collections.Counter()
    signal_hits = collections.Counter()
    signal_and_address = collections.Counter()
    max_entry = ""
    max_decision = ""
    no_description = 0

    req = urllib.request.Request(BULK, headers={"User-Agent": "agent-factory-recon/0.1"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        stream = io.TextIOWrapper(resp, encoding="utf-8", errors="replace", newline="")
        reader = csv.DictReader(stream)
        cols = reader.fieldnames or []
        for row in reader:
            rows += 1
            orgs[row.get("organisation-entity", "")] += 1

            for c in IDENTITY_COLS + USABILITY_COLS:
                if (row.get(c) or "").strip():
                    filled[c] += 1

            ed = (row.get("entry-date") or "").strip()
            if ed > max_entry:
                max_entry = ed
            dd = (row.get("decision-date") or "").strip()
            if dd > max_decision:
                max_decision = dd

            desc = (row.get("description") or "").strip()
            if not desc:
                no_description += 1
            has_addr = bool((row.get("address-text") or "").strip())
            for key, pat in SIGNAL.items():
                if desc and pat.search(desc):
                    signal_hits[key] += 1
                    if has_addr:
                        signal_and_address[key] += 1

    def pct(n):
        return f"{n:>8,}  ({100.0 * n / rows:5.1f}%)" if rows else "n/a"

    print("=" * 68)
    print("RECON ECHELON 0 -- planning.data.gov.uk `planning-application`")
    print("=" * 68)
    print(f"declared entity-count : {meta.get('entity-count'):,}")
    print(f"licence               : {meta.get('licence')}  ({meta.get('attribution')})")
    print(f"phase                 : {meta.get('phase')}")
    print(f"columns               : {len(cols)}")
    print()
    print(f"1 COVERAGE   rows streamed        : {rows:,}")
    print(f"             distinct LPAs        : {len(orgs)}   (England has ~317 LPAs)")
    print(f"             top 5 LPAs by volume : {orgs.most_common(5)}")
    print()
    print("2 IDENTITY   -- can a record become a contactable lead?")
    for c in IDENTITY_COLS:
        print(f"             {c:<26}{pct(filled[c])}")
    print()
    print("             NOTE: there is no applicant-name or agent-name column at all.")
    print()
    print("3 FRESHNESS  newest entry-date     : {}".format(max_entry or "NONE"))
    print(f"             newest decision-date : {max_decision or 'NONE'}")
    print()
    print("4 SIGNAL     rows with no description : {}".format(pct(no_description)))
    for k in SIGNAL:
        print(f"             {k:<12} in description  {pct(signal_hits[k])}"
              f"   of which addressable: {signal_and_address[k]:,}")
    print()
    print("5 USABILITY  -- can the population be filtered and timed?")
    for c in USABILITY_COLS:
        print(f"             {c:<26}{pct(filled[c])}")
    print("=" * 68)


if __name__ == "__main__":
    sys.exit(main())
