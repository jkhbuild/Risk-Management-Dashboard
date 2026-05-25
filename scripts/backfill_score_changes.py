"""One-shot score backfill for Risk_Updates.

Generates proposed values for probability_at_update / cost_impact_at_update /
schedule_impact_at_update on existing rows. Conservative pattern (most rows
stay null = no change), with deliberate exceptions:

  - **Initial update for each risk** (chronologically first): seed all 3
    columns with the Risk_Register baseline. This marks the risk's starting
    point on the Page 3 Score Over Time chart.
  - **Realized update** (last update for a Realized risk): freeze the latest
    lookback values into this row so the chart has an explicit endpoint.
  - **Closed update**: leave nulls (the [Score At Update] DAX returns 0
    automatically for Closed status).
  - **Keyword-hinted bumps**: when a note mentions "approaching", "rising",
    "deteriorating", "concern", "shoulder season" etc., propose probability +1
    (capped at 5). Most updates pass through unchanged (null).

Outputs a CSV the user reviews; user pastes accepted values into the 3 score
columns in Risk_Updates_MASTER.xlsx.

The DAX measure [Score At Update] (in _Measures.tmdl) handles lifecycle:
Closed → 0, Realized → frozen, otherwise lookback to latest non-null + baseline
fallback. This script feeds that measure the explicit data points.

Usage:
    PYTHONUTF8=1 python scripts/backfill_score_changes.py
        [--updates-file PATH] [--register-file PATH] [--out-file PATH]
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
DEFAULT_REGISTER = PROJECT_ROOT / "source_data" / "Tonnelle_Risk_Register_MASTER.xlsx"
DEFAULT_OUT = PROJECT_ROOT / "archive" / f"score_backfill_{dt.date.today():%y%m%d}.csv"

# Score-bump hints. Each pattern triggers a probability +1 on the matching row
# (capped at 5). Cost/schedule bumps require explicit user direction — too
# easy to misread notes for those, so leave them blank by default.
PROB_BUMP_PATTERNS = [
    r"\bapproaching\b", r"\brising\b", r"\bclimbing\b", r"\bincreasing\b",
    r"\bdeteriorating\b", r"\bworsening\b", r"\bescalating\b",
    r"\bconcern\b", r"\bconcerned\b", r"\bworry\b", r"\bworried\b",
    r"\bshoulder season\b", r"\bwinter\b", r"\bcold\b", r"\bsevere\b",
    r"\baccelerat\w+\b",
]
PROB_DROP_PATTERNS = [
    r"\bimproving\b", r"\bstabiliz\w+\b", r"\babating\b", r"\bsubsid\w+\b",
    r"\breduced exposure\b", r"\bmitigated\b",
]


def has_match(note: str, patterns: list[str]) -> bool:
    t = (note or "").lower()
    return any(re.search(p, t) for p in patterns)


def backfill(updates_path: Path, register_path: Path, out_path: Path,
             verbose: bool = False) -> dict:
    upd = pd.read_excel(updates_path, sheet_name="Risk_Updates")
    reg = pd.read_excel(register_path, sheet_name="Risk_Register")
    upd = upd.dropna(subset=["risk_id"]).copy()
    upd = upd.sort_values(["risk_id", "update_date", "update_id"]).reset_index(drop=True)

    # Baseline scores per risk_id from Risk_Register
    base = {}
    for _, r in reg.dropna(subset=["risk_id"]).iterrows():
        base[str(r["risk_id"])] = {
            "P": int(r["probability_score"]) if pd.notna(r["probability_score"]) else None,
            "C": int(r["cost_impact_score"]) if pd.notna(r["cost_impact_score"]) else None,
            "S": int(r["schedule_impact_score"]) if pd.notna(r["schedule_impact_score"]) else None,
        }

    proposals = []
    stats = {"initial_seeded": 0, "bump_proposed": 0, "drop_proposed": 0,
             "realized_frozen": 0, "closed_left_null": 0, "unchanged": 0}

    for rid, group in upd.groupby("risk_id", sort=False):
        rows = group.to_dict("records")
        b = base.get(str(rid), {"P": None, "C": None, "S": None})

        # Track current effective score for each component (for realized-freeze)
        cur_P, cur_C, cur_S = b["P"], b["C"], b["S"]

        for i, r in enumerate(rows):
            is_first = (i == 0)
            note = str(r.get("note") or "")
            status = str(r.get("updated_status") or "").strip()

            p_val = c_val = s_val = None
            reason = ""

            if is_first:
                # Seed baseline on the first update for this risk
                p_val, c_val, s_val = b["P"], b["C"], b["S"]
                reason = "initial"
                stats["initial_seeded"] += 1
            elif status == "Realized":
                # Freeze: write the latest known scores onto this row
                p_val, c_val, s_val = cur_P, cur_C, cur_S
                reason = "realized-freeze"
                stats["realized_frozen"] += 1
            elif status == "Closed":
                # Leave null; DAX returns 0
                reason = "closed-null (DAX returns 0)"
                stats["closed_left_null"] += 1
            elif has_match(note, PROB_BUMP_PATTERNS):
                # Conservative +1 to probability
                if cur_P is not None and cur_P < 5:
                    p_val = cur_P + 1
                    reason = "bump-keyword"
                    stats["bump_proposed"] += 1
                else:
                    reason = "bump-skip (already 5)"
                    stats["unchanged"] += 1
            elif has_match(note, PROB_DROP_PATTERNS):
                # Conservative -1 to probability
                if cur_P is not None and cur_P > 1:
                    p_val = cur_P - 1
                    reason = "drop-keyword"
                    stats["drop_proposed"] += 1
                else:
                    reason = "drop-skip (already 1)"
                    stats["unchanged"] += 1
            else:
                reason = "unchanged"
                stats["unchanged"] += 1

            # Update current state if scores changed
            if p_val is not None: cur_P = p_val
            if c_val is not None: cur_C = c_val
            if s_val is not None: cur_S = s_val

            proposals.append({
                "update_id": r["update_id"],
                "risk_id": rid,
                "update_date": r["update_date"].date() if pd.notna(r["update_date"]) else "",
                "updated_status": status,
                "note": note[:90],
                "proposed_probability_at_update": p_val if p_val is not None else "",
                "proposed_cost_impact_at_update": c_val if c_val is not None else "",
                "proposed_schedule_impact_at_update": s_val if s_val is not None else "",
                "reason": reason,
            })

            if verbose:
                print(f"  {rid} {r['update_date'].date() if pd.notna(r['update_date']) else '?'} "
                      f"[{reason:20}]: P={p_val} C={c_val} S={s_val}")

    # Sort by update_id for pasting
    def _key(p):
        try:
            return (0, int(p["update_id"]))
        except (TypeError, ValueError):
            return (1, str(p["update_id"]))
    proposals.sort(key=_key)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(proposals[0].keys()))
        w.writeheader()
        w.writerows(proposals)

    return {"total": len(proposals), "out": str(out_path), **stats}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--updates-file", type=Path, default=DEFAULT_UPDATES)
    p.add_argument("--register-file", type=Path, default=DEFAULT_REGISTER)
    p.add_argument("--out-file", type=Path, default=DEFAULT_OUT)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    if not args.updates_file.exists():
        sys.exit(f"updates file not found: {args.updates_file}")
    if not args.register_file.exists():
        sys.exit(f"register file not found: {args.register_file}")

    s = backfill(args.updates_file, args.register_file, args.out_file, args.verbose)
    print(f"\nWrote {s['total']} rows to:\n  {s['out']}")
    print(f"\nBreakdown:")
    print(f"  Initial (baseline seeded):  {s['initial_seeded']}")
    print(f"  Realized (frozen):          {s['realized_frozen']}")
    print(f"  Closed (null, DAX→0):       {s['closed_left_null']}")
    print(f"  Probability +1 (bump):      {s['bump_proposed']}")
    print(f"  Probability -1 (drop):      {s['drop_proposed']}")
    print(f"  Unchanged (null):           {s['unchanged']}")
    print("\nNext: review CSV, paste the 3 proposed_* columns into the 3 score")
    print("columns in Tonnelle_Risk_Updates_MASTER.xlsx. Blank cells stay blank.")


if __name__ == "__main__":
    main()
