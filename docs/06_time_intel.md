# 06. Time-intelligence measures

Phase 6 deliverable, prepared 2026-05-23. Skill loaded: `power-bi-dax-optimization`.

**Inputs:**
- `docs/03_design_locked.md` §b TimeIntel measure signatures; §d Page 1 visual #9 line-chart binding ("Risk Activity Over Time", X = `dim_Date[YearMonth]` continuous, Y = `[Updates Count]`).
- `docs/05_semantic_model.md` for the `_Measures` table pattern and the Counts/Scores precedent.
- Applied TMDL in `pbip/Tonnelle_Risk.SemanticModel/` (Phase 5 state, 10 measures pre-edit; 12 measures post-edit minus the Display 3 deferred to Phase 7).
- Source baselines computed against `source_data/Tonnelle_Risk_Updates_MASTER.xlsx` and `source_data/Tonnelle_Risk_Register_MASTER.xlsx`.

Scope: the 2 TimeIntel measures (`Updates Count`, `Days Since Last Update`) and the verification of date-table wiring that drives them. The Display folder (3 measures, Phase 7) and any further time-intel patterns are out of scope.

Locked trend-chart interpretation (per Phase 2 §c-Q4 lock, restated in 03 §d Page 1 visual #9 line 253): **count of updates per month**, not average score, not cumulative risk count. Title clarifies: "Risk Activity Over Time (updates per month)".

---

## a) Files changed

| File | Change |
|---|---|
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/_Measures.tmdl` | Appended 2 measures in `TimeIntel` display folder: `Updates Count`, `Days Since Last Update`. Total measures in file: 10 (4 Counts + 4 Scores + 2 TimeIntel). |
| `scripts/verify_phase6_measures.py` | **New file.** Computes expected monthly `[Updates Count]` series from the Updates source, plus per-risk `[Days Since Last Update]` summary. |

No model-structure changes. The active relationship `Risk_Updates[update_date] → dim_Date[Date]` and `dim_Date` date-table marking are Phase 4/5 deliverables and verified intact in §d below.

---

## b) Measure definitions

Both measures live in `_Measures.tmdl` under `displayFolder: TimeIntel`. Each carries a TMDL `///` description naming the intent and the consuming visual.

### `[Updates Count]`

```dax
Updates Count = COUNTROWS ( Risk_Updates )
```

- **Format:** `0` (integer).
- **Display folder:** `TimeIntel`.
- **Intent (03 §b):** Count of `Risk_Updates` rows in current filter context (date and otherwise).
- **Visual binding:** Page 1 visual #9 "Risk Activity Over Time", Y-axis. Page 2 visual #7 "Recent Risk Updates" implicit total (not displayed but driving the visual-level Top N 20).
- **How filter context reaches it:** the active M:1 relationship `Risk_Updates[update_date] → dim_Date[Date]` propagates `dim_Date[YearMonth]` filters from the X-axis down to `Risk_Updates`. Any Page 1 filter-pane slicers on `risk_category` / `risk_coordinator` propagate through `Risk_Updates[risk_id] → Risk_Register[risk_id]` (also M:1, single-direction, but the implicit `RELATED` chain works because filters always flow toward the many side via the natural propagation graph in this direction; the chain here is Register → Updates, which is the active direction). The Page 1 report-level filter `status = "Open"` is currently a no-op (status hidden, all rows "Open") and propagates the same way.

### `[Days Since Last Update]`

```dax
Days Since Last Update =
VAR LastUpdate = MAX ( Risk_Updates[update_date] )
RETURN
    IF (
        NOT ISBLANK ( LastUpdate ),
        DATEDIFF ( LastUpdate, TODAY (), DAY )
    )
```

- **Format:** `0` (integer; Page 2 column carries the unit suffix " d" per 03 §d Page 2 visual #5 line 267).
- **Display folder:** `TimeIntel`.
- **Intent (03 §b):** Days between today and the most-recent `update_date` for the current risk-row context; BLANK if no updates exist for the risk.
- **Visual binding:** Page 2 Top Risks table column "Days Since Last Update"; Page 3 meta strip (could be added, not in locked Page 3 layout but no obstacle).
- **How filter context reaches it:** the active M:1 `Risk_Updates → Risk_Register` (on `risk_id`) means each row in the Page 2 Top Risks table (one per Register risk) propagates a single-`risk_id` filter to `Risk_Updates`. `MAX(Risk_Updates[update_date])` then returns the latest update for that risk. When no Updates rows match (a risk newly added to the Register before its first log entry), `MAX` returns BLANK and the `IF` short-circuits to BLANK via the omitted else branch.

---

## c) Optimization rationale (data-goblin heuristics)

For both measures, the analysis framework from the loaded `power-bi-dax-optimization` skill is applied below.

### `[Updates Count]`

**Performance analysis.**
- `COUNTROWS` is the storage-engine-native row count. No row context, no iteration, no expression-per-row evaluation. Pure VertiPaq scan.
- No `CALCULATE` wrapper needed because filter context from `dim_Date[YearMonth]` propagates through the active relationship by default. Adding `CALCULATE` would introduce a no-op context transition.
- No `DISTINCTCOUNT` alternative is needed: the visual axis is `dim_Date[YearMonth]` and the value is "rows", not "distinct risks". (If the chart were ever rebound to "distinct risks updated per month" we would switch to `DISTINCTCOUNT(Risk_Updates[risk_id])`. Not the locked design.)

**Readability assessment.**
- Single-line measure; the TMDL `///` description carries the business intent. Variable-free is the right call when the expression is one storage-engine call.

**Best-practice compliance.**
- `COUNTROWS` over `COUNT(column)`: ✓ (`COUNT` requires a non-blank column predicate; `COUNTROWS` is the canonical row counter).
- No implicit measures: ✓ (explicit measure in `_Measures`).
- Returns BLANK on empty filter context: ✓. For the locked continuous-axis chart (months with zero updates shown per 03 §d line 253), BLANK on the line produces a gap rather than a zero. **Current data has no zero-update months in [2025-09, 2026-05] (verified in §d), so this is not observable in current data.** If a future month genuinely has zero updates and the user wants a flat-zero line rather than a gap, change the measure to `COUNTROWS ( Risk_Updates ) + 0`. Deferred unless Phase 9 visual review flags it.

**Antipattern scan.**
- No SUMX over fact table: ✓ (no iterator).
- No nested CALCULATE: ✓ (no CALCULATE at all).
- No unnecessary ALL / REMOVEFILTERS: ✓ (slicers must propagate; ALL would break Page 1 filter-pane behavior).

No optimization changes applied; the measure is already in its minimal form.

### `[Days Since Last Update]`

**Performance analysis.**
- `MAX(Risk_Updates[update_date])` is a storage-engine scalar aggregation, not an iterator. Evaluated once per filter context, not per row of `Risk_Updates`.
- `TODAY()` is constant within a query (cached for the query lifetime). Stored in implicit query context; no further optimization possible.
- `DATEDIFF(LastUpdate, TODAY(), DAY)` is a scalar arithmetic call.
- `VAR LastUpdate` ensures `MAX` is evaluated once and reused in both the `ISBLANK` check and the `DATEDIFF` call. Without the variable, the storage engine could reasonably fuse the two calls anyway, but the variable removes the dependency on optimizer behavior and aligns with data-goblin "variable usage opportunities."

**Readability assessment.**
- VAR/RETURN structure with a meaningful variable name (`LastUpdate`).
- `NOT ISBLANK ( LastUpdate )` reads naturally as the guard precondition.
- `IF` with no else branch returns BLANK by default — the documented DAX idiom for "compute or BLANK."

**Best-practice compliance.**
- `ISBLANK` check before date arithmetic: ✓. Without it, `DATEDIFF(BLANK(), TODAY(), DAY)` would return a very large positive integer (BLANK coerces to date 1899-12-30 in DAX), which would render as a misleading "huge stale" value on rows with no updates.
- `DATEDIFF` over `TODAY() - LastUpdate` subtraction: ✓. Explicit unit (`DAY`) over arithmetic; documented preferred form.
- No `CALCULATE`: ✓. The Page 2 table visual creates per-row filter context via implicit `CALCULATE` at the visual layer; adding another `CALCULATE` here would do nothing.

**Antipattern scan.**
- No SUMX / FILTER / iterator: ✓ (scalar MAX).
- No nested CALCULATE: ✓.
- No CALCULATE inside iterator: ✓ (no iterator).
- No ALL / REMOVEFILTERS: ✓.

No deferred optimizations.

---

## d) Self-verification log

### 1. Date table coverage

| Quantity | Value |
|---|---|
| `MIN(Risk_Updates[update_date])` | 2025-09-08 |
| `MAX(Risk_Updates[update_date])` | 2026-05-12 |
| Active range span | 2025-09 to 2026-05 (9 months) |
| `dim_Date` partition source (03 §a, applied in `dim_Date.tmdl`) | `CALENDAR(DATE(YEAR(MIN(update_date)),1,1), DATE(YEAR(MAX(update_date)),12,31))` |
| Resolved `dim_Date` span | 2025-01-01 to 2026-12-31 (730 days) |
| Buffer on each side | 8 months pre, 7 months post (full-calendar-year padding per 03 §a) |

Buffer is generous and exceeds any time-intel measure's pre/post-period needs (no LAG/LEAD or year-over-year functions in the locked Phase 6 measure set).

### 2. Date table marking

Grep `pbip/Tonnelle_Risk.SemanticModel/definition/tables/dim_Date.tmdl`:
- Line 3: `dataCategory: Time` on the table.
- Line 6: `isKey` on the `Date` column.

Marked-as-date-table per 03 §a, confirmed Phase 4 §d (CLAUDE.md Status section: "marked as date table (`dataCategory: Time`)" applied 2026-05-23).

### 3. Active relationship to dim_Date

Grep `pbip/Tonnelle_Risk.SemanticModel/definition/relationships.tmdl` lines 9-11:

```
relationship 1a664725-3fa5-50be-d3ea-f01a1de00149
    fromColumn: Risk_Updates.update_date
    toColumn: dim_Date.Date
```

No `isActive: false` line → active by default. Cardinality lines stripped by Power BI Desktop's TMDL serializer because M:1 single-direction is the implicit default (documented Phase 5 quirk in CLAUDE.md gotchas).

All three relationships from 03 §a present:

| From | To | Active |
|---|---|---|
| `Risk_Updates[risk_id]` | `Risk_Register[risk_id]` | Yes |
| `Risk_Register[project_id]` | `Project[project_id]` | Yes |
| `Risk_Updates[update_date]` | `dim_Date[Date]` | Yes |

### 4. Pre-computed expected monthly `[Updates Count]` series

Computed by `scripts/verify_phase6_measures.py` against `source_data/Tonnelle_Risk_Updates_MASTER.xlsx` this turn. This is the exact series the Page 1 Risk Activity Over Time line will plot once `[Updates Count]` is bound to the Y-axis and `dim_Date[YearMonth]` to the X-axis.

| YearMonth | Updates Count |
|---|---|
| 2025-09 | 8 |
| 2025-10 | 11 |
| 2025-11 | 14 |
| 2025-12 | 14 |
| 2026-01 | 11 |
| 2026-02 | 14 |
| 2026-03 | 19 |
| 2026-04 | 13 |
| 2026-05 | 23 |
| **TOTAL** | **127** |

Total reconciles with CLAUDE.md Status row count (`Risk_Updates=127`).

Months in `[MIN, MAX]` with zero updates: **none**. The line will be continuous across all 9 active months with no gaps. Months outside the active range (`dim_Date` covers 2025-01..2025-08 and 2026-06..2026-12 in addition) will resolve to BLANK and produce no line segment in those regions, which is the intended chart behavior given no underlying activity. If Phase 9 visual review prefers a forced-zero line across the full `dim_Date` span, change the measure to `COUNTROWS ( Risk_Updates ) + 0` (see §c deferred optimization note).

### 5. Pre-computed `[Days Since Last Update]` reference values

Reference `TODAY()` = 2026-05-23 (system date this turn; the in-Power-BI value updates daily). Computed by the same script.

| Quantity | Value |
|---|---|
| Risks in Register with no Updates rows (`[Days Since Last Update]` = BLANK) | **0** (all 37 risks have at least one update) |
| Updates `risk_id`s not in Register (orphan updates) | 0 |
| Per-risk min Days Since Last Update | 11 d |
| Per-risk median Days Since Last Update | 20 d |
| Per-risk max Days Since Last Update | 169 d |

Top-10 stalest risks (sanity sample for verifying the Page 2 Top Risks "Days Since Last Update" column once it is bound):

| risk_id | Days Since Last Update |
|---|---|
| TONN-CON.01 | 169 |
| TONN-CON.14 | 159 |
| TONN-CON.08 | 131 |
| TONN-CON.28 | 125 |
| TONN-CON.05 | 74 |
| TONN-CON.19 | 43 |
| TONN-CON.16 | 38 |
| TONN-CON.20 | 33 |
| TONN-CON.11 | 31 |
| TONN-CON.07 | 31 |

These will drift by one each calendar day until the next Excel-side update entry is appended. Re-run `scripts/verify_phase6_measures.py` whenever fresh updates are added.

### 6. TMDL syntax parse

`pbip/Tonnelle_Risk.SemanticModel/definition/tables/_Measures.tmdl` bracket/brace balance after edit: `paren=0 brack=0 brace=0`. Measure-name grep returns 10 unique names (4 Counts + 4 Scores + 2 TimeIntel). `displayFolder:` line count = 10 (no measure missing a folder).

### 7. Measure-name uniqueness across `_Measures.tmdl`

Grep results:
```
 5: 'Total Risks'
11: 'High Risks'
21: 'Medium Risks'
31: 'Low Risks'
41: 'Avg Risk Score Overall'
47: 'Avg Cost Score'
53: 'Avg Schedule Score'
59: 'Max Risk Score'
65: 'Updates Count'
71: 'Days Since Last Update'
```

10 measures, 10 unique names, all on `_Measures`. No naming collision with Counts/Scores measures (Phase 5 lock preserved).

### 8. Performance flag scan

Per the data-goblin antipattern checklist applied in §c above:

| Antipattern | `Updates Count` | `Days Since Last Update` |
|---|---|---|
| SUMX / FILTER over fact table without context filter | absent | absent |
| Nested CALCULATE | absent | absent |
| CALCULATE inside iterator | absent | absent |
| Unnecessary ALL / REMOVEFILTERS | absent | absent |
| DISTINCTCOUNT where COUNTROWS suffices | absent (COUNTROWS chosen) | n/a |
| `BLANK()` arithmetic without guard | n/a | guarded by `ISBLANK` ✓ |
| Subtraction instead of DATEDIFF | n/a | `DATEDIFF` chosen ✓ |
| Repeated subexpression without VAR | n/a | `LastUpdate` stored in VAR ✓ |

No optimizations deferred.

### 9. MCP cross-check

Skipped this turn. `powerbi-modeling-mcp` is held in reserve per CLAUDE.md tooling section. User can validate post-open by binding `[Updates Count]` to a clustered column or line visual with `dim_Date[YearMonth]` on the axis and comparing to the §d-4 expected series, and by adding `[Days Since Last Update]` as a column to a `risk_id`-keyed table and comparing to the §d-5 top-10 stalest list.

---

## e) User-side actions to apply

### e1. Refresh and verify the measures

1. **Close Power BI Desktop** if it has the file open.
2. **Open `pbip/Tonnelle_Risk.pbip` in Power BI Desktop.**
3. **Refresh model** (Home → Refresh) to reload data and re-evaluate measures against latest source.
4. **Inspect the Fields pane:** confirm `_Measures` now shows a `TimeIntel` display folder under it with two measures: `Updates Count`, `Days Since Last Update`.
5. **Sanity-test `[Updates Count]`** (throwaway, removed before Phase 9):
   - Insert a clustered column chart or line chart on a blank area.
   - X-axis: `dim_Date[YearMonth]`. Y-axis: `[Updates Count]`.
   - Compare values to §d-4 expected table. Total should be 127.
   - If `dim_Date[YearMonth]` doesn't render sorted Jan→Dec, confirm `YearMonth` is set to "Sort by column" → `YearMonthSort` (Phase 4 §d, CLAUDE.md Status note).
6. **Sanity-test `[Days Since Last Update]`** (throwaway):
   - Insert a table visual.
   - Columns: `Risk_Register[risk_id]`, `[Days Since Last Update]`.
   - Sort by `[Days Since Last Update]` desc; compare top 10 to §d-5 stalest table.
   - Reference value at the time of writing: TONN-CON.01 = 169 d. Today's actual value = 169 + (days elapsed since 2026-05-23).
7. **Delete the throwaway sanity visuals.** The locked Page 1 line chart is built in Phase 9; the locked Page 2 Top Risks table is built in Phase 10.
8. **Save.** Confirm the TMDL on disk retains both measures with `displayFolder: TimeIntel`.

If `[Updates Count]` totals anything other than 127, inspect the Power Query `Risk_Updates` partition for row-filter regressions (the M is documented in `docs/04_power_query.md`). If `[Days Since Last Update]` returns large negative numbers anywhere, the system clock or `TODAY()` reference is in the past relative to update dates.

### e2. Known display-folder behavior

The `TimeIntel` folder will be created implicitly the first time Power BI Desktop loads a measure with `displayFolder: TimeIntel`. No explicit folder declaration is needed in TMDL. Same pattern Phase 5 used for `Counts` and `Scores`.

---

## f) Status

Phase 6 deliverable complete. 2 measures defined (`Updates Count`, `Days Since Last Update`) in the `TimeIntel` display folder of `_Measures.tmdl`. Date table coverage and active relationship to `dim_Date` verified intact from Phase 4/5. Expected monthly Updates Count series computed against source (127 total; range 8 to 23 per month across Sep 2025 – May 2026); per-risk Days Since Last Update reference values computed (range 11 to 169 d, median 20 d, no BLANK rows in current data). Performance flag scan passes with no deferred optimizations.

Phase 7 (SVG pill measure: `Risk Level Pill SVG`, target `docs/07_svg_pill.md` + test SVGs, skill `power-bi-dax-optimization`) is the next phase, unblocked.
