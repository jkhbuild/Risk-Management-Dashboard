"""One-shot status backfill for Risk_Updates.

For each risk:
  - Sort updates chronologically.
  - For all non-last updates: assign Monitoring if the note contains a monitoring
    keyword, otherwise Open. Closure/realization keywords on non-last updates are
    IGNORED (per design: terminal status only occurs on the final update for
    each risk).
  - For the last update: apply full keyword rules. Closed wins over Realized
    wins over Monitoring; default Open.

Outputs a CSV the user reviews; user pastes values into the 'updated_status'
column already added to Risk_Updates_MASTER.xlsx.

Usage:
    PYTHONUTF8=1 python scripts/backfill_status.py
        [--updates-file PATH] [--out-file PATH]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UPDATES = PROJECT_ROOT / "source_data" / "Tonnelle_Risk_Updates_MASTER.xlsx"
DEFAULT_OUT = PROJECT_ROOT / "archive" / f"status_backfill_{dt.date.today():%y%m%d}.csv"

# Keyword rules. Closed wins over Realized wins over Monitoring. Default Open.
CLOSED_PATTERNS = [
    r"\brisk closed\b", r"\bclosed\b", r"\bresolved\b",
    r"\bno longer applicable\b", r"\bnot applicable\b",
    r"\bcancelled\b", r"\bcanceled\b", r"\bwithdrawn\b",
]
REALIZED_PATTERNS = [
    r"\brealized\b", r"\bmaterialized\b",
    r"\bchange order issued\b", r"\bchange order executed\b",
    r"\bbid item added\b", r"\bincident occurred\b", r"\bevent occurred\b",
]
MONITORING_PATTERNS = [
    r"\bmonitoring\b", r"\bwatching\b", r"\bunder review\b", r"\bdormant\b",
]


def has_match(note: str, patterns: list[str]) -> bool:
    text = (note or "").lower()
    return any(re.search(p, text) for p in patterns)


def infer_status(note: str, *, allow_terminal: bool) -> str:
    """Apply keyword rules. If allow_terminal=False, never return Closed/Realized
    (used for non-last updates per the design constraint).
    """
    if allow_terminal:
        if has_match(note, CLOSED_PATTERNS):
            return "Closed"
        if has_match(note, REALIZED_PATTERNS):
            return "Realized"
    if has_match(note, MONITORING_PATTERNS):
        return "Monitoring"
    return "Open"


def backfill(updates_path: Path, out_path: Path, verbose: bool = False) -> dict:
    upd = pd.read_excel(updates_path, sheet_name="Risk_Updates")
    upd = upd.dropna(subset=["risk_id"]).copy()
    # Sort by risk and chronologically by (date, id) so the "last" update is correctly identified
    upd = upd.sort_values(["risk_id", "update_date", "update_id"]).reset_index(drop=True)

    proposals = []
    counts = {"Open": 0, "Monitoring": 0, "Realized": 0, "Closed": 0}
    final_per_risk: dict[str, str] = {}

    # Walk per risk
    for rid, group in upd.groupby("risk_id", sort=False):
        rows = group.to_dict("records")
        last_idx = len(rows) - 1
        for i, r in enumerate(rows):
            is_last = (i == last_idx)
            proposed = infer_status(str(r["note"]), allow_terminal=is_last)
            counts[proposed] = counts.get(proposed, 0) + 1
            if is_last:
                final_per_risk[rid] = proposed
            proposals.append({
                "update_id": r["update_id"],
                "risk_id": rid,
                "update_date": r["update_date"].date() if pd.notna(r["update_date"]) else "",
                "author": r["author"],
                "note": r["note"],
                "is_last_update": "YES" if is_last else "",
                "proposed_updated_status": proposed,
            })
            if verbose:
                print(f"  {rid} {r['update_date'].date() if pd.notna(r['update_date']) else '?'} "
                      f"{'[LAST]' if is_last else '      '}: {proposed}")

    # Sort output back to original update_id order so paste-into-Excel is straightforward
    proposals.sort(key=lambda x: (str(x["update_id"]) if isinstance(x["update_id"], (int, float)) else x["update_id"]))
    # update_id might be int; coerce to int for proper numeric sort
    def _key(p):
        try:
            return (0, int(p["update_id"]))
        except (TypeError, ValueError):
            return (1, str(p["update_id"]))
    proposals.sort(key=_key)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(proposals[0].keys()))
        writer.writeheader()
        writer.writerows(proposals)

    return {
        "total_updates": len(proposals),
        "counts": counts,
        "out_file": str(out_path),
        "final_open": sum(1 for s in final_per_risk.values() if s == "Open"),
        "final_monitoring": sum(1 for s in final_per_risk.values() if s == "Monitoring"),
        "final_realized": sum(1 for s in final_per_risk.values() if s == "Realized"),
        "final_closed": sum(1 for s in final_per_risk.values() if s == "Closed"),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--updates-file", type=Path, default=DEFAULT_UPDATES)
    p.add_argument("--out-file", type=Path, default=DEFAULT_OUT)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    if not args.updates_file.exists():
        sys.exit(f"updates file not found: {args.updates_file}")

    s = backfill(args.updates_file, args.out_file, args.verbose)
    print(f"\nWrote {s['total_updates']} proposed rows to:")
    print(f"  {s['out_file']}")
    print(f"\nStatus distribution across all updates:")
    for k, v in s["counts"].items():
        print(f"  {k}: {v}")
    print(f"\nFinal status per risk (37 risks):")
    print(f"  Open: {s['final_open']}")
    print(f"  Monitoring: {s['final_monitoring']}")
    print(f"  Realized: {s['final_realized']}")
    print(f"  Closed: {s['final_closed']}")
    print("\nNext: open the CSV, paste the 'proposed_updated_status' column into")
    print("the 'updated_status' column in Tonnelle_Risk_Updates_MASTER.xlsx.")


if __name__ == "__main__":
    main()
