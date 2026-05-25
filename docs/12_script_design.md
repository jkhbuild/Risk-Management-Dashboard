# 12 - append_updates.py: design, CLI, limits

Phase 12 deliverable. The operational tool that keeps `Risk_Updates` in sync with new dated entries the user adds to `Risk_Register.mitigation_log`. No Power BI skills required; pure Python on the data layer.

The script preserves the Phase 1 lock: `Risk_Updates` remains a single-sheet append-only flat table with columns `update_id, risk_id, update_date, update_year, author, note`. New rows are appended below existing rows in source-data order; `update_id` continues from `MAX(existing) + 1`.

Source of truth (read-only): `source_data/Tonnelle_Risk_Register_MASTER.xlsx` and `source_data/Tonnelle_Risk_Updates_MASTER.xlsx`. The script never modifies the Register and only writes to `Risk_Updates` after a successful append computation (with optional pre-write backup).

---

## a) Workflow

The dashboard owner does not edit the Register. The risk manager (RM) on the project does. The RM emails a dated copy of the workbook back to the owner on each update cycle; the owner promotes the incoming file to MASTER and runs this script to bring `Risk_Updates_MASTER.xlsx` into sync with the new `mitigation_log` entries.

Per update cycle:

1. **RM** opens his working copy of `Tonnelle_Risk_Register_TEMPLATE.xlsx`, adds new risks and/or adds dated entries to existing `mitigation_log` cells. Dates use `M/D - text` shorthand, year implied. Save-as with a date suffix: `Tonnelle_Risk_Register_<YYMMDD>.xlsx`. Email to owner.
2. **Owner** drops the incoming file into `/archive/` (preserves the dated snapshot) and overwrites `/source_data/Tonnelle_Risk_Register_MASTER.xlsx` with the same file's content.
3. **Owner** runs `python scripts/append_updates.py --dry-run`. Reviews the proposed append rows and the DISCREPANCY block (§h) if any flags are surfaced.
4. **Owner** re-runs without `--dry-run` to commit. Before the write, the existing `Tonnelle_Risk_Updates_MASTER.xlsx` is auto-archived to `archive/Tonnelle_Risk_Updates_<YYMMDD>.xlsx` (YYMMDD = MAX(update_date) in the pre-write file). Only the Updates MASTER is rewritten; the Register MASTER is already correct from step 2. Pass `--no-archive` to skip archival in rare cases.
5. **Owner** refreshes the PBIP in Power BI Desktop. New rows appear on Page 1 Risk Activity, Page 2 Recent Risk Updates, and (via active M:1 relationship) the Page 3 drillthrough UpdatesHistory table.

The script is idempotent against the latest MASTER state: a second run with no further Register edits produces zero appends. Bootstrap calibration (§c) handles the cold-start case where the script's simple year-inference disagrees with Phase 2 regen's calibrated years on historical entries.

---

## b) Parse regex

```python
DATE_LEADER = re.compile(r"(?P<m>\d{1,2})/(?P<d>\d{1,2})\s*-\s*", re.MULTILINE)
```

Same shape used by `scripts/audit_inspect.py` (Phase 1) and `scripts/regenerate_updates.py` (Phase 2). It matches `M/D -` markers (any whitespace around the hyphen). The body of each entry is the substring from the match end to the next match start (or end of cell). Bodies are stripped of leading/trailing whitespace.

Tolerances:
- Out-of-range M/D (e.g. `13/45 - ...`): logged as WARNING, entry skipped, parsing continues.
- Empty body (e.g. two consecutive leaders with nothing between): logged, skipped.
- Non-string cell value (e.g. None): treated as zero entries.

The parser is the same shape that originally produced the 127 rows in `Tonnelle_Risk_Updates_MASTER.xlsx`, so what was parseable then remains parseable now. The audit found no malformed entries in the current Register; the malformed-tolerance path exists as a safety net for future edits.

---

## c) Matching key (dedupe)

```python
def fingerprint(risk_id, d, note):
    return (risk_id, d.isoformat(), normalize(note)[:120])
```

Exact-date. Same `risk_id` + same FULL date + same first 120 chars of normalized note = same event. `normalize` collapses internal whitespace, lowercases, and strips trailing punctuation (`. , ; : ! ?`).

Distinct dated entries each produce their own Updates row. Multiple entries on the same day with different wording all append. Same M/D in different years with **different** wording both append.

### Bootstrap calibration (cold-start handling)

A literal exact-date dedupe would re-append every historical entry on the first run, because Phase 2 regen anchored years via calibration (an entry parsed as `9/12` was anchored to 2025 if an existing Updates row was dated 2025-09-12) while this script uses the simple `today.year + 6mo-future` rule (`9/12` infers to 2026 in May). The cold-start dry-run would have proposed ~30 false-positive duplicates.

To bridge this, the script builds a `(risk_id, M, D) → {historical years seen}` map from existing Updates rows. Before declaring a log entry new, it tries the exact-date fingerprint AND tries the fingerprint at each historical year known for that risk's M/D. Match at any historical year ⇒ already represented ⇒ skip.

The inserted row's date is unaffected: new entries still get the forward-year via `infer_year`. The calibration only widens the dedupe lookup. Confirmed by cold-start dry-run: `Rows to append: 0` against the live MASTER.

### What the dedupe handles cleanly

- Cold start against the Phase 2-regenerated MASTER → 0 appends (calibration finds every historical row).
- Re-running with no Register changes after a write → 0 appends (idempotent).
- Light wording edits to a previously-recorded entry (whitespace, case, punctuation) → absorbed by `normalize` within the 120-char prefix; no false append.
- Multiple entries on the same day with different wording → all append as separate rows.
- Same M/D in different years with **different** wording → both rows present.

### What it does NOT handle (limits)

- Same M/D in different years with **identical** wording past the 120-char prefix → second occurrence skipped. The calibration cannot distinguish "recurring annual note worded identically" from "re-statement of the existing entry". To force the second entry, phrase it slightly differently.
- Wholesale rewrite of an existing entry's wording past the 120-char prefix → produces a duplicate row (the rewritten text doesn't fingerprint-match any historical year's row). Manually delete the obsolete row.
- Two identical-text entries typed on the same calendar day → second one skipped (typo case).
- Re-ordering entries inside the `mitigation_log` cell → unaffected; parse order doesn't enter the fingerprint.

---

## d) Year inference

Per the phase-12 prompt rule, with no calibration against existing Updates rows:

1. If `--year-override YYYY` is set, use that year (validated against month/day; falls through to skip if `date(year, m, d)` raises).
2. Otherwise default to `today.year`. Compute `candidate = date(today.year, m, d)`. If `(candidate - today).days > 183` (~6 months), use `today.year - 1`.
3. If `date(...)` raises (e.g. Feb 30, Feb 29 in a non-leap year), log a warning and skip the entry.

Examples with `today = 2026-05-23`:

| M/D | Inferred year | Reason |
|---|---|---|
| 5/22 | 2026 | Yesterday, in current year window |
| 5/23 | 2026 | Today |
| 5/25 | 2026 | +2 days, in current year window |
| 1/5 | 2026 | -138 days, past, in current year window |
| 11/15 | 2026 | +176 days, ≤183, stays in current year |
| 12/1 | 2025 | +192 days, >183, rolls back to prior year |
| 9/12 | 2026 | +112 days, ≤183 (an actual Sep 2025 entry in mitigation_log will be appended as 2026 under exact-date dedupe; see §c cold-start limit) |
| 2/30 | (skipped) | Invalid calendar date for any year |

The forward use case (RM logs "today's news") is the design center: such entries always resolve to the current year correctly. The boundary case (RM backfills an event from 6+ months ago into mitigation_log today) requires `--year-override` to override; the year inference rule alone cannot distinguish a forward-dated entry from a backfill within the 6-month window. The discrepancy flag (§j) surfaces these for review.

The 6-month threshold is documented as the phase-12 rule and is not adjustable from the CLI.

---

## e) Author inference

Default: the appended row's `author` is the `risk_coordinator` value from the Register row for that risk. Matches the Phase 2 regeneration convention (every existing Updates row's author is its risk's current coordinator).

Override: `--author "Name"` forces that exact string as the author for ALL appended rows in this run. Useful when a non-coordinator (the PMC, the Chief Engineer) logged the update.

Fallback: if a risk has a blank `risk_coordinator` AND no `--author` is passed, the row is written with `author = "(unassigned)"`. Same sentinel used by `regenerate_updates.py`.

---

## f) CLI surface

```text
$ python scripts/append_updates.py --help
usage: append_updates.py [-h] [--register REGISTER] [--updates UPDATES]
                         [--dry-run] [--no-archive] [--archive-dir DIR]
                         [--year-override YYYY] [--author NAME]
                         [--today YYYY-MM-DD] [-v]

Append new dated mitigation_log entries from Risk_Register to Risk_Updates.
Idempotent: re-runs append nothing if no changes exist. Recommended workflow:
--dry-run first, then re-run (auto-archives the previous MASTER to /archive/
unless --no-archive).

options:
  -h, --help            show this help message and exit
  --register REGISTER   Risk_Register .xlsx (default:
                        source_data/Tonnelle_Risk_Register_MASTER.xlsx)
  --updates UPDATES     Risk_Updates .xlsx (default:
                        source_data/Tonnelle_Risk_Updates_MASTER.xlsx)
  --dry-run             Print proposed appends; do not write; do not archive.
  --no-archive          Skip the auto-archive step. By default, before
                        writing, the existing Updates MASTER is copied to
                        <archive>/<base>_<YYMMDD>.xlsx where YYMMDD =
                        MAX(update_date) in the file. Second append in the
                        same day appends _HHMMSS.
  --archive-dir DIR     Archive folder (default: archive)
  --year-override YYYY  Force YYYY for ALL parsed entries instead of the
                        current-year + 6-month-future rule.
  --author NAME         Override author for ALL appended rows (default:
                        risk_coordinator from Register).
  --today YYYY-MM-DD    Override today's date for year inference (testing
                        aid).
  -v, --verbose         Verbose logging (DEBUG level).
```

Exit codes: `0` success (any number of appends including zero), `2` input file missing or `--today` malformed.

---

## g) Failure modes

| Condition | Behavior |
|---|---|
| `--dry-run` | Prints proposed rows; no file written; no archive created. |
| Default (no flag) | Before write: copy existing Updates MASTER to `archive/<base>_<YYMMDD>.xlsx`, YYMMDD = MAX(update_date) in pre-write file. Same-day re-run appends `_HHMMSS` to disambiguate. Rollback = copy the archive back over the MASTER. |
| `--no-archive` | Skip archival; write straight into Updates MASTER. Use when the archive is unnecessary (e.g., scripted test runs). |
| Archive copy fails (permissions, disk full) | ERROR logged; exit 2; the Updates MASTER is NOT modified. Either fix the archive folder or pass `--no-archive` if you accept the risk. |
| Malformed log entry (out-of-range M/D, empty body) | WARNING logged; entry skipped; parsing continues for the rest of the cell. |
| Invalid calendar date after year inference (Feb 30, Feb 29 in non-leap, etc.) | WARNING logged; entry skipped. |
| Missing Register or Updates input file | ERROR logged; exit 2; nothing written. |
| Risk with blank `risk_coordinator` and no `--author` | Row written with `author = "(unassigned)"`. |
| `--year-override` invalid for an entry (e.g. override=2025 + M/D=2/29) | WARNING logged; that entry skipped; others unaffected. |
| Run with zero proposed appends | Prints `Nothing to append; Risk_Updates is in sync.`; no write; exit 0. |
| Proposed-append date >45d from today | Row printed with `[FLAG]`; `DISCREPANCY:` summary at end. Non-blocking; the write still happens unless `--dry-run`. See §h. |

The script never overwrites the Register or any file outside `source_data/`.

---

## h) Discrepancy flagging

Each proposed append row whose inferred date is more than **45 days** (~1.5 months) from `today` (in either direction) prints with a `[FLAG]` marker, and a `DISCREPANCY:` summary block lists each flagged row at the end of the dry-run output. Non-blocking; the script still proceeds to write if `--dry-run` is not set.

Purpose: catches RM-side typos and forgotten backdated entries. The year inference rule (§d) is forward-looking — it can't distinguish "RM typed 11/15 meaning May 15" from "RM logged a real Nov entry". When a parsed entry's date lands far from today, the flag prompts the owner to verify before committing.

Examples with `today = 2026-05-23`, threshold = 45 days:

| Entry in mitigation_log | Inferred date | Days from today | Flagged? | Likely meaning |
|---|---|---|---|---|
| `5/22 - ...` | 2026-05-22 | -1 | no | Recent, fine |
| `4/10 - ...` | 2026-04-10 | -43 | no | Just inside window |
| `3/15 - ...` | 2026-03-15 | -69 | **yes** | RM probably forgot to log earlier; verify year |
| `11/15 - ...` | 2026-11-15 | +176 | **yes** | Could be typo of 5/15; could be legit future entry; verify |
| `12/20 - ...` (today=Jan 5) | 2025-12-20 | -16 | no | Jan/Dec rollover handled by year rule |

The flag's only effect is on stdout. The row is still appended unless `--dry-run` is set.

If a flagged row turns out to have the wrong year, the owner has two recovery paths:
1. Edit the offending `mitigation_log` entry in MASTER Register to spell out the right M/D (e.g. correct a typo), re-run.
2. Run with `--year-override YYYY` to force a specific year for ALL parsed entries this run. Useful for a one-time backfill batch.

---

## i) Self-verification log

All checks run from project root, `2026-05-23`.

**Static compile**
```
python -m py_compile scripts/append_updates.py scripts/test_append_updates.py
# OK
```

**Pyflakes**
```
python -m pyflakes scripts/append_updates.py scripts/test_append_updates.py
# (no findings)
```

**Pytest** (32 cases)

```
scripts/test_append_updates.py::test_parse_log_two_entries PASSED
scripts/test_append_updates.py::test_parse_log_empty_or_none PASSED
scripts/test_append_updates.py::test_parse_log_no_dated_markers PASSED
scripts/test_append_updates.py::test_parse_log_malformed_does_not_crash PASSED
scripts/test_append_updates.py::test_parse_log_empty_body_logged_and_skipped PASSED
scripts/test_append_updates.py::test_infer_year_default_current_year PASSED
scripts/test_append_updates.py::test_infer_year_more_than_six_months_future_rolls_back PASSED
scripts/test_append_updates.py::test_infer_year_just_under_six_months_stays_current PASSED
scripts/test_append_updates.py::test_infer_year_past_date_stays_current PASSED
scripts/test_append_updates.py::test_infer_year_override_wins PASSED
scripts/test_append_updates.py::test_infer_year_override_invalid_returns_none PASSED
scripts/test_append_updates.py::test_infer_year_feb29_non_leap_returns_none PASSED
scripts/test_append_updates.py::test_compute_appends_detects_one_new PASSED
scripts/test_append_updates.py::test_compute_appends_idempotent PASSED
scripts/test_append_updates.py::test_compute_appends_author_override PASSED
scripts/test_append_updates.py::test_compute_appends_year_override PASSED
scripts/test_append_updates.py::test_compute_appends_minor_edit_does_not_duplicate PASSED
scripts/test_append_updates.py::test_compute_appends_same_md_different_year_different_text_appends PASSED
scripts/test_append_updates.py::test_compute_appends_cold_start_calibration PASSED
scripts/test_append_updates.py::test_compute_appends_multiple_entries_same_day_all_append PASSED
scripts/test_append_updates.py::test_compute_appends_jan_dec_rollover PASSED
scripts/test_append_updates.py::test_compute_appends_skips_invalid_date_silently PASSED
scripts/test_append_updates.py::test_dry_run_does_not_write PASSED
scripts/test_append_updates.py::test_real_write_appends_rows PASSED
scripts/test_append_updates.py::test_archive_dated_by_last_update_date PASSED
scripts/test_append_updates.py::test_archive_same_day_disambiguates_with_hhmmss PASSED
scripts/test_append_updates.py::test_dry_run_does_not_archive PASSED
scripts/test_append_updates.py::test_no_archive_flag_skips_archive PASSED
scripts/test_append_updates.py::test_no_changes_returns_zero_and_writes_nothing PASSED
scripts/test_append_updates.py::test_discrepancy_flag_surfaces_backdated_entry PASSED
scripts/test_append_updates.py::test_discrepancy_flag_skipped_when_within_window PASSED
scripts/test_append_updates.py::test_malformed_in_workbook_does_not_crash PASSED

============================= 32 passed in 0.84s ==============================
```

**Dry-run on live MASTER files (cold start)**

```
$ python scripts/append_updates.py --dry-run --today 2026-05-23
Existing Updates rows: 127
Rows to append:        0

Nothing to append; Risk_Updates is in sync.
```

Confirms bootstrap calibration. Without it, this dry-run would have surfaced 30 false-positive appends from Sep-Nov 2025 entries whose Phase 2 calibrated year disagrees with the simple-rule inference. See §c "Bootstrap calibration".

**Idempotency** (back-to-back dry-runs on MASTER)

```
diff dryrun_a.txt dryrun_b.txt
# (empty)
IDEMPOTENT
```

**Synthetic-change dry-run**

Synthetic edit: three entries appended to TONN-CON.01's `mitigation_log` (two on 5/22, one on 5/23) and one to TONN-CON.37's (5/22). Same workbook saved as `.tmp/synthetic_register.xlsx`. Live Updates unchanged.

```
$ python scripts/append_updates.py --register .tmp/synthetic_register.xlsx \
                                   --dry-run --today 2026-05-23
Existing Updates rows: 127
Rows to append:        4

update_id  risk_id       date        author                note
--------------------------------------------------------------------------------------------------------------
      128  TONN-CON.01   2026-05-22  Anton Benedict        Site walk completed; no further obstructions found.
      129  TONN-CON.01   2026-05-22  Anton Benedict        Followup; signoff in progress.
      130  TONN-CON.01   2026-05-23  Anton Benedict        Final excavation signoff received.
      131  TONN-CON.37   2026-05-22  Justin Hwang          Reforecast submitted to GDC.

--dry-run: no file written.
```

Detection: 4-of-4 including the two same-day 5/22 entries on TONN-CON.01. Identifiers continue from `128 = 127 + 1`. Year correctly inferred to 2026. Authors correctly drawn from each risk's coordinator (Anton Benedict for TONN-CON.01, Justin Hwang for TONN-CON.37).

---

## j) Limits the user must know

1. **Year inference is forward-looking only.** Backfilling an entry from 6+ months ago (e.g. typing `11/15 - <event from Nov 2025>` today on 2026-05-23) infers `2026-11-15`. The simple rule cannot distinguish a forward-dated entry from a backfill within the 6-month window. Use `--year-override 2025` to correct, or edit the Updates row manually after the run. Inspect dry-run output before committing.
2. **Same M/D + identical wording across years collapses.** Bootstrap calibration treats `5/22 - annual safety walk` typed today as already represented if the same wording exists at `2025-05-22`. To force the new-year row, phrase the new note slightly differently.
3. **Same-day same-text double entries collapse.** Two entries on the same risk + same full date + same first-120-char wording (typically a typo case) will collapse to one row. Same-day entries with different wording are independent and both append.
4. **Wholesale rewrites past the 120-char prefix create a duplicate row.** If you edit an existing entry's wording such that the first 120 normalized chars change, the script treats it as a new entry. Inspect dry-run output and either accept the duplicate (then delete the obsolete row) or revert the wording.
5. **The Updates file is rewritten on every successful append.** openpyxl rewrites the whole `.xlsx`. The `update_date` `yyyy-mm-dd` number format is preserved; any out-of-schema formatting (cell fills, borders) on the original file would be lost. The Updates file currently carries no such formatting.
6. **The author override is per-run, not per-row.** Either every appended row in a run gets the override author, or none does. For multiple risks updated by different non-coordinator authors: accept the coordinator default and edit afterward, or run the script in multiple targeted passes.
7. **The script does not touch the Register.** It only reads it. There is no Register write path; safety-by-design.
8. **The script does not validate the Phase 1 schema beyond what it needs.** It reads `risk_id`, `risk_coordinator`, `mitigation_log` from the Register and `update_id, risk_id, update_date, update_year, author, note` from Updates. If a schema migration ever adds or renames columns, this script needs updating in lockstep.
