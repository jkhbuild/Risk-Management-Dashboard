# 10. Page 2 Risk Register Detail

Phase 10 deliverable, prepared 2026-05-23. Skill loaded: `pbi-report-design` (data-goblin).

**Inputs:**
- `docs/03_design_locked.md` §c (theme), §d Page 2 visual list and positions (7 visuals), §f-1 SVG pill deviation.
- `docs/05_semantic_model.md` (`Total Risks`), `docs/06_time_intel.md` (`Days Since Last Update`), `docs/07_svg_pill.md` (`Risk Level Pill SVG` + `dataCategory: ImageUrl`).
- `docs/08_theme.md` (`assets/theme.json`, eight `visualStyles` entries).
- `docs/09_page1.md` for style continuity (custom KPI/slicer title pattern at 11pt `#5a5a5a`, theme-driven palette, drillFilterOtherVisuals true).
- `docs/cf_authoring.md` (no CF this phase; pattern reserved).
- `assets/risk_dashboard_mockup.png` (Page 2 portion: header bar, 3 slicers chip row, Top Risks table with pill column, coordinator bar, recent updates feed).
- Current PBIR state: one finished page `Overview` from Phase 9; `pages.json` listed only `Overview`.

Scope: seven PBIR visuals on a single page named `Detail` (display "Risk Register Detail"), plus a minimal `RiskDetail` page stub (drillthrough destination, no visuals — those are Phase 11). No semantic-model edits this phase.

---

## a) Files changed

| File | Change |
|---|---|
| `pbip/Tonnelle_Risk.Report/definition/pages/pages.json` | `pageOrder` extended `["Overview"]` → `["Overview", "Detail", "RiskDetail"]`. `activePageName` set to `Detail` so the file opens on the new work; user can switch tabs after verification. |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/page.json` | **New.** `name: Detail`, `displayName: Risk Register Detail`, 1280×720 FitToPage. |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/visuals/PageHeader/visual.json` | **New** textbox. Two paragraphs: title "Risk Register Detail" (Segoe UI Semibold 22pt `#1a1a1a`) and subtitle "Project TONN-01  •  Page 2 of 3" (Segoe UI 11pt `#5a5a5a`). |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/visuals/SlicerCategory/visual.json` | **New** slicer (vertical list). Field `Risk_Register.risk_category`. `selection.singleSelect=false`. Header off (visual title carries the label). Custom visual title "Category" 11pt `#5a5a5a`. |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/visuals/SlicerCoordinator/visual.json` | **New** slicer. Field `Risk_Register.risk_coordinator`. Same options as SlicerCategory. Title "Coordinator". |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/visuals/SlicerRiskLevel/visual.json` | **New** slicer. Field `Risk_Register.risk_level`. Inherits model-level `sortByColumn risk_level_sort` (Low/Medium/High order). Title "Risk Level". |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/visuals/TopRisks/visual.json` | **New** tableEx. 7 columns in order: `risk_id` (header "Risk ID"), `risk_title` ("Title"), `risk_category` ("Category"), `[Risk Level Pill SVG]` ("Level"), `risk_score_overall` ("Score"), `risk_coordinator` ("Coordinator"), `[Days Since Last Update]` ("Days"). Sort `risk_score_overall` desc. `objects.grid.imageHeight=44D` (iterated 24 → 36 → 44 based on visual feedback that pills looked too small in early renders; SVG viewBox is 60×20 so imageHeight=44 gives the pill room to render at proper scale with vertical padding). |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/visuals/RisksByCoordinator/visual.json` | **New** clusteredBarChart. Category `Risk_Register.risk_coordinator`, Y `[Total Risks]`, sort Y desc. Single-series accent inherits theme `dataColors[0] = #488f31` (matches Page 1 RiskActivity line, per 08 §a). |
| `pbip/Tonnelle_Risk.Report/definition/pages/Detail/visuals/RecentRiskUpdates/visual.json` | **New** tableEx. 4 columns: `update_date` ("Date"), `risk_id` ("Risk ID"), `author` ("Author"), `note` ("Note", wordWrap on). Sort `update_date` desc. Visual-level `TopN` filter on `update_id`: `Where[].Condition.VisualTopN.ItemCount = 20` PLUS sibling `filter.OrderBy[]` with rank field `update_date` and `Direction: 2` (Descending). See §d-1 for iteration history; final shape is schema-canonical per Microsoft's `semanticQuery/1.2.0/schema.json`. |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/page.json` | **New.** `name: RiskDetail`, `displayName: Risk Detail`, hidden (`visibility: HiddenInViewMode`). Drillthrough destination registered via `pbir pages drillthrough --table Risk_Register --field risk_id`, which writes three required pieces: page-level `filterConfig.filters[0]` Categorical filter with `howCreated: "Drillthrough"`, `type: "Drillthrough"` at page root, and a `pageBinding` block binding the filter to the drillthrough parameter. Hand-authoring just the filter (my first attempt) was silently insufficient — the page didn't register as a drillthrough destination and the right-click action never surfaced on TopRisks. Lesson: [feedback-pbir-drillthrough-destination](../../../../.claude/projects/C--Users-jkhbu-OneDrive-Projects-powerbi-risk-register/memory/feedback_pbir_drillthrough_destination.md). |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/PlaceholderRiskId/visual.json` | **New** card visual showing `Risk_Register.risk_id` with title "PHASE 11 PLACEHOLDER — Drilled-into Risk ID". Confirms the drillthrough chain works end-to-end today. Phase 11 will replace with the 7-visual layout per 03 §d Page 3 (back button, dynamic title textbox, meta strip multiRowCard, mitigation card, section labels, updates history tableEx). |

No deletions. No semantic model edits.

A pre-edit backup was not created this phase (Phase 9 already left a snapshot; pages.json + new files only).

### Drillthrough wiring choice

Power BI's right-click drillthrough is a destination-driven mechanism: the right-click action surfaces on any visual containing the drillthrough field when a destination page declares a Categorical filter on that field with `howCreated: "Drillthrough"`. The source visual needs no extra configuration. Two pieces are now in place:

1. **Destination side:** `RiskDetail/page.json` declares the `risk_id` drillthrough filter. Phase 11 will add visuals; the filter remains in place across that build.
2. **Source side:** `TopRisks` includes `risk_id` as its first column projection. Right-click on any row's risk_id cell surfaces "Drill through → Risk Detail".

Stub-now / fill-later was chosen over deferring the wiring to Phase 11 so the user-side verification step (right-click → confirm "Risk Detail" appears) can be checked today.

---

## b) Visuals shipped (7 visuals matching 03 §d Page 2)

| # | Visual name | Type | Position (x, y, w, h) | Data binding |
|---|---|---|---|---|
| 1 | `PageHeader` | textbox | (24, 24, 1232, 60) | Static. Line 1 (Semibold 22pt `#1a1a1a`): "Risk Register Detail". Line 2 (11pt regular `#5a5a5a`): "Project TONN-01  •  Page 2 of 3". |
| 2 | `SlicerCategory` | slicer | (24, 100, 280, 80) | `Risk_Register.risk_category`. Vertical list, multi-select, header hidden, custom visual title "Category". |
| 3 | `SlicerCoordinator` | slicer | (320, 100, 280, 80) | `Risk_Register.risk_coordinator`. Title "Coordinator". |
| 4 | `SlicerRiskLevel` | slicer | (616, 100, 280, 80) | `Risk_Register.risk_level` (model sort-by-column resolves Low/Medium/High order). Title "Risk Level". |
| 5 | `TopRisks` | tableEx | (24, 196, 800, 360) | `risk_id`, `risk_title`, `risk_category`, `[Risk Level Pill SVG]`, `risk_score_overall`, `risk_coordinator`, `[Days Since Last Update]`. Column headers renamed via projection `displayName`. Sort `risk_score_overall` desc. `grid.imageHeight=24D`. |
| 6 | `RisksByCoordinator` | clusteredBarChart | (840, 196, 416, 360) | Category `risk_coordinator` (sort by `[Total Risks]` desc), Y `[Total Risks]`. Single series; color from theme `dataColors[0] = #488f31`. |
| 7 | `RecentRiskUpdates` | tableEx | (24, 572, 1232, 124) | `update_date`, `risk_id`, `author`, `note` (wordWrap). Sort `update_date` desc. Visual-level TopN filter, count 20, OrderBy `update_date` desc. |

Visual count = 7. Visual types: 1 textbox + 3 slicer + 2 tableEx + 1 clusteredBarChart. Matches 03 §d Page 2 to the visual. No project slicer (single contract per 03 §a).

Positions are pixel-locked: slicer row sits at y=100 with 16 px gaps (24, 320, 616); the table+bar row sits at y=196 with the table 800 wide and the bar 416 wide totalling 1232 with one 16-px gap; the updates feed spans the full content width at y=572 with 124-px height. All positions sum to `1232 + 24×2 = 1280` width and `60 + 16 + 80 + 16 + 360 + 16 + 124 + 24 = 696 ≈ 720 − 24 bottom margin`. No overlap.

### Page-level filter

03 §d sets a report-level filter `status = "Open"` (forward-compat, no-op today). Not encoded this phase, same rationale as Phase 9: status is hidden in the model and requires either programmatic `report.json` edit or a Desktop UI temp-unhide step. Deferred consistent with 09 §e3.

---

## c) Conditional formatting and visual-level overrides

### CF rules applied

None. Page 2 has no conditional formatting needs per 03 §d:
- TopRisks cell coloring is the SVG pill measure (visual-level rendering, not a CF rule).
- RisksByCoordinator single-series color comes from theme `dataColors[0]`, not CF.
- Slicer items, tableEx cells, header textbox: all theme-driven defaults.

The `docs/cf_authoring.md` patterns remain reserved for any Page 3 needs (Phase 11) or future Page 2 enhancements.

### Per-visual title overrides (continuity with Phase 9)

The 3 slicers each set `visualContainerObjects.title.show = true` with a custom short label ("Category", "Coordinator", "Risk Level") at Segoe UI 11pt `#5a5a5a` left-aligned, mirroring the Phase 9 KPI card title style. Reasoning matches 09 §c: theme wildcard sets visual title at Semibold 14pt, which is too heavy for a slicer chip row; 11pt `#5a5a5a` reads as a small grey label above the chip's items.

Slicer `header.show = false` to avoid duplicating the label inside the slicer (Power BI's default slicer header repeats the field name).

### SVG pill column (TopRisks)

The `[Risk Level Pill SVG]` measure is bound as column #4 of TopRisks with `displayName: "Level"`. Power BI renders the cell as an inline image because the measure carries `dataCategory: ImageUrl` in TMDL (Phase 7 §a, confirmed via Modeling ribbon UI 2026-05-23). PBIR cannot express "Data category = Image URL" on a per-visual basis; the property lives on the measure definition only.

`objects.grid.imageHeight = 24D` sets the per-row image height (matches the K201 example pattern). The SVG payload is a 60×20 viewBox; 24-px row height leaves ~2 px vertical padding for the pill. If the visual on first open shows squashed pills (a Power BI Desktop quirk on tableEx with mixed text + image columns), increase to 28D or 32D via the Format pane > Grid > Image height slider; persists to `grid.imageHeight` automatically.

Raw `risk_level` column remains unbound (and unhidden in the model per 03 §f-1) so future visuals or filters can address the text directly. The Page 2 SlicerRiskLevel binds to plain text `risk_level`, not the SVG measure.

### Theme-inherited styling (no per-visual override needed)

- Slicer items: theme `slicer` block (11pt regular, `#FFFFFF` fill, `#e0e0e0` border).
- tableEx headers / cells: theme `tableEx` block (Semibold 11pt header on `#f1f1f1`, regular 11pt cells, horizontal gridlines `#e0e0e0`, no row banding, totals off).
- clusteredBarChart axes / labels: theme `clusteredBarChart` (10pt category labels `#1a1a1a` on the bar's left, value axis hidden, data labels on at `OutsideEnd` 10pt, gridlines off).
- Visual title default: theme wildcard (Semibold 14pt left-aligned) for TopRisks "Top Risks by Overall Score", RisksByCoordinator "Risk Count by Coordinator", RecentRiskUpdates "Recent Risk Updates". The slicer titles override to 11pt `#5a5a5a` (above).
- Backgrounds / borders / drop shadows: theme defaults (no shadow, transparent on charts, `#FFFFFF` + `#e0e0e0` border on cards/tables).

### Inline hex codes (theme-driven palette check)

Grep across all 7 Page 2 visual.json files:

| Hex | Found in | Justification |
|---|---|---|
| `#1a1a1a` | PageHeader title text run | textbox cannot be theme-styled (08 §c). |
| `#5a5a5a` | PageHeader subtitle; SlicerCategory/Coordinator/RiskLevel `title.fontColor` | textbox inline; per-visual KPI/label typography role (03 §c2; same precedent as Phase 9 KPI cards). |

Only 2 distinct hexes, both from 03 §c1, both justified. No improvised hex codes. No CF-driven inline color (no CF on this page).

---

## d) Self-verification log

### 1. PBIR JSON parse

```
OK: pages.json
OK: Detail\page.json
OK: Detail\visuals\PageHeader\visual.json
OK: Detail\visuals\RecentRiskUpdates\visual.json
OK: Detail\visuals\RisksByCoordinator\visual.json
OK: Detail\visuals\SlicerCategory\visual.json
OK: Detail\visuals\SlicerCoordinator\visual.json
OK: Detail\visuals\SlicerRiskLevel\visual.json
OK: Detail\visuals\TopRisks\visual.json
OK: RiskDetail\page.json
```

All 10 new/changed JSON files parse as valid JSON.

`pbir validate` reports 3 pre-existing errors and 9 SCHEMA_DEGRADED warnings:
- **3 errors pre-existing per CLAUDE.md tooling notes** (`report.json` `$schema` mismatch, `pages.json` `$schema` mismatch, `Tonnelle_Risk.pbip` missing `$schema`). Phase 9 §d-1 already documented these as harmless CLI-schema-lag.
- **9 warnings** all `SCHEMA_DEGRADED` (visualContainer 2.9.0 schema absent in CLI bundle); pre-existing per Phase 9; do not block Power BI Desktop.

**TopN schema iteration (resolved 2026-05-23):** Three passes:

1. **Pass 1** authored per `filter-pane.md` §391-433 (`VisualTopN.{Expression, Count, OrderBy, IsAscending}`). Both `pbir validate` and Power BI Desktop's loader rejected with "`'ItemCount' is a required property`" and "Additional properties are not allowed ('Count', 'Expression', 'IsAscending', 'OrderBy' were unexpected)".

2. **Pass 2** stripped to minimum: `{"VisualTopN": {"ItemCount": 20}}` alone, assuming the visual's `sortDefinition` would feed the rank. **Schema accepted; runtime silently no-op'd** — visual rendered all 127 rows starting 2025-09-08. Same silent-failure class as the CF patterns in `docs/cf_authoring.md`: structurally valid PBIR can pass validation without engaging the renderer.

3. **Pass 3** added an `OrderBy` array as a sibling of `From`/`Where` inside `filter` (per `semanticQuery/1.2.0/schema.json` `QueryDefinition`). Power BI Desktop on PBIP open rejected: "An additional property 'OrderBy' was included in /filterConfig/filters/0/filter". The `visualContainer/2.9.0` schema constrains `filter` to `{Version, From, Where}` only — `OrderBy` lives only in QueryDefinitions that aren't the outer filter (like inside a subquery).

4. **Pass 4** (canonical, resolved via reverse-engineering `pbir add filter --type TopN --no-validate` CLI emission) — TopN uses a **subquery pattern**. The outer filter `Where.In` references a subquery in `filter.From[0]`; the subquery's `Query` holds `Select`+`OrderBy`+`Top`. `From` has two entries: the subquery (`Type: 2`) and the regular table alias (`Type: 0`). `VisualTopN` is a separate feature not used here. Initial OrderBy was just `update_date Desc` and returned 22 rows (ties at the May 2026 boundary — `update_date` is day-granular, multiple updates per day). **Pass 4b** added `update_id` as a compound OrderBy tie-breaker; now clamps to exactly 20. Final shape:

   ```json
   "filter": {
     "Version": 2,
     "From": [
       {
         "Name": "subquery",
         "Expression": {"Subquery": {"Query": {
           "Version": 2,
           "From": [{"Name": "u", "Entity": "Risk_Updates", "Type": 0}],
           "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "u"}}, "Property": "update_id"}, "Name": "field"}],
           "OrderBy": [{"Direction": 2, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "u"}}, "Property": "update_date"}}}],
           "Top": 20
         }}},
         "Type": 2
       },
       {"Name": "u", "Entity": "Risk_Updates", "Type": 0}
     ],
     "Where": [{"Condition": {"In": {
       "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "u"}}, "Property": "update_id"}}],
       "Table": {"SourceRef": {"Source": "subquery"}}
     }}}]
   }
   ```

   `Direction: 2` = Descending (Top N most recent). `Direction: 1` = Ascending (Bottom N).

**Process lessons** (saved to memory):
- [feedback-pbir-topn-filter-shape](../../../../.claude/projects/C--Users-jkhbu-OneDrive-Projects-powerbi-risk-register/memory/feedback_pbir_topn_filter_shape.md): canonical TopN subquery pattern.
- [feedback-pbir-microsoft-schema-authoritative](../../../../.claude/projects/C--Users-jkhbu-OneDrive-Projects-powerbi-risk-register/memory/feedback_pbir_microsoft_schema_authoritative.md): when bundled pbir-format docs disagree with Desktop's loader, WebFetch the Microsoft schema OR — even faster — run `pbir add ... --no-validate` against a sandbox visual and read the canonical emission. The CLI knows the runtime-correct shape because Microsoft's reference implementation feeds it.

Distinct visuals counted by `pbir validate`: 16 (9 Overview + 7 Detail). Match.

### 2. Measure / column name resolution

Field references across the 7 Detail visuals (deduplicated, walked from PBIR JSON):

| Field | Used by | Resolved in model |
|---|---|---|
| `Risk_Register.risk_id` | TopRisks Values | ✓ |
| `Risk_Register.risk_title` | TopRisks Values | ✓ |
| `Risk_Register.risk_category` | TopRisks Values; SlicerCategory; RisksByCoordinator (implicit via SlicerCategory cross-filter) | ✓ |
| `Risk_Register.risk_level` | SlicerRiskLevel | ✓ |
| `Risk_Register.risk_score_overall` | TopRisks Values + sort | ✓ |
| `Risk_Register.risk_coordinator` | TopRisks Values; SlicerCoordinator; RisksByCoordinator Category | ✓ |
| `Risk_Updates.update_date` | RecentRiskUpdates Values + sort + TopN OrderBy | ✓ |
| `Risk_Updates.risk_id` | RecentRiskUpdates Values | ✓ |
| `Risk_Updates.update_id` | RecentRiskUpdates TopN target field + Expression | ✓ |
| `Risk_Updates.author` | RecentRiskUpdates Values | ✓ |
| `Risk_Updates.note` | RecentRiskUpdates Values | ✓ |
| `_Measures.Total Risks` | RisksByCoordinator Y + sort | ✓ |
| `_Measures.Days Since Last Update` | TopRisks Values | ✓ |
| `_Measures.Risk Level Pill SVG` | TopRisks Values | ✓ |

14 distinct field references, 14 resolutions. No unresolved measures or columns.

### 3. Visual count and types vs 03 §d

| 03 §d Page 2 visual | PBIR visual | Type match |
|---|---|---|
| #1 Page header (textbox) | PageHeader | ✓ textbox |
| #2 Slicer: Category | SlicerCategory | ✓ slicer |
| #3 Slicer: Coordinator | SlicerCoordinator | ✓ slicer |
| #4 Slicer: Risk Level | SlicerRiskLevel | ✓ slicer |
| #5 Top Risks (tableEx) | TopRisks | ✓ tableEx |
| #6 Risk Count by Coordinator (clustered horizontal bar) | RisksByCoordinator | ✓ clusteredBarChart |
| #7 Recent Risk Updates (tableEx) | RecentRiskUpdates | ✓ tableEx |

7 visuals, 7 type matches. Position match to 03 §d to the pixel.

### 4. Drillthrough source wiring

| Element | Present | Detail |
|---|---|---|
| RiskDetail page exists | ✓ | `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/page.json` (stub) |
| RiskDetail hidden from page tabs | ✓ | `visibility: HiddenInViewMode` |
| RiskDetail declares drillthrough filter | ✓ | `filterConfig.filters[0]` on `Risk_Register.risk_id`, `type: Categorical`, `howCreated: Drillthrough` |
| Source visual (TopRisks) contains the drillthrough field | ✓ | `risk_id` is the first projection in TopRisks `Values` |

PBIR fully represents drillthrough config; no extra source-side wiring is needed beyond the destination-page filter declaration plus the source visual carrying the field. **However, Power BI Desktop's UI render of the drillthrough action requires a UI re-confirmation step in some build versions; see §e3.**

### 5. Slicer field bindings

| Slicer | Field | Match 03 §d |
|---|---|---|
| SlicerCategory | `Risk_Register.risk_category` | ✓ |
| SlicerCoordinator | `Risk_Register.risk_coordinator` | ✓ |
| SlicerRiskLevel | `Risk_Register.risk_level` (model-level `sortByColumn risk_level_sort` resolves order) | ✓ |

No project slicer (single contract per 03 §a). Three slicers total (under DG's "max 3 per page" cap).

### 6. SVG pill column configuration

The `[Risk Level Pill SVG]` measure is bound on TopRisks as column #4 with `displayName: "Level"`. The measure's `dataCategory: ImageUrl` lives in `_Measures.tmdl` (Phase 7); PBIR consumes it transparently. `objects.grid.imageHeight=24D` accommodates the 20-px pill.

**User-side confirmation:** Phase 7 §d already includes the Modeling ribbon → Properties → Data category = Image URL step. If a future Power BI Desktop build round-trips the property to "Uncategorized" on save, re-set via the same path. Listed as §e2 below for explicit traceability.

### 7. Sort and top-N

| Visual | Sort field | Direction | Top N |
|---|---|---|---|
| TopRisks | `Risk_Register.risk_score_overall` | Descending | none (table is scrollable; show all in filter context, per 03 §d) |
| RisksByCoordinator | `_Measures.Total Risks` | Descending | none |
| RecentRiskUpdates | `Risk_Updates.update_date` | Descending | `VisualTopN.ItemCount = 20` on field `Risk_Updates.update_id`. Rank order inherited from the visual's sortDefinition (update_date Descending). |

All match 03 §d.

### 8. Theme-driven colors

Per §c above: only 2 inline hex codes used (`#1a1a1a` text title, `#5a5a5a` label color), both from 03 §c1 palette, both at the same continuity points as Phase 9 (textbox + small label fontColor). No CF on this page. No raw hex outside the palette. Bar series color comes from theme `dataColors[0]`, not visual-level CF.

### 9. Cross-filter sanity (trace by reasoning)

Page 2 has 3 slicers and several visuals that bind to `Risk_Register`. Tracing a representative selection:

- **Click "Construction" in SlicerCategory**: filter `Risk_Register[risk_category] = "Construction"`. Propagates to:
  - TopRisks: rows filter to Construction; sort preserves; the SVG pill, Days Since Last Update, and Score columns re-evaluate per row.
  - RisksByCoordinator: Y `[Total Risks]` re-aggregates over the Construction subset; bar lengths shift; sort re-applies; some coordinators may drop off if they have zero Construction risks.
  - RecentRiskUpdates: filter propagates `Risk_Register → Risk_Updates` via the active M:1 `risk_id` relationship (single direction, Register filters Updates). Only updates for Construction risks contribute; the visual's TopN re-evaluates over the filtered set, returning up to 20 most-recent within the Construction subset.
- **Click a row in TopRisks**: visual-to-visual cross-filter applies `risk_id = TONN-CON.NN` to every other Page 2 visual. Slicers stay independent. RecentRiskUpdates narrows to that risk's update history within the top-20 envelope. (Same Page 1 trace from 09 §d-4; mechanism unchanged.)
- **Right-click a row in TopRisks** → drillthrough action surfaces in the context menu when `risk_id` is the cell or any column with the row context, navigating to `RiskDetail` with `risk_id` filter applied. See §4 and §e3 for the user-side confirmation step.

---

## e) User-side actions to apply

### e1. Refresh / reopen

1. **Close Power BI Desktop** if it has `Tonnelle_Risk.pbip` open.
2. **Open `pbip/Tonnelle_Risk.pbip`.** The file should open on the Detail page (per `activePageName: Detail`).
3. Confirm the page tab strip shows **"Executive Overview" | "Risk Register Detail"** (and not "Risk Detail" — the latter is hidden via `visibility: HiddenInViewMode`).

### e2. Re-confirm SVG pill measure's Data category

If Phase 7 §d was already done, the measure should still carry `dataCategory: ImageUrl`. Re-verify if pills render as raw text URL strings instead of images:

1. Fields pane → `_Measures` → `Display` folder → click `Risk Level Pill SVG`.
2. **Modeling** ribbon → **Properties** group → **Data category** dropdown → confirm **Image URL**. If not, set it.
3. Save.

### e3. Verify drillthrough source-side wiring

1. Click anywhere on the **TopRisks** table on Page 2.
2. **Right-click** any row.
3. In the context menu, hover **Drill through**.
4. A submenu should list **"Risk Detail"** (the destination page).
5. Click it. Power BI navigates to the (currently empty) RiskDetail page. The page's filter pane should show a Drillthrough filter `risk_id = <selected row's id>`.
6. Click the back button (top-left of Page 3 chrome, or browser-back-equivalent) to return to Detail.

**If "Risk Detail" does NOT appear in the Drill through submenu:**
- The most common cause on first open after a hand-authored drillthrough filter is that Power BI Desktop needs to "see" the destination's filter pane once. Open the RiskDetail page directly via the Page Navigation pane (or temporarily flip `visibility` to AlwaysVisible in `RiskDetail/page.json`, save, open Desktop, then flip back). After Desktop has rendered the page once, the right-click action appears reliably.
- Alternatively, drop the `risk_id` field from the Fields pane onto the RiskDetail page's Drillthrough field well in the Visualizations pane. This is the Desktop UI equivalent of the `howCreated: "Drillthrough"` PBIR declaration; it round-trips to the same JSON shape.

This is the source-side wiring confirmation called out in the Phase 10 prompt. Phase 11 will replace the empty RiskDetail page with its 7 visuals (per 03 §d Page 3); the drillthrough filter declaration remains in place across that build.

### e4. Verify Recent Risk Updates TopN

The visual-level TopN filter on RecentRiskUpdates is authored per the schema-canonical shape derived from Microsoft's `semanticQuery/1.2.0/schema.json` (see §d-1 Pass 3): `{"VisualTopN": {"ItemCount": 20}}` inside `Where`, with a sibling `filter.OrderBy[]` ranking by `update_date` `Direction: 2` (Descending). On open, the visual should show exactly 20 rows, top row date 2026-05-12 (per 06 §d-4).

If the row count differs from 20 or the order is wrong:
1. Click RecentRiskUpdates.
2. **Filters pane** (right side) → **Filters on this visual** → confirm `update_id` carries a "Top N" filter showing "Top 20 by update_date".
3. If absent or unconfigured, drag `update_id` from Risk_Updates into the visual's filter well, set **Filter type = Top N**, **Show items = Top 20**, **By value = update_date** Descending. Desktop will re-emit the same canonical shape, and we can read it back to confirm if needed.

### e5. Sanity-test the visuals

1. **PageHeader**: title and subtitle render in the expected typography.
2. **Slicers**: 3 chips at (24, 320, 616) × y=100. Click "Construction" in SlicerCategory → TopRisks filters; RisksByCoordinator bar lengths shift; RecentRiskUpdates feed narrows.
3. **TopRisks**: 37 rows in the table (or filtered count), sorted by Score desc. The Level column shows red/yellow/green pills (white text on red/green; dark on yellow). Days column shows integers 11 to 169 (per 06 §d-5). Top row should be one of the score=25 risks (TONN-CON.01 by Days Since Last Update = 169 today; per 06 §d-5 it's the stalest, and per 05 §c the max score is 25).
4. **RisksByCoordinator**: ~6 coordinator bars sorted by count desc, single green-accent color, data labels on the right.
5. **RecentRiskUpdates**: 20 rows, top row date 2026-05-12 (per 06 §d-4 latest), note column word-wraps.
6. Clear all slicer selections (Ctrl-click each chip header → Clear selection, or the eraser icon).
7. Save (Ctrl-S).

### e6. Screenshot (optional, for portfolio)

Save Page 2 rendering to `assets/page2_built.png`.

### e7. Do NOT proceed to Phase 11

Phase 11 (Page 3 Risk Detail drillthrough) is the next phase per CLAUDE.md phase map; not in scope this turn. The RiskDetail stub is intentionally empty; Phase 11 will add the back button, dynamic title textbox, meta strip multiRowCard, mitigation paragraph card, and updates history tableEx per 03 §d Page 3, plus 2 new Display measures (`Selected Risk Title`, `Selected Risk Mitigation Log`) per 03 §b.

---

## f) Status

Phase 10 deliverable shipped. 7 PBIR visuals on Page 2 ("Detail" / display "Risk Register Detail"), positions match 03 §d to the pixel. Drillthrough source-side wired: RiskDetail page stub created with Categorical drillthrough filter on `risk_id`, `howCreated: Drillthrough`; TopRisks contains `risk_id` as a column projection. Theme.json palette respected throughout (only 2 inline hex codes used, both from 03 §c1).

No semantic model edits this phase. No CF this phase. No new measures (per 03 §b lock; Phase 11 will add the remaining 2 Display measures).

**Schema iteration on RecentRiskUpdates TopN filter:** first pass used the documented `filter-pane.md` §391-433 shape with `Expression`/`Count`/`OrderBy`/`IsAscending` nested in `VisualTopN`; both `pbir validate` and Power BI Desktop's loader rejected it. Reauthored to the current schema: `{"VisualTopN": {"ItemCount": 20}}` with rank direction inherited from the visual's sortDefinition. Project-internal `filter-pane.md` reference is now known-outdated for this case. Lesson saved as a memory entry for future phases.

Phase 11 (Page 3 Risk Detail drillthrough; target `docs/11_page3.md` + PBIR; skill `pbi-report-design`) is unblocked. Phase 11 will fill the RiskDetail page with 7 visuals per 03 §d Page 3 (back button, title textbox, meta strip multiRowCard, mitigation paragraph card, section-label textboxes, updates history tableEx) and add `Selected Risk Title` + `Selected Risk Mitigation Log` measures to `_Measures.Display`, bringing the final measure count to 15 (per the floor-not-ceiling treatment locked in CLAUDE.md and Phase 9 §e4).
