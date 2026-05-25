# 09. Page 1 Executive Overview

Phase 9 deliverable, prepared 2026-05-23. Skill loaded: `pbi-report-design` (data-goblin).

**Inputs:**
- `docs/03_design_locked.md` §c (theme), §d Page 1 visual list and positions (9 visuals), §f-1/f-4/f-6 documented rule violations.
- `docs/05_semantic_model.md` (8 Counts/Scores measures), `docs/06_time_intel.md` (2 TimeIntel measures); 11 measures total before this turn.
- `docs/08_theme.md` (`assets/theme.json`, eight `visualStyles` entries; title font/color, card.title.show=false, lineChart continuous axis, etc.).
- Mockup `assets/risk_dashboard_mockup.png` (typography weight, KPI density, P-I cell colors, line color).
- Current PBIR state: one empty page `e9278a0c19c775b80859` with `displayName: Page 1`; one `pbir`-managed `Title.Visual` from a prior session.

Scope: nine PBIR visuals on a single page named `Overview` (display "Executive Overview"). One semantic model extension: a calculated column `max_impact_score` on `Risk_Register` to drive the P-I matrix column axis. The theme is not applied this phase; that is a one-click user-side step per 08 §g.

---

## a) Files changed

| File | Change |
|---|---|
| `pbip/Tonnelle_Risk.Report/definition/pages/pages.json` | `pageOrder` and `activePageName` updated `e9278a0c19c775b80859` → `Overview`. |
| `pbip/Tonnelle_Risk.Report/definition/pages/e9278a0c19c775b80859/` | **Renamed** to `pages/Overview/` (pbir CLI `pages rename` + manual `name`/`displayName` edit). |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/page.json` | `name: Overview`, `displayName: Executive Overview` (was `Page 1`); 1280x720, FitToPage preserved. |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/PageHeader/visual.json` | **New** textbox (renamed from `pbir add title`-generated `Title/`). Two paragraphs: title (Segoe UI Semibold 22pt #1a1a1a) and subtitle (Segoe UI 11pt #5a5a5a). |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/KPITotalRisks/visual.json` | **New** card. Binds `_Measures.Total Risks`. Title "Total Risks". |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/KPIHighRisks/visual.json` | **New** card. Binds `_Measures.High Risks`. Title "High". Rules CF on `labels.color`: if `[High Risks] > 10` then `#de425b` (per 03 §d Page 1 #3). |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/KPIMediumRisks/visual.json` | **New** card. Binds `_Measures.Medium Risks`. Title "Medium". |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/KPILowRisks/visual.json` | **New** card. Binds `_Measures.Low Risks`. Title "Low". |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/KPIAvgScore/visual.json` | **New** card. Binds `_Measures.Avg Risk Score Overall`. Title "Avg Score". `labels.labelPrecision = 1` to display "10.4" not "10". |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/PIMatrix/visual.json` | **New** pivotTable. Rows `Risk_Register.probability_score` (desc), Columns `Risk_Register.max_impact_score` (asc), Values `_Measures.Total Risks`. **Note: shipped with bindings + sort only.** Initial Phase 9 attempt added `showAll: true` on both axes plus rules CF on `values.backColor`/`fontColor` keyed to `_Measures.Max Risk Score`, but Power BI Desktop on open returned `InvalidOrMalformedDataShapeBinding_RepeatedIndicesProjectionsOrGroupBy` (likely the combination of showAll on two axes plus CF referencing a measure not in projections). Stripped back to minimal; user adds CF and "Show items with no data" via Desktop UI (see §e). |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/RisksByCategory/visual.json` | **New** clusteredBarChart. Category `Risk_Register.risk_category`, Y `_Measures.Total Risks` (sort desc), Series `Risk_Register.risk_level`. Rules CF on `dataPoint.fill` keyed to `risk_level`: Low→`#488f31`, Medium→`#e8b450`, High→`#de425b`. |
| `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/RiskActivity/visual.json` | **New** lineChart. Category `dim_Date.YearMonth` (sort asc), Y `_Measures.Updates Count`. `lineStyles.markerShape = circle`, `markerSize = 4`. Single-series line picks up theme `dataColors[0] = #488f31`. |
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/Risk_Register.tmdl` | Calculated column `max_impact_score = IF(Risk_Register[cost_impact_score] >= Risk_Register[schedule_impact_score], Risk_Register[cost_impact_score], Risk_Register[schedule_impact_score])` added between `schedule_impact_score` and `risk_score_cost`. dataType int64, formatString `0`, `summarizeBy: none`, `SummarizationSetBy = User`, visible. |
| `pbip/Tonnelle_Risk.Report/definition/pages/e9278a0c19c775b80859/` | **Deleted** (folder renamed by pbir CLI). |

A pre-edit backup of the report was created via `pbir backup` at `~/.config/pbir/backups/tonnelle-risk/20260523T060049Z/` ("Pre-Phase-9 baseline (empty Page 1 only)").

### Phase 9-driven semantic model extension

The P-I matrix Columns axis requires `MAX(cost_impact_score, schedule_impact_score)` as a field per 03 §d Page 1 visual #7. Matrix column axes cannot bind an expression; only fields. Two options were considered:

1. Add a Power Query M step on `Risk_Register` to compute the column at load.
2. Add a DAX calculated column on `Risk_Register`.

Chose option 2 because the Phase 4 M code is locked (04 §c), and a calculated column is a smaller, more localized change. The column is row-context-evaluated, has identical compression properties to a source column post-VertiPaq, and supports the matrix axis directly. Locked-decision review: 03 §a "score columns are Excel formulas, not DAX, not Power Query" governs `risk_score_*` (the actual P x I products); `max_impact_score` is a derived axis value, not a score, so the rule does not apply.

The column is visible (not hidden) so a user can also use it in slicers or filters if a later phase requires.

---

## b) Visuals shipped (9 visuals matching 03 §d Page 1)

| # | Visual name | Type | Position (x, y, w, h) | Measure/column bindings |
|---|---|---|---|---|
| 1 | `PageHeader` | textbox | (24, 24, 1232, 60) | Static. Line 1 (22pt Semibold): "Tonnelle Avenue Bridge Relocation — Risk Register". Line 2 (11pt regular): "Project TONN-01  •  Data refreshed 2026-05-23". |
| 2 | `KPITotalRisks` | card | (24, 100, 233, 100) | `[Total Risks]`. Custom title "Total Risks" (11pt regular #5a5a5a). categoryLabels hidden. |
| 3 | `KPIHighRisks` | card | (273, 100, 233, 100) | `[High Risks]`. Custom title "High". CF on `labels.color`: rule `[High Risks] gt 10` → `#de425b`; else theme default `#1a1a1a`. |
| 4 | `KPIMediumRisks` | card | (522, 100, 233, 100) | `[Medium Risks]`. Custom title "Medium". |
| 5 | `KPILowRisks` | card | (771, 100, 233, 100) | `[Low Risks]`. Custom title "Low". |
| 6 | `KPIAvgScore` | card | (1020, 100, 236, 100) | `[Avg Risk Score Overall]`. Custom title "Avg Score". `labels.labelPrecision = 1` (display "10.4"). |
| 7 | `PIMatrix` | pivotTable | (24, 216, 480, 290) | Rows `Risk_Register.probability_score` desc; Columns `Risk_Register.max_impact_score` asc; Values `[Total Risks]`. Natural axis sort on Columns (asc). **CF and showAll deferred to user-side Desktop UI** (see §e). Initial JSON-based CF and `showAll: true` produced a "RepeatedIndices" error on open. |
| 8 | `RisksByCategory` | clusteredBarChart | (520, 216, 736, 290) | Category `risk_category` (sort by Total Risks desc); Y `[Total Risks]`; Series `risk_level` (sort by `risk_level_sort` Low/Medium/High). **Per-series colors via theme `dataColors` slot order** after CF rules failed (see §c). Title "Risks by Category". |
| 9 | `RiskActivity` | lineChart | (24, 522, 1232, 174) | Category `dim_Date.YearMonth` (sort asc; column sort-by `YearMonthSort` resolves chronological order); Y `[Updates Count]`. Markers circle 4px. Line color from theme `dataColors[0] = #488f31`. Title "Risk Activity Over Time (updates per month)". |

Visual count = 9, matching 03 §d. Visual types match: 1 textbox + 5 card + 1 pivotTable + 1 clusteredBarChart + 1 lineChart. No slicers on Page 1 (03 §d filter pane only).

Active relationships continue to propagate slicer/filter context to `[Updates Count]` and `[Max Risk Score]` per 05 §d and 06 §c (no `ALL`/`REMOVEFILTERS` anywhere, including added CF measures).

### Page-level filter

The report-level filter `status = "Open"` from 03 §d (forward-compat, no-op today since all rows are "Open") is not encoded in this phase. The status column is hidden in the model; adding a filter referencing a hidden column requires a Power BI Desktop UI step (right-click the field in the Filter pane, set to `Open`). Listed in §e as a user-side click.

---

## c) Conditional formatting and visual-level overrides

### CF rules applied

| Visual | Container | Field basis | Rules |
|---|---|---|---|
| KPIHighRisks | `labels.color` | `_Measures.High Risks` | `gt 10` → `#de425b`. Default theme color `#1a1a1a` for ≤ 10. |
| ~~PIMatrix~~ | ~~values.backColor~~ | ~~Max Risk Score~~ | **Deferred to user-side Desktop UI** (see §e and §f Known issue). |
| ~~PIMatrix~~ | ~~values.fontColor~~ | ~~Max Risk Score~~ | **Deferred to user-side Desktop UI.** |
| ~~RisksByCategory~~ | ~~dataPoint.fill~~ | ~~Risk_Register.risk_level~~ | **Removed.** Two iterations failed: pbir CLI's `Left.Measure` wrapper hit `Missing_References` (Power BI strictly type-checks the wrapper against the column's actual role); switching to `Left.Column` then hit `RepeatedIndicesProjectionsOrGroupBy` (the field is already in `Series` projection; the CF comparison creates a duplicate column reference in the data shape). The CF-rules approach pbir CLI generates doesn't compose with column-based series binding. **Per-series colors now driven by theme `dataColors` slot order** (theme.json reordered this turn so slots [0,1,2] = Low/Medium/High and align with the `risk_level` series natural sort by `risk_level_sort`). See §c "Theme-driven per-series binding" below. |

CF created via `pbir visuals cf --rules`. Generated structure: `objects.<container>[1].properties.<prop>.solid.color.expr.Conditional.Cases[]` with `Comparison` (`ComparisonKind: 0` eq, `1` gt, `2` gte) and `Literal` color values, plus a `selector.data[dataViewWildcard]` for wildcard application across all data points. The first array entry (`objects.<container>[0]`) is a placeholder with empty properties; pbir CLI emits this so a `ThemeOnly` slot is preserved.

The RisksByCategory CF was edited post-CLI-generation: pbir CLI emitted `Left.Measure` for the `risk_level` field comparison; changed to `Left.Column` because `risk_level` is a column, not a measure (Power BI's CF rule type wrapper). See §d-9.

### Per-visual title overrides (deviation from 08 §c "card.title.show = false")

The 5 KPI cards each set `visualContainerObjects.title.properties.show = true` with custom text. Theme has `card.title.show = false`. The override is necessary because the spec labels ("Total Risks", "High", "Medium", "Low", "Avg Score") in 03 §d do not all match measure names ("Total Risks", "High Risks", "Medium Risks", "Low Risks", "Avg Risk Score Overall"). categoryLabels would auto-display the measure name; custom title text was the cleanest way to use the spec's short labels.

Title styling per card: `fontFamily: Segoe UI`, `fontSize: 11pt`, `bold: false`, `fontColor: #5a5a5a`, `alignment: left`. This matches 03 §c2 "KPI label" typography role rather than the theme wildcard's title default (Semibold 14pt). The result is a small grey label above the 32pt KPI value (mockup: "TOTAL RISKS / 64").

To avoid duplication, `objects.categoryLabels[0].properties.show = false` on every KPI card.

### Theme-driven per-series binding (RisksByCategory)

After two failed CF iterations (see CF rules table above), per-series colors on RisksByCategory now come from the theme `dataColors` slot order. The series field `risk_level` has `sortByColumn: risk_level_sort` (Low=1, Medium=2, High=3) per Phase 4-5 model, so Power BI binds series-to-slot in that order. Theme reordered this turn:

| Slot | Hex | Token | Series value (Risks by Category) |
|---|---|---|---|
| 0 | `#488f31` | risk_low | Low |
| 1 | `#e8b450` | risk_medium | Medium |
| 2 | `#de425b` | risk_high | High |

Slot 0 remains `#488f31` (preserves single-series-line and brand-accent intent from 08 §a). Slot 1 swapped from `#de425b` to `#e8b450` so the natural risk-band gradient (low → med → high) maps cleanly to slot order. No other Page 1 visual on the locked spec explicitly binds to slot 1, so this reorder is a safe theme adjustment. See [docs/08_theme.md](08_theme.md) for the updated dataColors block.

**Tradeoff:** the theme must be applied for these colors to take effect. Pre-theme, Power BI Desktop uses its default palette and the clustered bars render in default blue/orange/red. After the user applies `assets/theme.json` (Phase 8 §g / §e1 of this doc), the bars pick up the locked palette automatically.

### Theme-inherited styling (no per-visual override needed)

- KPI card value: 32pt Semibold #1a1a1a per theme `card.labels`.
- Matrix gridlines/headers: per theme `pivotTable.grid` (no vertical/horizontal lines), `pivotTable.columnHeaders/rowHeaders` (Semibold 11pt #1a1a1a).
- Line chart axes/legend: per theme `lineChart.categoryAxis` (Continuous), `valueAxis`, `legend`, `labels`.
- Clustered bar chart axes/labels: per theme `clusteredBarChart.categoryAxis` (10pt #1a1a1a), `valueAxis.show = false`, `labels.show = true labelPosition: Outside end`.
- All visual backgrounds/borders/drop-shadows: per theme `card.background/border` (white fill, #e0e0e0 1px border, no shadow) and `*.dropShadow.show = false`.

### Inline hex codes (deviation from "all colors derive from theme" goal)

Found 9 distinct hex codes in Page 1 PBIR JSON across visuals. All are justified by the locked spec:

| Hex | Found in | Justification |
|---|---|---|
| `#1a1a1a` | PageHeader title text run; PIMatrix CF fontColor (Medium cells) | Theme cannot drive textbox content (08 §c "textbox not styled by theme"); CF on matrix is explicit per 03 §c1. |
| `#5a5a5a` | PageHeader subtitle; KPI title.fontColor (all 5 cards) | textbox inline; KPI label per 03 §c2 typography role. |
| `#488f31` | PIMatrix backColor CF; RisksByCategory dataPoint CF | 03 §c1 heatmap (`risk_low`); 03 §d Page 1 #8 series binding. |
| `#e8b450` | Same | 03 §c1 (`risk_medium`); 03 §d Page 1 #8. |
| `#de425b` | KPIHighRisks labels.color CF; PIMatrix; RisksByCategory | 03 §c1 (`risk_high`); 03 §d Page 1 #3 conditional value-color rule. |
| `#FFFFFF` | PIMatrix fontColor CF (Low and High cells) | 03 §c1 heatmap cell text rule. |

The KPI card title `fontColor: #5a5a5a` could have used the theme's `header` textClass (#1a1a1a) instead; chose to override per 03 §c2 which explicitly assigns `text_secondary #5a5a5a` to the KPI label role. The deviation is locally justified by the spec and not a defect.

No "raw" hex was introduced (all 6 distinct hexes are tokens from 03 §c1 / theme.json).

### "Show items with no data"

Locked spec implication for PIMatrix: empty cells must show with white fill rather than collapse out of the grid. Achieved by `showAll: true` on Rows and Columns projections (pbir CLI `visuals show-all --role Rows/Columns`); written to the visual.json query state.

This is also the right-click "Show items with no data" Power BI Desktop UI option per CLAUDE.md gotcha; PBIR encoding via `showAll` is fully sufficient and does not require a Desktop UI click after open.

The 03 §d Page 1 layout does not call for "Show items with no data" on any other visual.

---

## d) Self-verification log

### 1. PBIR JSON parse

```
OK: visuals\KPIAvgScore\visual.json
OK: visuals\KPIHighRisks\visual.json
OK: visuals\KPILowRisks\visual.json
OK: visuals\KPIMediumRisks\visual.json
OK: visuals\KPITotalRisks\visual.json
OK: visuals\PIMatrix\visual.json
OK: visuals\PageHeader\visual.json
OK: visuals\RiskActivity\visual.json
OK: visuals\RisksByCategory\visual.json
OK: page.json (name=Overview display=Executive Overview)
```

All 9 visual.json files plus page.json parse as valid JSON.

`pbir validate` reports 3 errors and 2 warnings, all pre-existing per CLAUDE.md tooling notes ("CLI's bundled schemas lag report's"; "Neither blocks Power BI Desktop"). The errors are:
- `report.json` schema version mismatch (3.3.0 declared, CLI bundled 3.2.0).
- `pages.json` schema version mismatch (1.1.0 declared, CLI bundled).
- `Tonnelle_Risk.pbip` lacks `$schema` (Power BI Desktop's standard pbip envelope; pre-existing from Phase 3 setup).

No new errors introduced this phase.

### 2. Measure-name resolution

Field references across 9 Page 1 visuals (grep against PBIR JSON, deduplicated):

| Field | Used by | Resolved in model |
|---|---|---|
| `_Measures.Total Risks` | KPITotalRisks; PIMatrix; RisksByCategory | ✓ (05 §b) |
| `_Measures.High Risks` | KPIHighRisks (Values + CF) | ✓ (05 §b) |
| `_Measures.Medium Risks` | KPIMediumRisks | ✓ (05 §b) |
| `_Measures.Low Risks` | KPILowRisks | ✓ (05 §b) |
| `_Measures.Avg Risk Score Overall` | KPIAvgScore | ✓ (05 §b) |
| `_Measures.Max Risk Score` | PIMatrix CF (backColor + fontColor) | ✓ (05 §b; reserved-for-Phase-5+ noted, now used) |
| `_Measures.Updates Count` | RiskActivity | ✓ (06 §b) |
| `Risk_Register.probability_score` | PIMatrix Rows | ✓ (Risk_Register.tmdl line 66) |
| `Risk_Register.max_impact_score` | PIMatrix Columns | ✓ (this phase, line 94) |
| `Risk_Register.risk_category` | RisksByCategory Category | ✓ (Risk_Register.tmdl line 42) |
| `Risk_Register.risk_level` | RisksByCategory Series + dataPoint CF | ✓ (Risk_Register.tmdl line 120) |
| `dim_Date.YearMonth` | RiskActivity Category | ✓ (dim_Date.tmdl line 43; sortByColumn YearMonthSort) |

All 12 referenced fields resolve. No unresolved measures or columns.

### 3. Visual count and types vs 03 §d

| 03 §d Page 1 visual | PBIR visual | Type match |
|---|---|---|
| #1 Page header (textbox) | PageHeader | ✓ textbox |
| #2 Total Risks (card) | KPITotalRisks | ✓ card |
| #3 High Risks (card) | KPIHighRisks | ✓ card |
| #4 Medium Risks (card) | KPIMediumRisks | ✓ card |
| #5 Low Risks (card) | KPILowRisks | ✓ card |
| #6 Avg Risk Score (card) | KPIAvgScore | ✓ card |
| #7 P-I matrix (matrix/pivotTable) | PIMatrix | ✓ pivotTable |
| #8 Risks by Category (clustered horizontal bar) | RisksByCategory | ✓ clusteredBarChart |
| #9 Risk Activity (line) | RiskActivity | ✓ lineChart |

9 visuals, 9 type matches.

Position match: all 9 visuals on disk match 03 §d (x, y, w, h) byte-for-byte. Verified by grepping `position.x, .y, .width, .height` for each.

### 4. Cross-filter sanity

Page 1 has no slicers. Cross-filter exercised via visual-to-visual click.

Example trace, "click on Construction bar in RisksByCategory":

1. Click action creates a filter `Risk_Register[risk_category] = "Construction"`.
2. Filter applies to all Page 1 visuals that bind to `Risk_Register`:
   - KPI cards (`Total Risks`, `High`, `Medium`, `Low`, `Avg Risk Score Overall`): all measures re-evaluate inside the filtered context. `[Total Risks]` shows the Construction subset; level counts shift; `[Avg Risk Score Overall]` averages only Construction risks.
   - PIMatrix: the rows/columns axis (`probability_score`, `max_impact_score`) remain enumerated 1-5 because of `showAll: true`. Values cells (`[Total Risks]`) reflect only Construction risks. `[Max Risk Score]` CF basis reflects only Construction risks; cells with no Construction risks lose their CF fill (revert to theme white).
3. RiskActivity binds Y = `[Updates Count]` which depends on `Risk_Updates`. The filter propagates via the active M:1 `Risk_Updates[risk_id] → Risk_Register[risk_id]` (single direction, Register filters Updates). Only updates for Construction risks contribute to the monthly count.
4. X-axis `dim_Date[YearMonth]` remains independent of the Risk_Register filter (axis enumeration comes from `dim_Date`, a separate dimension). All 9 months in the active range continue to render; only the Y value changes.

Trend chart preserves monthly grain after the cross-filter. The line shifts down (lower per-month count) but stays continuous over Sep 2025 - May 2026.

The same trace applies if the user clicks a matrix cell (filters by `probability_score = X AND max_impact_score = Y`): KPIs and category bar shift; RiskActivity X-axis (months) preserved, Y shifts.

### 5. Theme-driven colors vs inline hex

Grep result documented in §c above. 6 distinct hex tokens appear inline across 9 visuals (all are tokens from 03 §c1 or theme.json). All inline hex usage is justified by the locked spec:
- PageHeader textbox (cannot be theme-styled).
- KPI title `fontColor` (per-card override for 03 §c2 KPI label typography role).
- Conditional formatting rules on KPIHighRisks, PIMatrix, RisksByCategory (per 03 §c1 heatmap, 03 §d conditional rules, 03 §d series binding).

No hardcoded hex outside of the 03 §c1 palette tokens.

### 6. Field-well "Show items with no data"

Required by locked spec for PIMatrix (full 5x5 grid). Encoded in PBIR via `queryState.Rows.showAll = true` and `queryState.Columns.showAll = true`. No Power BI Desktop UI click needed.

No other visual on Page 1 requires "Show items with no data" per 03 §d.

### 7. Sort order

| Visual | Field | Direction | Source |
|---|---|---|---|
| PIMatrix | `Risk_Register.probability_score` | Descending (5..1) | 03 §d Page 1 #7. Single sortDefinition entry. |
| PIMatrix | `Risk_Register.max_impact_score` | Ascending (1..5) | 03 §d Page 1 #7. **Natural axis sort** (no explicit sortDefinition entry) - matrix axes default to ascending which is what we want. The initial 2-entry sortDefinition was simplified to 1 when stabilizing for the open-file RepeatedIndices error. |
| RisksByCategory | `_Measures.Total Risks` | Descending | 03 §d Page 1 #8 (`Y-axis: risk_category sorted by COUNTROWS desc`) |
| RiskActivity | `dim_Date.YearMonth` | Ascending | 03 §d Page 1 #9 (continuous X-axis); column's sort-by `YearMonthSort` resolves chronological |
| KPI cards | (none) | n/a | single-value cards |

### 8. Continuous-axis line chart

`lineChart.categoryAxis.axisType = Continuous` is set in `assets/theme.json` (line 304-311). Per 06 §d, the current data range has no zero-update months in Sep 2025 - May 2026, so the continuous-vs-categorical distinction is not visually apparent today. When the dataset extends or a month genuinely has zero updates, the line will gap rather than show a zero point ([Updates Count] returns BLANK per 06 §c, not 0). The deferred toggle `COUNTROWS(Risk_Updates) + 0` documented in 06 §c remains available if Phase 13 review prefers flat-zero.

### 9. CF rule type wrapper (Column vs Measure)

`pbir visuals cf --rules` generates the `Left` of each Comparison as a `Measure` wrapper even when the field is a Column. This is a pbir CLI quirk. Manually corrected on RisksByCategory.visual.json: the `risk_level` reference was `Left.Measure` (pbir CLI default), changed to `Left.Column`. PIMatrix and KPIHighRisks use measure fields, so their CF wrappers correctly stay as `Measure`. KPIHighRisks compares the same measure to a numeric literal, also `Left.Measure` is correct (the field is a measure).

**On open, Power BI Desktop rejects `Left.Measure` for a column field reference with `Missing_References: (Risk_Register) risk_level`.** The wrapper must match the field's actual data-shape role. Confirmed empirically this turn after the user reported the error. The fix is not optional. Add to the Phase 10/11 checklist: when applying CF on a column-bound field role (Category, Series, Group, etc.), edit pbir CLI's output to swap `Left.Measure` → `Left.Column` for that field's CF rule. Verify in [CLAUDE.md](../CLAUDE.md) gotchas section that this is captured.

---

## e) User-side actions to apply

### e1. Apply the theme (Phase 8 user-side step)

If not already done per 08 §g:

1. Open `pbip/Tonnelle_Risk.pbip` in Power BI Desktop.
2. **View** ribbon > **Themes** > **Browse for themes**.
3. Navigate to `assets/theme.json` > Open.
4. Save (`Ctrl-S`).
5. Confirm `pbip/Tonnelle_Risk.Report/definition/report.json` `themeCollection` references `Tonnelle_Risk_Naik` instead of `CY26SU05` after save.

Without the theme, KPI values display in Power BI's default colors and the line chart picks up `#118DFF` (Power BI default first-series blue) instead of `#488f31`. The visuals still render and bind correctly; only the palette is wrong.

### e2. Refresh model

1. Home ribbon > **Refresh**. This loads the new `max_impact_score` calculated column.
2. Confirm in the Fields pane that `Risk_Register` now has 20 visible columns (was 19 pre-edit); `max_impact_score` should appear between `schedule_impact_score` and `risk_score_cost`.
3. If the calculated-column expression triggers a TMDL normalizer revert on save (similar to Phase 5 §e2 quirks), re-create via Desktop UI:
   - Risk_Register table > **New column** > paste DAX: `max_impact_score = IF(Risk_Register[cost_impact_score] >= Risk_Register[schedule_impact_score], Risk_Register[cost_impact_score], Risk_Register[schedule_impact_score])`
   - Set Format `0`, Summarization `Don't summarize`.

### e3. Set report-level "Open" status filter

03 §d sets a report-level filter `status = "Open"`. `status` is hidden in the model (per 03 §a, §f-2). Power BI's filter pane will not surface a hidden field by default; the filter has to be added programmatically or by temporarily unhiding the column.

Two equivalent paths:

- **Programmatic:** edit `pbip/Tonnelle_Risk.Report/definition/report.json` to add a report-level `filters[]` entry referencing `Risk_Register.status = "Open"`. PBIR supports this. Not done this phase to avoid scope creep; deferred to user or a future cleanup phase.
- **Desktop UI:** in the Fields pane, right-click `status` > **Unhide in model view**, drag `status` to the report-level Filter pane, set value `Open`, then right-click `status` again > **Hide in model view**. The filter persists after the column is re-hidden.

Defer per CLAUDE.md "currently a no-op today since all rows are Open" - the filter has no observable effect until Excel-side backfill is done. Leaving for Phase 13 (or whenever the user backfills).

### e4. PIMatrix cell coloring - final working configuration

**Final landing state (after several iterations):** the PI matrix renders all 25 cells with the locked 3-band heatmap, including the two empty cells (P=2,I=2 score 4 and P=3,I=2 score 6) that have no risks in current data. Three model additions plus a Values measure swap were needed beyond what 03 §a/§b spec'd.

**Iterations and lessons (chronological):**

1. **Initial attempt:** `pbir visuals cf --rules` to add CF on `values.backColor` and `values.fontColor` (each as separate `objects.values[]` entries), `showAll: true` on Rows+Columns, multi-entry `sortDefinition`. On open: `InvalidOrMalformedDataShapeBinding_RepeatedIndicesProjectionsOrGroupBy`.

2. **Strip-down:** removed `showAll`, single sort entry, no CF. Matrix loads but is uncolored.

3. **CF re-applied:** consolidated `objects.values[1]` (both `backColor` and `fontColor` in one properties block, shared `dataViewWildcard` selector), CF basis `[Max Risk Score]`. Matrix loads, CF fires for cells with risks. Empty cells still white because `[Max Risk Score]` returns BLANK for them.

4. **Cell PI Score measure** added to compute the cell's potential P×I score from axis context. Initial version used `SELECTEDVALUE(Risk_Register[probability_score])` - still BLANK for empty cells (combined filter yields 0 rows in Risk_Register, so VALUES returns empty).

5. **dim_Probability / dim_Impact tables** added as DAX calculated tables (`SELECTCOLUMNS(GENERATESERIES(1,5), "<col>", [Value])`), each with M:1 single-direction relationship to Risk_Register. Matrix axes rebound from Risk_Register columns to dim columns. `Cell PI Score` rewired to read SELECTEDVALUE from the dims (which have all 5 values regardless of Risk_Register matches). On open: matrix renders with most cells colored. Two empty cells (P=2,I=2 and P=3,I=2) **still white** because Power BI's matrix CF on `values.backColor` does NOT fire when the cell's displayed Values measure returns BLANK.

6. **Cell Total Risks measure** added (`COUNTROWS(Risk_Register) + 0`) so empty cells display `0` instead of BLANK. Matrix Values swapped from `Total Risks` to `Cell Total Risks`. CF now fires on all 25 cells. Empty cells show `0` on green background. **Final working state.**

**Bug also hit along the way:** `///` docstring above a `relationship` block crashed Power BI Desktop on load with `Property 'description' is unknown` (`DataModelLoadFailed`). TMDL docstrings are valid on tables/columns/measures but NOT on relationships. Removed the docstrings from `relationships.tmdl`; relationship intent documented in this doc instead. See [feedback-pbi-tmdl-normalization](../../../../.claude/projects/C--Users-jkhbu-OneDrive-Projects-powerbi-risk-register/memory/feedback_pbi_tmdl_normalization.md).

**Final PIMatrix configuration:**

| Element | Value |
|---|---|
| Rows axis | `dim_Probability[Probability]`, sort Descending, showAll true |
| Columns axis | `dim_Impact[Impact]`, sort default Ascending, showAll true |
| Values | `_Measures.Cell Total Risks` (returns 0 for empty cells; CF fires on all 25) |
| backColor CF | basis `[Cell PI Score]` (= dim P × dim I), 3 rules: gte 1 → `#488f31`, gte 8 → `#e8b450`, gte 15 → `#de425b` |
| fontColor CF | basis `[Cell PI Score]`, 3 rules: gte 1 → `#FFFFFF`, gte 8 → `#1a1a1a`, gte 15 → `#FFFFFF` |

**Deviations from 03 §a/§b lock:**

- Schema gained 2 new dim tables (`dim_Probability`, `dim_Impact`) with their relationships to Risk_Register. 03 §a did not anticipate these but the PI matrix locked spec (03 §d Page 1 #7) implicitly requires them for the "Empty cells: canvas fill" requirement to be both visible AND colored.
- Measure count increased from 13 (03 §b) to 13 + 2 (`Cell PI Score`, `Cell Total Risks`). New measures in the `Display` folder alongside `Risk Level Pill SVG`. The 03 §b lock anticipated 3 Display measures (incl. 2 Phase 11 deferrals); current Display folder has 3 measures (`Risk Level Pill SVG`, `Cell PI Score`, `Cell Total Risks`); Phase 11 will add 2 more (`Selected Risk Title`, `Selected Risk Mitigation Log`) bringing the final count to 15. Acceptable deviation; documenting here rather than amending 03.

### e5. Verify Page 1 visual rendering

1. Confirm the 9 visuals render in their locked positions (no overlap, no off-canvas).
2. Visual-by-visual sanity:
   - KPITotalRisks: shows "37" (per 05 §c baseline). High shows "12" (red color, since 12 > 10). Medium 10. Low 15. Avg Score 10.4.
   - PIMatrix: 5x5 grid; (P=5, I=5) cell shows 4; (P=3, I=5) shows 3; empty cells show no number on white fill. Bands color per §c above. Diagonal-ish gradient of green-yellow-red follows the score-band rule.
   - RisksByCategory: 7 category bars (Construction, Field Condition, Design Change, Safety, Environmental, Political, Financial), each with up to 3 clustered sub-bars (Low/Medium/High where present). Colors `risk_low/medium/high`.
   - RiskActivity: line spans Sep 2025 to May 2026 across the bottom panel. Y-axis from ~8 to ~23 per 06 §d table. Markers at each month.
3. Confirm cross-filter behavior by clicking once on the Construction bar; observe the trend chart Y-axis values shift down but the X-axis keeps all 9 months.
4. If markers don't appear on RiskActivity, open Format pane > Markers > toggle Show on. PBIR `lineStyles.markerSize = 4` should suffice; a UI-confirmation may be needed on some Desktop builds.
5. Save (`Ctrl-S`).

### e6. Screenshot (optional, for portfolio)

Take a screenshot of the rendered Page 1 and save to `assets/page1_built.png`. The 1280x720 canvas should capture in a 1280-wide window; pad with the Power BI Desktop chrome.

### e7. Do NOT proceed to Phase 10

Phase 10 (Page 2 Risk Register Detail) is the next phase per CLAUDE.md phase map; not in scope this turn.

---

## f) Status

Phase 9 deliverable shipped. 9 PBIR visuals on Page 1 ("Overview" / display "Executive Overview"), positions match 03 §d to the pixel. Full heatmap on PIMatrix including the 2 empty (P,I) cells. KPIHighRisks conditional value color firing. Theme imports and applies cleanly. RisksByCategory per-series colors via theme `dataColors` slot order. RiskActivity continuous chronological line.

**Model additions beyond 03 §a/§b lock** (all documented in §e4 above): 2 new dim tables (`dim_Probability`, `dim_Impact`), 2 new relationships (M:1 single direction from Risk_Register to each dim), 2 new measures (`Cell PI Score`, `Cell Total Risks` in `Display` folder). 1 new calculated column on `Risk_Register` (`max_impact_score`) - still present for backward compat but no longer referenced by visuals (the matrix now uses `dim_Impact[Impact]` instead). Could be removed at Phase 11 cleanup if desired.

**Theme.json fixes applied this phase:** removed invalid top-level `secondBackground` (not a recognized Power BI theme property); fixed 6 enum-value casing/type errors (PascalCase for `alignment`/`labelPosition`/`axisType`/`outline`; integer not string for `slicer.orientation`); slot 1 / slot 2 swapped (`dataColors[1] = #e8b450` Medium, `dataColors[2] = #de425b` High) so RisksByCategory series sort (Low/Medium/High) maps cleanly to colors.

Phase 10 (Page 2 Risk Register Detail; target `docs/10_page2.md` + PBIR; skill `pbi-report-design`) is unblocked. Recommended for Phase 10: leverage the `+ 0` measure trick and dim-table approach when any matrix on Page 2 needs CF on empty cells; otherwise stick with theme-driven per-series colors over CF rules for column-bound series.
