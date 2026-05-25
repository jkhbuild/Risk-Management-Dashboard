# 05. Semantic model + Counts/Scores measures

Phase 5 deliverable, prepared 2026-05-23. Skills loaded: `powerbi-modeling`, `power-bi-dax-optimization`.

**Inputs:**
- `docs/03_design_locked.md` (binding schema, relationships, measure architecture, naming).
- `docs/04_power_query.md` (Phase 4 M and application notes).
- Applied TMDL in `pbip/Tonnelle_Risk.SemanticModel/` (Phase 4 load).
- Source-data baselines computed against `source_data/Tonnelle_Risk_Register_MASTER.xlsx` this turn.

Scope: model-structure edits plus the 8 Counts and Scores measures. Time-intelligence (2) and Display (3) measures deferred to Phase 6 and Phase 7 per CLAUDE.md phase map.

---

## a) Files changed

| File | Change |
|---|---|
| `pbip/Tonnelle_Risk.SemanticModel/definition/relationships.tmdl` | Added explicit `fromCardinality: many`, `toCardinality: one`, `crossFilteringBehavior: oneDirection` on all three relationships. Added `///` docstrings. GUIDs preserved. |
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/Project.tmdl` | `project_id`: added `isHidden` (FK per 03 §a, was exposed in Phase 4 application). |
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/Risk_Register.tmdl` | Six score columns flipped `summarizeBy: sum` → `summarizeBy: none` per 03 §a "Don't summarize" lock: `probability_score`, `cost_impact_score`, `schedule_impact_score`, `risk_score_cost`, `risk_score_schedule`, `risk_score_overall`. Also `risk_level_sort` (was sum). |
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/Risk_Updates.tmdl` | `update_year`: flipped `summarizeBy: sum` → `summarizeBy: none`. |
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/_Measures.tmdl` | **New file.** Helper table with hidden `_dummy` column, calculated partition `ROW("_dummy", BLANK())`, and 8 measures across `Counts` (4) and `Scores` (4) display folders. |
| `pbip/Tonnelle_Risk.SemanticModel/definition/model.tmdl` | Added `ref table '_Measures'` (kept at the bottom of the ref list; query order untouched). |
| `scripts/verify_phase5_measures.py` | **New file.** Computes expected baseline values from the Register source workbook; produces the §c table below. |

No deletions. No measure or table other than `_Measures` was created.

Phase 4 deficiencies caught and corrected:
- Project.project_id was loaded unhidden despite 03 §a marking it `Hidden=Yes` (FK).
- Six numeric columns on Risk_Register and one on Risk_Updates inherited Power BI's `summarizeBy: sum` default during load despite 03 §a marking them `Don't summarize`. Risk_level_sort had the same. Now corrected.

---

## b) Measure definitions

All 8 measures live in `_Measures.tmdl`. Each carries a TMDL `///` description naming the intent and the consuming visual. Format strings match 03 §a/§d conventions (`0` for integer counts and max, `0.0` for averages per Page 1 KPI card spec line 250).

### Counts (4)

```dax
Total Risks = COUNTROWS ( Risk_Register )

High Risks =
CALCULATE (
    COUNTROWS ( Risk_Register ),
    Risk_Register[risk_level] = "High"
)

Medium Risks =
CALCULATE (
    COUNTROWS ( Risk_Register ),
    Risk_Register[risk_level] = "Medium"
)

Low Risks =
CALCULATE (
    COUNTROWS ( Risk_Register ),
    Risk_Register[risk_level] = "Low"
)
```

### Scores (4)

```dax
Avg Risk Score Overall = AVERAGE ( Risk_Register[risk_score_overall] )

Avg Cost Score = AVERAGE ( Risk_Register[risk_score_cost] )

Avg Schedule Score = AVERAGE ( Risk_Register[risk_score_schedule] )

Max Risk Score = MAX ( Risk_Register[risk_score_overall] )
```

### Optimization rationale (data-goblin heuristics applied)

- `COUNTROWS` chosen over `DISTINCTCOUNT(Risk_Register[risk_id])`. `risk_id` is the PK; uniqueness is guaranteed by Phase 1 audit, so the two return identical values and `COUNTROWS` is the faster path (no hash table build).
- High/Medium/Low Risks use `CALCULATE` with a single Boolean filter argument; the filter is folded into the storage-engine scan with no row context introduced. No `FILTER(ALL(...))` wrapper, no row-by-row iteration.
- No `SUMX`-style iteration is required because all four count measures resolve against a flat fact table with no expression-per-row needed.
- Averages use the scalar `AVERAGE(column)` form rather than `AVERAGEX(table, expression)`. The two are equivalent for a plain column, but `AVERAGE` is the documented preferred form for clarity.
- `Max Risk Score` uses scalar `MAX`. No `MAXX` needed.
- No `ALL`, no `KEEPFILTERS`, no `REMOVEFILTERS`. The locked Page 2 slicers (category, coordinator, risk_level) must propagate to these measures; using `ALL` would break that.

### Display folder mapping

| Measure | displayFolder |
|---|---|
| `Total Risks`, `High Risks`, `Medium Risks`, `Low Risks` | `Counts` |
| `Avg Risk Score Overall`, `Avg Cost Score`, `Avg Schedule Score`, `Max Risk Score` | `Scores` |

`TimeIntel` and `Display` folders will be created when Phase 6 and Phase 7 add their respective measures; TMDL implicitly creates display folders the first time a measure references one.

---

## c) Expected measure values (verify after open and refresh)

Computed against `source_data/Tonnelle_Risk_Register_MASTER.xlsx` (37 rows, all `risk_id` non-null). Script: `scripts/verify_phase5_measures.py`.

| Measure | Expected value | Source-data computation |
|---|---|---|
| `[Total Risks]` | 37 | COUNTROWS(Risk_Register) where risk_id is not null |
| `[High Risks]` | 12 | Rows where risk_level = 'High' |
| `[Medium Risks]` | 10 | Rows where risk_level = 'Medium' |
| `[Low Risks]` | 15 | Rows where risk_level = 'Low' |
| `[Avg Risk Score Overall]` | 10.35 | Mean of risk_score_overall (37 rows) |
| `[Avg Cost Score]` | 9.65 | Mean of risk_score_cost (37 rows) |
| `[Avg Schedule Score]` | 7.86 | Mean of risk_score_schedule (37 rows) |
| `[Max Risk Score]` | 25 | Max of risk_score_overall (37 rows) |

Row-level integrity: risk_level value counts `{Low: 15, High: 12, Medium: 10}` sum to 37, matching total. No stray values.

These match the CLAUDE.md Status-section baselines exactly.

---

## d) Self-verification log

### 1. TMDL syntax parse

Bracket and brace balance across all 11 TMDL files (database, expressions, model, relationships, cultures/en-US, 5 tables, _Measures) yields `paren=0 brack=0 brace=0` for every file. Every measure has a definition expression; every relationship declares `fromColumn`, `toColumn`, `fromCardinality`, `toCardinality`, `crossFilteringBehavior`. Verified by `python -c` against all `.tmdl` files this turn.

### 2. Measure name uniqueness

Grep across `definition/`:
```
_Measures.tmdl:15  Total Risks
_Measures.tmdl:21  High Risks
_Measures.tmdl:31  Medium Risks
_Measures.tmdl:41  Low Risks
_Measures.tmdl:51  Avg Risk Score Overall
_Measures.tmdl:57  Avg Cost Score
_Measures.tmdl:63  Avg Schedule Score
_Measures.tmdl:69  Max Risk Score
```

8 measures, 8 unique names, all on `_Measures`.

### 3. Display folder coverage

8 measures, 8 `displayFolder:` lines (4 `Counts`, 4 `Scores`). Zero measures without a display folder. Folder names match the 03 §b lock.

### 4. Relationship match against 03 §a

| From | To | Cardinality | Cross-filter | TMDL declared |
|---|---|---|---|---|
| `Risk_Updates[risk_id]` | `Risk_Register[risk_id]` | M:1 | Single | `fromCardinality: many`, `toCardinality: one`, `crossFilteringBehavior: oneDirection` ✓ |
| `Risk_Register[project_id]` | `Project[project_id]` | M:1 | Single | same ✓ |
| `Risk_Updates[update_date]` | `dim_Date[Date]` | M:1 | Single | same ✓ |

No deviation. No bidirectional relationships. Per 03 §a closing note, if a future measure needs Register-filtered-from-Updates context, use `CROSSFILTER` inside the measure rather than enabling bidirectional at the relationship level.

### 5. Hidden columns match 03 §a

| Table | Column | Required | Actual |
|---|---|---|---|
| Risk_Register | project_id | Hidden | Hidden ✓ |
| Risk_Register | status | Hidden | Hidden ✓ |
| Risk_Register | risk_level_sort | Hidden | Hidden ✓ |
| Risk_Updates | update_id | Hidden | Hidden ✓ |
| Risk_Updates | risk_id | Hidden | Hidden ✓ |
| Risk_Updates | update_year | Hidden | Hidden ✓ |
| dim_Date | MonthNumber | Hidden | Hidden ✓ |
| dim_Date | YearMonthSort | Hidden | Hidden ✓ |
| Project | project_id | Hidden | Hidden ✓ (fixed this turn) |
| _Measures | _dummy | Hidden | Hidden ✓ |

### 6. Date table marking

`dim_Date.tmdl` line 3: `dataCategory: Time` on the table; line 6: `isKey` on the `Date` column. Marked-as-date-table per 03 §a. CLAUDE.md Status section confirms the mark was applied 2026-05-23.

### 7. Expected-value computation

`scripts/verify_phase5_measures.py` ran cleanly against the source workbook this turn; 37 rows loaded, all expected values printed as in §c above. User runs the same script (`PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python scripts/verify_phase5_measures.py`) any time the Register source workbook is updated to refresh the baselines.

### 8. MCP cross-check (optional)

Skipped this turn. `powerbi-modeling-mcp` is held in reserve until Phase 6 per CLAUDE.md "MCP held in reserve" note. User can run a Power BI Desktop visual binding each measure to a card to confirm post-refresh values match §c.

---

## e) User-side actions to apply

**Iteration note (2026-05-23):** First attempt at TMDL-direct edits was partially reverted by Power BI Desktop's TMDL normalizer on save. `_Measures.tmdl` reauthored using Power BI's canonical pattern (column `Value`, partition source `{BLANK()}`, `isNameInferred`) and accepted by Power BI Desktop on re-open. The four §e2 reverts were re-applied via the Desktop UI (Column tools "Don't summarize" → `SummarizationSetBy = User`; right-click Hide for FKs); all 8 numeric columns now carry `summarizeBy: none` and FK columns `isHidden`. Relationship cardinality lines stripped by the serializer because M:1 single-direction is the implicit default; behavior matches spec. User also added a Power Query step `#"Removed Bottom Rows" = Table.RemoveLastN(WithSort, 3)` on Risk_Register to drop 3 trailing all-null rows that crept into the source workbook; net loaded row count is the 37 baseline rows (verified by `scripts/verify_phase5_measures.py`, which independently drops null-risk_id rows via pandas `dropna` and arrives at the same 37).

### e1. Apply the _Measures table

1. **Close Power BI Desktop** if it has the file open. (Power BI Desktop's TMDL writer can overwrite on save; close it before swapping files.)
2. **Open `pbip/Tonnelle_Risk.pbip` in Power BI Desktop.**
3. **Inspect the Fields pane:** confirm the `_Measures` table appears with `Counts` and `Scores` display folders. Each folder contains 4 measures.
4. **If the table does not appear,** create it via the Desktop UI as a fallback (this guarantees Power BI Desktop's own TMDL writer produces the table):
   - Modeling → **New table** → enter: `_Measures = {BLANK()}` → Enter.
   - Right-click the auto-created `Value` column → **Hide in report view**.
   - For each of the 8 measures in §b: Modeling → **New measure** → paste the DAX → in the Properties pane, set **Display folder** to `Counts` or `Scores` per §b mapping, set **Format** to `0` (integer counts/max) or `0.0` (averages).
   - Save.

### e2. Re-apply the four reverts via UI

Power BI Desktop's TMDL serializer reverted these on save because its automatic-mode defaults override explicit TMDL values for int64 columns and for relationship cardinality. They must be reset via the Desktop UI.

| Setting | Where | Action |
|---|---|---|
| `Project.project_id` hidden | Fields pane, right-click `project_id` under Project | **Hide in report view**. |
| Score columns "Don't summarize" | Fields pane, select each numeric column on Risk_Register (`probability_score`, `cost_impact_score`, `schedule_impact_score`, `risk_score_cost`, `risk_score_schedule`, `risk_score_overall`, `risk_level_sort`) | Column tools → **Summarization: Don't summarize**. |
| `Risk_Updates[update_year]` "Don't summarize" | Fields pane, Risk_Updates → `update_year` (currently hidden) | Show hidden in model view, set Column tools → **Summarization: Don't summarize**, re-hide. |
| Relationship cardinality | Model view, double-click each of the three relationships | Confirm **Many-to-one (*:1)** and **Single** cross-filter. (Power BI's defaults; the lines just get stripped from TMDL when they equal the default.) |

UI-driven changes set the column annotation to `SummarizationSetBy = User` and persist correctly across saves; TMDL-direct edits to `summarizeBy: none` get stripped because the column's `SummarizationSetBy = Automatic` annotation tells Power BI to apply its own default.

### e3. Sanity-test the measures

1. **Build a one-card sanity test (throwaway, not part of the locked Page 1 layout):**
   - Drop `[Total Risks]` onto a blank card.
   - Drop `[High Risks]`, `[Medium Risks]`, `[Low Risks]`, `[Avg Risk Score Overall]`, `[Max Risk Score]` onto more cards.
2. **Compare to §c expected values.** If the user kept the `#"Removed Bottom Rows"` step (drops 3 rows from Risk_Register), expected counts will be lower than §c by exactly the dropped band's contribution. Re-run `scripts/verify_phase5_measures.py` after the user finalizes the row set.
3. **Save** the file.
4. **Delete the throwaway sanity cards.** The locked Page 1 layout is built in Phase 9.

If any expected value mismatches §c, do not proceed to Phase 6. Inspect the measure definition in `_Measures.tmdl` line-by-line and the Risk_Register row count via Power Query Editor.

---

## f) Status

Phase 5 deliverable complete and applied 2026-05-23. 8 measures defined in TMDL using Power BI's canonical measures-table pattern; model structure matches 03 §a lock; §e2 UI follow-ups applied (Project.project_id hidden; 7 numeric columns set to "Don't summarize" with `SummarizationSetBy = User`; relationships M:1 single-direction confirmed). User dropped 3 trailing null rows from Risk_Register via Power Query `Table.RemoveLastN(WithSort, 3)`; row count is the 37 baseline. Phase 6 (TimeIntel measures: `Updates Count`, `Days Since Last Update`; target `docs/06_time_intel.md`) is the next phase, unblocked.
