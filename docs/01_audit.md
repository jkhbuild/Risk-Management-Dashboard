# 01 — Data audit and reconciliation

Phase 1 discovery, prepared 2026-05-22. Source: `scripts/audit_inspect.py` against `source_data/Tonnelle_Risk_Register_260519.xlsx` and `source_data/Tonnelle_Risk_Updates_260519.xlsx`. Discovery only; no schema decisions made here.

---

## a) Risk_Register state

### Inventory

- File: `Tonnelle_Risk_Register_260519.xlsx`, tab `Risk_Register`.
- 37 populated data rows (template ships with 30; user added rows TONN-CON.31 through TONN-CON.37).
- 19 columns, matching the turnover spec verbatim:

  `risk_id, project_id, source_ref, status, risk_category, risk_title, risk_type, probability_score, cost_impact_score, schedule_impact_score, risk_score_cost, risk_score_schedule, risk_score_overall, risk_level, risk_entity, risk_coordinator, mitigation_status, next_review_date, mitigation_log`

### Score and band integrity

| Check | Result |
|---|---|
| `risk_score_overall` equals `probability_score * MAX(cost_impact_score, schedule_impact_score)` | 0 mismatches across 37 rows |
| `risk_level` equals expected band (High >= 15, Medium 8-14, Low 1-7) | 0 mismatches across 37 rows |

Stored formulas are intact.

### Distributions

**risk_level**

| Level | Count |
|---|---|
| High | 12 |
| Medium | 10 |
| Low | 15 |

**risk_category**

| Category | Count |
|---|---|
| Construction | 15 |
| Design Change | 7 |
| Field Condition | 5 |
| Safety | 5 |
| Financial | 2 |
| Political | 2 |
| Environmental | 1 |

**risk_entity**

| Entity | Count |
|---|---|
| CM | 11 |
| Contractor | 9 |
| Designer | 7 |
| GDC | 6 |
| Shared | 4 |

**risk_coordinator**

| Coordinator | Count |
|---|---|
| Anton Benedict | 9 |
| Eric Kautz | 8 |
| Justin Hwang | 7 |
| Joshua Giron | 6 |
| Yaseen Arshev | 4 |
| Vin Pallypis | 3 |

**status**: 37 of 37 rows = "Open". No `Closed`, `Monitoring`, or `Realized` values present. This contradicts the mitigation_log content for several risks (multiple risks have terminal log entries such as "risk closed" or "Differing site condition documented; risk closed"). The `status` column appears not to have been maintained as the project progressed. Flagged in section (e).

### Locked-list reconciliation

The turnover spec's locked sets are:
- Categories: Construction, Field Condition, Design Change, Safety, Environmental, Political (6 values).
- Entities: GDC, CM, Contractor, Shared (4 values).

The workbook's `Lookups` tab carries:
- `category_list`: 7 values, adds **Financial**.
- `entity_list`: 5 values, adds **Designer**.

Data in `Risk_Register` exactly matches `Lookups` (no values in data that are missing from Lookups). Divergence is between Lookups + data on one side and the turnover-locked spec on the other:

| Field | In data not in locked spec | Affected rows |
|---|---|---|
| risk_category | `Financial` | 2 |
| risk_entity | `Designer` | 7 |

Both additions appear deliberate (added to the validation lists in `Lookups`) and used in real risk rows. Flagged in section (e).

### Blank required-field audit

| Field | Blanks |
|---|---|
| status | 0 |
| risk_coordinator | 0 |
| probability_score | 0 |
| cost_impact_score | 0 |
| schedule_impact_score | 0 |

All required input fields populated.

### next_review_date

- Excel-serial decoding succeeded (openpyxl returned native dates).
- 34 of 37 rows populated; 3 blank.
- Min = max = **2026-05-22** (today's date per CLAUDE.md).

Every populated row carries the same date, today. This is almost certainly a template default or a `=TODAY()` formula that has been allowed to resolve uniformly across all rows. No row falls outside a one-year-back, two-years-forward sanity window, but the column is providing no real signal. Flagged in section (e).

---

## b) Risk_Updates state

- File: `Tonnelle_Risk_Updates_260519.xlsx`, single sheet `Risk_Updates`.
- 92 populated data rows.
- 6 columns: `update_id, risk_id, update_date, update_year, author, note`.
- `update_date` Excel-serial decoding succeeded.

### Date range

| | |
|---|---|
| Min | 2025-09-08 |
| Max | 2026-05-12 |
| Span | ~8 months |

### Year distribution

| Source | 2025 | 2026 |
|---|---|---|
| Stored `update_year` column | 46 | 46 |
| Derived from `update_date.year` | 46 | 46 |

The stored `update_year` column matches the derived year on every row. Year disambiguation has been correctly applied (per the turnover spec, the splitter resolved short `M/D` markers like `1/13` to the right calendar year).

### Orphans (Updates rows whose risk_id is not in Register)

None. All 92 Updates rows reference risk_ids that exist in `Risk_Register`.

### Zero-coverage (Register risks with no Updates row)

Seven risks: **TONN-CON.31, TONN-CON.32, TONN-CON.33, TONN-CON.34, TONN-CON.35, TONN-CON.36, TONN-CON.37**.

These are the seven risks the user added beyond the template's first 30. The mitigation_log on each of these risks IS populated (see section (c)), so the absence of Updates rows means the Updates file was generated before these risks were added (or before their mitigation_log entries were written) and has not been regenerated since.

---

## c) Cross-file reconciliation — `Register.mitigation_log` vs `Updates.note`

### Parsing approach

For each Register row, the `mitigation_log` cell was split on `M/D -` date markers (regex `(\d{1,2}/\d{1,2})\s*-\s*`). Each parsed entry was paired against any `Updates` rows for the same `risk_id` whose `update_date` falls on the same calendar month/day. Note text was compared with case + whitespace + trailing-punctuation normalization (script `normalize()` helper).

### Counts

| Bucket | Count |
|---|---|
| Risks with at least one dated mitigation_log entry | 37 of 37 |
| Total mitigation_log dated entries parsed | 121 |
| Exact text match (after normalization) | 83 |
| Same risk + date, different text (material drift) | 3 |
| Log entry with no corresponding Updates row | 35 |
| Updates row with no corresponding log entry | 6 |

### Material drift (3 cases)

| risk_id | Date | mitigation_log | Updates.note |
|---|---|---|---|
| TONN-CON.02 | 12/8 | Product recovery underway; volume being quantified. | Product recovery underway; cost impact being quantified |
| TONN-CON.03 | 11/2 | Plates re-bedded and pinned; movement reduced. | Plates re-bedded and pinned; movement eliminated |
| TONN-CON.10 | 2/20 | Time extension request submitted for access delays. | Schedule impact realized; time extension request submitted |

Each case is a genuine semantic difference, not punctuation. In each case the Register's `mitigation_log` could have been edited after Updates was generated, OR the Updates author phrased the same event differently.

### Log-only (35 cases, sample of 5)

| risk_id | M/D | mitigation_log |
|---|---|---|
| TONN-CON.02 | 3/14 | Recovery continuing; extent larger than first estimated. |
| TONN-CON.02 | 5/6 | Remediation ongoing; cost exposure under review. |
| TONN-CON.03 | 2/10 | Periodic reinspection added to weekly walk. |
| TONN-CON.03 | 4/28 | No movement at latest inspection; monitoring continues. |
| TONN-CON.04 | 2/15 | Survey readings stable. |

The dates of log-only entries are heavily clustered in 2026 (Feb to May), after the Updates file's apparent last regeneration. Combined with the seven zero-coverage risks (TONN-CON.31-37), this strongly suggests `Risk_Updates` is stale relative to `mitigation_log`.

### Updates-only (6 cases, full list)

| risk_id | update_date | Updates.note |
|---|---|---|
| TONN-CON.02 | 2026-02-15 | Remediation cost executed via change order; risk realized |
| TONN-CON.03 | 2025-11-20 | Reinspected with no movement; risk closed |
| TONN-CON.04 | 2025-12-12 | No further settlement observed; risk closed |
| TONN-CON.06 | 2025-12-01 | Cleared by site safety; risk closed |
| TONN-CON.07 | 2025-12-10 | Schedule recovered to baseline; risk closed |
| TONN-CON.10 | (varies) | (see drift row above) |

All Updates-only rows describe terminal events ("risk closed", "risk realized"). These either never made it into the mitigation_log column or were trimmed from it later. They are consistent with the section (a) finding that `status` is uniformly "Open" despite resolution events being recorded.

### Hypothesis on lead source

The turnover spec is explicit that `Risk_Register.mitigation_log` is the source and `Risk_Updates` is derived ("USER PROVIDES filled register with mitigation_log"; "NEW CHAT GENERATES separate Risk_Updates file by splitting the mitigation_log column"). The data is consistent with that: 83 of 121 log entries match Updates rows exactly; the 35 log-only entries are all recent and the 7 zero-coverage risks are all post-template additions. The 3 material drifts and 6 Updates-only resolution events are the only places Updates diverges from log, and they look like:
- Drifts: minor in-place edits to mitigation_log after the split.
- Updates-only: closing events that the splitter created but were not echoed back into mitigation_log when the user updated the register.

**Lead source: `Risk_Register.mitigation_log`.** Treat `Risk_Updates` as a derived view that needs regeneration before Phase 2 builds visuals on top of it. The 6 Updates-only resolution events should be reviewed before discarding; they may carry information the log no longer carries.

---

## d) Risk Score Trend feasibility (the open design question)

The mockup's Page 1 shows "Risk Score Trend Over Time" as a line chart of avg overall score by month, fed from `Risk_Updates`. The underlying problem:

- `Risk_Register` stores only the **current** P, C, S scores (one row per risk, scores are the latest values, not historical).
- `Risk_Updates` stores **events** (one row per dated note), not score deltas. No historical score column exists in either file.

With the schema as it stands, a line chart of "score over time" cannot show how scores actually evolved. The available interpretations:

1. **Avg score of risks that had any update in month M.** For each month, take all risks with at least one Updates row in that month and average their CURRENT `risk_score_overall`. This is what the mockup chart is most likely producing today. Conceptually weak: the "score" displayed for September 2025 is actually the May 2026 score of risks that happened to be updated in September.
2. **Count of updates per month.** A volume chart, not a score chart. Honest but loses the "score" framing.
3. **Cumulative risks identified by update_date.** Treat each risk's earliest `update_date` as its identification date and plot the cumulative count over time. A discovery-velocity chart, not a score chart.
4. **Something else** (e.g., capture historical scores as a new column on `Risk_Updates`; require the user to log P/C/S whenever an update is filed; abandon the chart in favor of a snapshot).

This is the single biggest open question for Phase 2. The chart cannot be implemented faithfully without picking one interpretation, and (1) is misleading despite matching the mockup. Resolution required before Phase 2.

---

## e) Open questions (must resolve before Phase 2)

1. **Locked-list extensions.** The data uses `Financial` (category) and `Designer` (entity), both in the workbook's `Lookups` tab but neither in the turnover-locked spec. Three choices: (a) accept the extensions and update the locked spec; (b) refile the 2 Financial risks under another category and the 7 Designer risks under another entity; (c) some hybrid (e.g., accept Designer, refile Financial). Decision blocks model design (relationships, slicer values) and the Page 1 stacked-bar visual.
2. **Status column is stale.** All 37 risks are marked "Open" despite multiple risks having terminal mitigation_log entries and Updates-only resolution events. Decide whether the `status` field is authoritative going forward (and needs backfilling), or whether the dashboard should derive an "Effective Status" from terminal log/Updates language (fragile) or be silent on status until backfilled.
3. **Risk_Updates is stale relative to mitigation_log.** 35 dated log entries (all clustered Feb-May 2026) and 7 user-added risks have no Updates representation. Phase 2 should regenerate `Risk_Updates` from current `mitigation_log` before connecting it to Power BI. Also decide whether to retain the 6 Updates-only resolution events that never made it back into the log.
4. **Three material text drifts** between log and Updates (TONN-CON.02 12/8, TONN-CON.03 11/2, TONN-CON.10 2/20). Pick one canonical wording per pair, or accept the regeneration in (3) overwrites the Updates wording with the current log wording.
5. **next_review_date column is non-signal.** Every populated row carries 2026-05-22 (today). Decide whether to populate real per-risk review dates, hide the field on the dashboard, or replace it with "days since last update" derived from Updates.
6. **Risk Score Trend Over Time chart interpretation** (section (d)). Pick one of the four candidates, or change the schema to capture historical scores (and thereby change the user's stated "no Power BI editing" workflow).
