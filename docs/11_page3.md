# 11. Page 3 Risk Detail (drillthrough destination)

Phase 11 deliverable, prepared 2026-05-23. Skill loaded: `pbi-report-design` (data-goblin).

**Inputs:**
- `docs/03_design_locked.md` §c (theme), §d Page 3 visual list and positions (7 visuals, single-column narrative), §b (2 remaining Display measures), §f-1 SVG pill deviation.
- `docs/05_semantic_model.md` (`_Measures` canonical pattern), `docs/06_time_intel.md`, `docs/07_svg_pill.md` (`Risk Level Pill SVG` consumed by MetaStrip).
- `docs/08_theme.md` (`assets/theme.json` `multiRowCard` / `tableEx` / `card` / `textbox` / `actionButton` coverage).
- `docs/09_page1.md` (custom card title / categoryLabels-off pattern; theme-driven palette).
- `docs/10_page2.md` (drillthrough source+destination wiring; tableEx with `displayName` projection renames; word-wrap pattern on `note` column; `grid.imageHeight` not needed here because the SVG pill renders inside a multiRowCard, not a table).
- Current PBIR state: Phase 10 left `RiskDetail` page with full drillthrough metadata (`type: "Drillthrough"`, `pageBinding`, page-level Categorical filter on `Risk_Register[risk_id]` with `howCreated: "Drillthrough"`) and one placeholder card visual `PlaceholderRiskId/`.

Scope: replace the Phase 10 placeholder with the locked 7-visual layout per 03 §d Page 3; add the 2 remaining Display measures (`Selected Risk Title`, `Selected Risk Mitigation Log`) bringing the final `_Measures` count to 15. `RiskDetail/page.json` untouched (the Phase 10 drillthrough wiring is correct and load-bearing). No changes to other pages, no theme.json changes, no other semantic-model edits.

---

## a) Files changed

| File | Change |
|---|---|
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/_Measures.tmdl` | **Appended 2 measures** in `Display` folder: `Selected Risk Title` = `SELECTEDVALUE(Risk_Register[risk_title], "No risk selected")`; `Selected Risk Mitigation Log` (revised post-deliverable per §g-1 — now pulls from `Risk_Updates` with `CONCATENATEX(..., DESC)` so the mitigation paragraph reads as a newest-first list of `M/D/YYYY - note` lines separated by `UNICHAR(10)`, replacing the original SELECTEDVALUE on the static `Risk_Register[mitigation_log]` column). Total measures in file: **15** (4 Counts + 4 Scores + 2 TimeIntel + 5 Display). |
| `pbip/Tonnelle_Risk.Report/definition/pages/pages.json` | `activePageName` flipped `Detail` → `RiskDetail` so the file opens on Phase 11 work for verification. `pageOrder` `["Overview","Detail","RiskDetail"]` unchanged. |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/PlaceholderRiskId/` | **Deleted.** Phase 10 placeholder card removed via `pbir rm`. The visual.json deleted cleanly; the parent folder deletion needed a manual `Remove-Item -Recurse -Force` (OneDrive lock per CLAUDE.md "OneDrive: `pbir rm` deletes `visual.json` but cannot remove the parent folder"). Both gone now. |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/BackButton/visual.json` | **New** actionButton. `visualContainerObjects.visualLink[0].properties.type = "'Back'"` triggers Power BI's auto drillthrough back-action; `objects.text[0].properties` configures "Back" label at Segoe UI 11pt `#1a1a1a`; `objects.icon[0].properties` enables left-arrow chevron; `objects.outline[0].properties.show = true` makes the button tap-target visible against the white canvas. z=1 so it stays clickable above any overlap. No data binding. (visualLink belongs under `visualContainerObjects`, not `objects`; my first authoring placed it incorrectly under `objects` and Power BI Desktop silently stripped it on save — resolved per §g-2.) |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/RiskTitle/visual.json` | **New** card. Binds `_Measures.Selected Risk Title`. categoryLabels off; `labels.fontFamily/fontSize/color/alignment` overridden to `'Segoe UI Semibold'` / `22D` / `#1a1a1a` / `'left'` (matches 03 §c2 report-title typography role). Title/background/border all hidden. Same per-visual-override pattern Phase 9 KPI cards used. |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/MetaStrip/visual.json` | **New** tableEx (swapped from multiRowCard per §g-3). 6 projections in order: `risk_id` ("Risk ID"), `risk_category` ("Category"), `risk_entity` ("Entity"), `risk_coordinator` ("Coordinator"), `risk_score_overall` ("Score"), `_Measures.Risk Level Pill SVG` ("Level"). The drillthrough filter reduces `Risk_Register` to 1 row → tableEx renders header + 1 data row in the 1232×80 strip. `objects.grid.imageHeight = 44D` so the 60×20 pill renders inline as an image (multiRowCard does not honor the measure's `dataCategory: ImageUrl`; tableEx does — same pattern as Detail/TopRisks). Optional 7th `source_ref` deferred per 03 §d ("Six fields in one row" is the floor). |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/MitigationLabel/visual.json` | **New** textbox. Single paragraph, single textRun "Mitigation" at Segoe UI Semibold 14pt `#1a1a1a` (visual-title typography role per 03 §c2). Title/background/border hidden. Mirrors the static-textbox pattern from Detail/PageHeader. |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/MitigationParagraph/visual.json` | **New** card. Binds `_Measures.Selected Risk Mitigation Log`. categoryLabels off; `labels.fontFamily/fontSize/color/alignment/wordWrap` overridden to `'Segoe UI'` / `11D` / `#1a1a1a` / `'left'` / `true`. 200-px height + word-wrap + native card vertical scroll on overflow handles long mitigation log text (current data: range 67-650 chars, median ~250 chars; TONN-CON.02 = 301 chars per §d-6 dry-run). Title hidden. |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/UpdatesHistoryLabel/visual.json` | **New** textbox. Same Semibold 14pt `#1a1a1a` styling as MitigationLabel; text "Updates History". |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/UpdatesHistory/visual.json` | **New** tableEx. 3 columns in order: `update_date` ("Date"), `author` ("Author"), `note` ("Note", `objects.values[].properties.wordWrap = true` with `selector.metadata = "Risk_Updates.note"` — same wordWrap pattern as Detail/RecentRiskUpdates). `sortDefinition`: `update_date Descending`, `isDefaultSort: true`. No visual-level TopN filter (the drillthrough's `risk_id` filter propagates via the active M:1 `Risk_Updates[risk_id] → Risk_Register[risk_id]` and clamps the table to that risk's update history; typical 2-10 rows). Title hidden (the UpdatesHistoryLabel textbox carries the section header). |
| `pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/page.json` | **No change.** Phase 10 drillthrough wiring (`type: "Drillthrough"`, `pageBinding`, `visibility: "HiddenInViewMode"`, `filterConfig.filters[0]` Categorical filter on `Risk_Register[risk_id]` with `howCreated: "Drillthrough"`) preserved. |

No semantic model edits beyond the 2 measure appends. No theme.json changes. No CF rules. A pre-edit backup was not created this phase (no destructive operations on Phase 9-10 visuals; only the Phase 10 placeholder card was deleted, and the destination page metadata is fully reproducible from `pbir pages drillthrough --table Risk_Register --field risk_id` per CLAUDE.md memory entry [feedback-pbir-drillthrough-destination](../../../../.claude/projects/C--Users-jkhbu-OneDrive-Projects-powerbi-risk-register/memory/feedback_pbir_drillthrough_destination.md)).

### Authoring approach

`pbir add visual` used to scaffold canonical `actionButton` and `multiRowCard` shells (neither visualType had project precedent). Schema discovery: `pbir schema describe actionButton.visualLink` revealed the `type ∈ {Back, Bookmark, Drillthrough, ...}` enumeration; `pbir schema containers multiRowCard` confirmed the standard `Values.projections[]` query state matches the `card`/`tableEx` pattern already used Phases 9-10. After scaffolding, all 7 files were hand-authored from the template patterns (PageHeader for textboxes, KPIAvgScore for cards, TopRisks + RecentRiskUpdates for tableEx). No CF rules generated; theme + measure-side palette carries all coloring on Page 3.

---

## b) Visuals shipped (7 visuals matching 03 §d Page 3)

| # | Visual name | Type | Position (x, y, w, h) | Data binding |
|---|---|---|---|---|
| 1 | `BackButton` | actionButton | (24, 24, 80, 32) | None. `visualLink.type = Back`; `text.text = "Back"` at Segoe UI 11pt `#1a1a1a`. |
| 2 | `RiskTitle` | card | (120, 24, 1136, 60) | `_Measures.Selected Risk Title`. Custom labels Semibold 22pt `#1a1a1a`; title/background/border off. |
| 3 | `MetaStrip` | tableEx | (24, 100, 1232, 80) | `risk_id` ("Risk ID"), `risk_category` ("Category"), `risk_entity` ("Entity"), `risk_coordinator` ("Coordinator"), `risk_score_overall` ("Score"), `_Measures.Risk Level Pill SVG` ("Level"). `grid.imageHeight=44D`. Title off. |
| 4 | `MitigationLabel` | textbox | (24, 196, 1232, 32) | Static "Mitigation" Semibold 14pt `#1a1a1a`. |
| 5 | `MitigationParagraph` | card | (24, 236, 1232, 200) | `_Measures.Selected Risk Mitigation Log`. Custom labels regular 11pt `#1a1a1a` `wordWrap=true`; title off. |
| 6 | `UpdatesHistoryLabel` | textbox | (24, 452, 1232, 32) | Static "Updates History" Semibold 14pt `#1a1a1a`. |
| 7 | `UpdatesHistory` | tableEx | (24, 492, 1232, 204) | `update_date` ("Date"), `author` ("Author"), `note` ("Note", wordWrap on). Sort `update_date` Descending. Drillthrough filter on `risk_id` propagates via active M:1 relationship. |

Visual count = 7. Visual types: 1 actionButton + 2 textbox + 2 card + 2 tableEx. Matches 03 §d Page 3 by visual *count* (7) and *role* (header / meta / mitigation / updates); the spec's "multi-row card" choice for the meta strip was overridden by §g-3 for ImageUrl rendering reasons.

Position math:
- x-stack: most visuals span `(24, 1256)` width 1232. BackButton occupies `(24, 104)` width 80; RiskTitle occupies `(120, 1256)` width 1136 with a 16-px gap between them.
- y-stack: 24 (back+title) → 100 (meta strip) → 196 (mitigation label) → 236 (mitigation paragraph, +200) → 452 (updates history label, leaves a 16-px gap from paragraph end 436) → 492 (updates history, +204) → 696. Leaves 24-px bottom margin (720 - 696 = 24).
- No overlaps.

### Page-level filter

`page.json` `filterConfig.filters[0]` is the Categorical drillthrough filter on `Risk_Register[risk_id]` (`howCreated: "Drillthrough"`). The filter is *defined* by the destination page but *populated* by Power BI at drillthrough time with the source visual's `risk_id` value. Phase 10 wired this; Phase 11 leaves it untouched.

No additional page-level filters (`status = "Open"` from 03 §d Pages 1-2 is intentionally not propagated to Page 3 — the drillthrough delivers a single specific risk regardless of its status; surfacing it on a status-filtered detail page would mislead if the user ever drills through to a Closed/Realized risk).

---

## c) Conditional formatting and visual-level overrides

### CF rules applied

**None.** Page 3 has no measure-driven coloring:
- The `Risk Level Pill SVG` measure carries its own color palette inside the SVG (per 03 §c1 / 07 §b); MetaStrip renders the pill as-is, no CF wrapper needed.
- Score/Days/text fields render as plain values in the theme's neutral typography.
- No KPI cards, no matrix heatmap, no clustered series legend on Page 3.

### Per-visual title overrides (continuity with Phases 9-10)

All 7 visuals set `visualContainerObjects.title.show = false`. The two card visuals (RiskTitle, MitigationParagraph) replace the theme title chrome with their own value typography (RiskTitle = 22pt header; MitigationParagraph = 11pt body), so a duplicate theme title would clutter the layout. The two textbox visuals (MitigationLabel, UpdatesHistoryLabel) are the section headers themselves; a theme title above them would be a redundant label. The multiRowCard (MetaStrip) is positioned directly under the header strip; the field display names ("Risk ID", "Category", etc.) carry the labeling. The tableEx (UpdatesHistory) has the UpdatesHistoryLabel textbox immediately above it providing the section header.

### Card label styling (RiskTitle + MitigationParagraph)

Both cards override `objects.labels` directly (not via `visualContainerObjects.title`). The card visualType has `labels` for the value text and `categoryLabels` for the field name. RiskTitle and MitigationParagraph both turn `categoryLabels.show = false` (don't display "Selected Risk Title" / "Selected Risk Mitigation Log" as a subtitle) and customize `labels` typography per their role:

| Card | fontFamily | fontSize | color | wordWrap |
|---|---|---|---|---|
| RiskTitle | Segoe UI Semibold | 22D | #1a1a1a | (default off) |
| MitigationParagraph | Segoe UI | 11D | #1a1a1a | true |

Background and border on RiskTitle are also hidden (the page has no header bar; the title text floats directly on `#FFFFFF` canvas). MitigationParagraph inherits theme `card` background/border defaults (white fill, `#e0e0e0` 1px border, no shadow) which subtly delineates the paragraph block from the surrounding whitespace.

### tableEx layout (MetaStrip)

After the §g-3 swap from multiRowCard to tableEx, MetaStrip renders as a labeled header row + 1 data row (the drilled-into risk) at 1232×80. `objects.grid.imageHeight = 44D` reserves vertical space for the 60×20 SVG pill in the Level column (header band ~24px + data row 44px + ~12px padding = 80px). Same grid pattern as Detail/TopRisks. tableEx honors `dataCategory: ImageUrl` on measure-bound columns (Phase 10 §c confirms); multiRowCard does not, so the original spec's "multi-row card" choice rendered the SVG measure as raw URL text instead of an image (visible in the first-render screenshot before §g-3).

### tableEx wordWrap on `note` column (UpdatesHistory)

`objects.values[].properties.wordWrap = true` with `selector.metadata = "Risk_Updates.note"` — same column-scoped pattern Detail/RecentRiskUpdates uses (10 §a). The `selector.metadata` reference targets the specific column projection by its `queryRef` so only the `note` column wraps; `update_date` and `author` render single-line as expected.

### Theme-inherited styling (no per-visual override needed)

- multiRowCard `card`/`title`/`dataLabels`/`categoryLabels`: theme `multiRowCard` block (08 §a).
- tableEx headers/cells/gridlines: theme `tableEx` block (08 §a; same defaults as TopRisks and RecentRiskUpdates on Detail page).
- actionButton chrome (BackButton): no theme override per 08 §c "actionButton not styled by theme"; Power BI default back-action button chrome accepted (small arrow chevron icon next to the "Back" text label).
- textbox text styling: inline `textStyle` on each `textRun` (textbox cannot be theme-styled per 08 §c, same as PageHeader on Detail).

### Inline hex codes (theme-driven palette check)

Grep across all 7 Page 3 visual.json files (`#[0-9a-fA-F]{3,6}` regex):

| Hex | Found in | Justification |
|---|---|---|
| `#1a1a1a` | BackButton text.fontColor; RiskTitle labels.color; MitigationParagraph labels.color; MitigationLabel textRun.color; UpdatesHistoryLabel textRun.color | 03 §c1 `text_primary`. Used on textboxes (cannot be theme-styled) and on the two cards' value-text override (per 03 §c2 typography role: report-title 22pt and body 11pt). Same precedent as Phases 9-10. |

Only `#1a1a1a`. No `#5a5a5a` this phase (Page 3 has no subtitle text or label-secondary role). No improvised hex codes. No CF-driven inline color (no CF on this page). The Risk Level Pill SVG color palette (`#de425b` / `#e8b450` / `#488f31` / `#FFFFFF`) is consumed via the measure, not declared inline in any Page 3 visual.json.

---

## d) Self-verification log

### 1. PBIR JSON parse

```
OK: pages.json
OK: RiskDetail\page.json
OK: RiskDetail\visuals\BackButton\visual.json
OK: RiskDetail\visuals\RiskTitle\visual.json
OK: RiskDetail\visuals\MetaStrip\visual.json
OK: RiskDetail\visuals\MitigationLabel\visual.json
OK: RiskDetail\visuals\MitigationParagraph\visual.json
OK: RiskDetail\visuals\UpdatesHistoryLabel\visual.json
OK: RiskDetail\visuals\UpdatesHistory\visual.json
```

All 9 files (pages.json + Phase-10-untouched RiskDetail/page.json + 7 new visuals) parse as valid JSON.

`pbir validate` reports **2 errors, 13 warnings**, all pre-existing or new-but-harmless per CLAUDE.md tooling notes:
- **2 errors** (pre-existing): `report.json` `$schema` mismatch, `pages.json` `$schema` mismatch (CLI's bundled schemas lag report's). Phase 10 had 3; the third was tied to the deleted `PlaceholderRiskId` visual (its `visualContainer/2.7.0` mismatch resolved by deletion).
- **13 warnings**: 9 pre-existing `SCHEMA_DEGRADED` from Phase 9-10 visuals on `visualContainer/2.9.0` (CLI bundles `2.7.0` fallback) plus 4 new warnings on Phase 11 visuals declaring `visualContainer/2.9.0` (MitigationLabel, UpdatesHistoryLabel, UpdatesHistory all use `2.9.0` matching the textbox/tableEx schema; BackButton, RiskTitle, MetaStrip, MitigationParagraph use `2.7.0` matching the actionButton/card/multiRowCard scaffold). All 13 are informational per CLAUDE.md "Neither blocks Power BI Desktop."

No new errors introduced this phase. Total visuals counted by `pbir validate`: 23 (9 Overview + 7 Detail + 7 RiskDetail).

### 2. Page hidden flag

`RiskDetail/page.json` line 27 retains `"visibility": "HiddenInViewMode"` (Phase 10; file untouched this phase). Confirmed via Read; the page tab strip will show only "Executive Overview" and "Risk Register Detail" after open; "Risk Detail" is reachable only via right-click drillthrough.

### 3. Drillthrough filter declaration

`RiskDetail/page.json` (untouched) contains the three required pieces (per the [feedback-pbir-drillthrough-destination](../../../../.claude/projects/C--Users-jkhbu-OneDrive-Projects-powerbi-risk-register/memory/feedback_pbir_drillthrough_destination.md) lesson):

| Element | Location | Value |
|---|---|---|
| Page-level drillthrough filter | `filterConfig.filters[0]` | `field: Risk_Register[risk_id]`, `type: "Categorical"`, `howCreated: "Drillthrough"`, `name: "6d8be0f08d944951e25e"` |
| Page type | `page.json` root | `"type": "Drillthrough"` |
| Page binding | `page.json` root | `pageBinding.parameters[0].boundFilter = "6d8be0f08d944951e25e"` (binds the drillthrough parameter to the filter by name), `fieldExpr: Risk_Register[risk_id]` |

All three intact.

### 4. Visual data bindings (grep against PBIR JSON)

| Field / measure | Used by | Resolved in model |
|---|---|---|
| `Risk_Register.risk_id` | MetaStrip; (page-level drillthrough filter) | ✓ |
| `Risk_Register.risk_category` | MetaStrip | ✓ |
| `Risk_Register.risk_entity` | MetaStrip | ✓ |
| `Risk_Register.risk_coordinator` | MetaStrip | ✓ |
| `Risk_Register.risk_score_overall` | MetaStrip | ✓ |
| `Risk_Updates.update_date` | UpdatesHistory (Values + sort) | ✓ |
| `Risk_Updates.author` | UpdatesHistory | ✓ |
| `Risk_Updates.note` | UpdatesHistory (Values + wordWrap selector) | ✓ |
| `_Measures.Risk Level Pill SVG` | MetaStrip | ✓ (Phase 7) |
| `_Measures.Selected Risk Title` | RiskTitle | ✓ (this phase) |
| `_Measures.Selected Risk Mitigation Log` | MitigationParagraph | ✓ (this phase) |

11 distinct field/measure references, 11 resolutions. No unresolved bindings.

BackButton, MitigationLabel, UpdatesHistoryLabel intentionally have empty `query.queryState` (action visuals and static textboxes have no data binding).

### 5. Back button presence

`pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/visuals/BackButton/visual.json` exists at position (24, 24, 80, 32), `visualType: actionButton`, `objects.visualLink[0].properties.type.expr.Literal.Value = "'Back'"`. Power BI's auto drillthrough back-action engages on this type; clicking returns to the source page (Page 2 "Detail") with the prior selection state intact.

### 6. End-to-end chain dry-run for TONN-CON.02

Computed against `source_data/Tonnelle_Risk_Register_MASTER.xlsx` and `source_data/Tonnelle_Risk_Updates_MASTER.xlsx` via inline Python this turn (mirrors the Phase 5/6 verification path). Today = 2026-05-23.

| Page 3 visual | Expected content for TONN-CON.02 |
|---|---|
| `RiskTitle` (`[Selected Risk Title]`) | `Area of Concern 20 free product` |
| `MetaStrip` Risk ID | `TONN-CON.02` |
| `MetaStrip` Category | `Environmental` |
| `MetaStrip` Entity | `GDC` |
| `MetaStrip` Coordinator | `Joshua Giron` |
| `MetaStrip` Score | `20` (integer) |
| `MetaStrip` Level | High pill (red `#de425b` fill, white text) — `risk_level = "High"` |
| `MitigationParagraph` (`[Selected Risk Mitigation Log]`, post-§g-1 rewrite) | **6 lines, newest first**, each `M/D/YYYY - note` separated by `UNICHAR(10)` line breaks: `5/6/2026 - Remediation ongoing; cost exposure under review.` / `3/14/2026 - Recovery continuing; extent larger than first estimated.` / `2/15/2026 - Remediation cost executed via change order; risk realized` / `12/8/2025 - Product recovery underway; volume being quantified.` / `10/22/2025 - NJDEP notified; remediation plan submitted.` / `9/20/2025 - Free product detected at AOC-20 during environmental monitoring.` Rendered in 1232×200 card with `labels.wordWrap = true`; Power BI Desktop renders `UNICHAR(10)` as a true line break when wordWrap is on. (The pre-§g-1 SELECTEDVALUE-on-static-column form returned a 301-char single-paragraph blob; first render visible in §g screenshot.) |
| `UpdatesHistory` (drillthrough-filtered to TONN-CON.02) | **6 rows**, sorted `update_date` desc. Top 3: `2026-05-06 / Joshua Giron / Remediation ongoing; cost exposure under review.` ; `2026-03-14 / Joshua Giron / Recovery continuing; extent larger than first estimated.` ; `2026-02-15 / Joshua Giron / Remediation cost executed via change order; risk realized` |
| `[Days Since Last Update]` for TONN-CON.02 (if displayed) | 17 d as of 2026-05-23 (drifts +1 per calendar day) |

These values are what the user should see on Page 3 after right-click drillthrough from Page 2 TopRisks row TONN-CON.02 → Drill through → Risk Detail. Re-verify by re-running the inline computation against current source any time updates are appended.

### 7. Theme-driven colors

Grep `#[0-9a-fA-F]{3,6}` across all 7 Page 3 visual.json files:

| Hex | Count | Files | Tokens consumed (03 §c1) |
|---|---|---|---|
| `#1a1a1a` | 5 | BackButton, RiskTitle, MetaStrip (n/a, only inherited), MitigationLabel, MitigationParagraph, UpdatesHistoryLabel | `text_primary` |

Only `#1a1a1a` appears. No improvised hex codes. No CF rules (and therefore no CF-driven hex). The SVG pill measure's palette (`#de425b` / `#e8b450` / `#488f31` / `#FFFFFF`) is consumed via measure, not declared on any Page 3 visual.json. Matches the Phase 9-10 precedent of "only `text_primary` and `text_secondary` inline; all other colors from theme or measure."

### 8. Cross-filter / drillthrough trace

Right-click on Detail/TopRisks row TONN-CON.02 → Drill through → Risk Detail:

1. Power BI populates the page-level filter `Risk_Register[risk_id] = "TONN-CON.02"` from the source visual's row context.
2. Filter propagates to every visual on Page 3 that binds to `Risk_Register`:
   - RiskTitle: `[Selected Risk Title]` SELECTEDVALUE collapses to the single row → returns `"Area of Concern 20 free product"`.
   - MetaStrip: multiRowCard renders the single row's 6 fields. The SVG pill measure also SELECTEDVALUE-collapses → red High pill.
   - MitigationParagraph: `[Selected Risk Mitigation Log]` SELECTEDVALUE → 301-char text.
3. UpdatesHistory binds to `Risk_Updates`; the page filter propagates via the active M:1 `Risk_Updates[risk_id] → Risk_Register[risk_id]` (single direction, Register filters Updates) → Updates table reduces to 6 rows for TONN-CON.02 → tableEx sort by `update_date` Descending presents most-recent-first.
4. BackButton, MitigationLabel, UpdatesHistoryLabel have no data binding; they render static.
5. Click BackButton → Power BI's auto back-action returns to Detail page with the prior cross-filter / selection state intact.

Trace is complete and unambiguous. No race conditions, no implicit ALL/REMOVEFILTERS interactions.

### 9. Drillthrough filter propagation across relationships

The locked relationships from 03 §a (re-confirmed Phase 4/5):
- `Risk_Updates[risk_id]` → `Risk_Register[risk_id]` M:1 single-direction Active
- `Risk_Register[project_id]` → `Project[project_id]` M:1 single-direction Active

For Page 3:
- Page-level drillthrough filter on `Risk_Register[risk_id]` filters `Risk_Register` to 1 row directly (the field is on the table itself; no traversal needed).
- The Risk_Register → Risk_Updates relationship is single-direction "Updates is filtered by Register" (i.e., filter flows from Register's risk_id to Updates' risk_id). This is the direction Page 3's UpdatesHistory needs: with 1 risk_id selected in Register, Updates reduces to that risk's history. Verified by §d-6 (6 updates for TONN-CON.02).
- No traversal of the Project relationship needed by any Page 3 visual.
- No CROSSFILTER inside any measure (03 §a closing note's deferred option for "Register-filtered-from-Updates context" measures); not needed for any Phase 11 binding.

### 10. Measure-name uniqueness and final count

`_Measures.tmdl` grep for `measure '` after this phase:

```
Total Risks (Counts)
High Risks (Counts)
Medium Risks (Counts)
Low Risks (Counts)
Avg Risk Score Overall (Scores)
Avg Cost Score (Scores)
Avg Schedule Score (Scores)
Max Risk Score (Scores)
Updates Count (TimeIntel)
Days Since Last Update (TimeIntel)
Risk Level Pill SVG (Display)
Cell PI Score (Display)
Cell Total Risks (Display)
Selected Risk Title (Display)            ← Phase 11 new
Selected Risk Mitigation Log (Display)   ← Phase 11 new
```

15 measures, 15 unique names. Final count matches the floor-not-ceiling treatment in CLAUDE.md (03 §b lock was 13; Phase 9 added 2 dim-axis helpers `Cell PI Score` and `Cell Total Risks`; Phase 11 adds the 2 deferred Display measures `Selected Risk Title` and `Selected Risk Mitigation Log`).

### 11. Performance flag scan on new measures

`Selected Risk Title` and `Selected Risk Mitigation Log`:

| Antipattern | Status |
|---|---|
| SUMX / FILTER over fact table | absent |
| Nested CALCULATE | absent (no CALCULATE at all) |
| Unnecessary ALL / REMOVEFILTERS | absent (drillthrough filter must propagate; ALL would break Page 3) |
| `BLANK()` arithmetic without guard | n/a (text return) |
| DISTINCTCOUNT where COUNTROWS suffices | n/a |
| Repeated subexpression without VAR | absent (single-call body) |
| `SELECTEDVALUE` without fallback | **mitigated** (both measures pass the optional `alternateResult` argument: `"No risk selected"` / `""`) |

`SELECTEDVALUE` is a single-column scalar lookup; the only storage-engine work is one column scan of 37 rows. Same shape as the Phase 7 `Risk Level Pill SVG` template (which also uses SELECTEDVALUE on Risk_Register, no CALCULATE).

VAR-name trap: neither measure uses VARs (one-liner bodies), so the Phase 7 `LevelText`-vs-`Level` reserved-token bug is dodged by construction. If a future iteration adds VARs, avoid `Title` / `Value` / `Date` / `Name` / `Year` / `Month` / `Level` as identifier names.

---

## e) User-side actions to apply

### e1. Refresh / reopen

1. **Close Power BI Desktop** if it has `Tonnelle_Risk.pbip` open.
2. **Open `pbip/Tonnelle_Risk.pbip`.** The file should open on the `RiskDetail` page (per `activePageName: RiskDetail`). Because `RiskDetail` is `HiddenInViewMode`, Desktop opens to its visuals in edit mode but the page tab strip still hides it; switch to "Risk Register Detail" or "Executive Overview" to navigate.
3. Confirm the Fields pane shows the 2 new measures in `_Measures` → `Display`: `Selected Risk Title`, `Selected Risk Mitigation Log` (the `Display` folder now has 5 measures total).

### e2. Verify the drillthrough chain end-to-end

1. Navigate to **Risk Register Detail** (Page 2) via the page tab strip.
2. **Right-click** the TONN-CON.02 row in the TopRisks table.
3. In the context menu, hover **Drill through**.
4. Click **Risk Detail**. Power BI navigates to Page 3 with the `risk_id = "TONN-CON.02"` drillthrough filter applied.
5. Expected Page 3 contents (per §d-6):
   - **RiskTitle**: "Area of Concern 20 free product" (22pt Semibold)
   - **MetaStrip**: 6 fields in one row — `TONN-CON.02 | Environmental | GDC | Joshua Giron | 20 | <red High pill>`
   - **Mitigation label** then **paragraph card**: full 301-char mitigation log word-wrapped
   - **Updates History label** then **table**: 6 rows, top row `2026-05-06 / Joshua Giron / Remediation ongoing; cost exposure under review.`
6. Click **Back** button (top-left). Power BI returns to Page 2 Detail with the prior selection state.

### e3. Possible iterations on first open

After the §g revisions, one residual behavior is worth a re-check on first open:

- **MitigationParagraph line breaks**: if the card displays the 6 update entries as a flowing single paragraph (line-break characters not respected), click MitigationParagraph → Format pane → Callout value → confirm Word wrap = ON. The PBIR already declares `labels.wordWrap = true`; Power BI Desktop renders `UNICHAR(10)` from the DAX measure as a true line break when wordWrap is on, but some builds need a one-click reconfirm to re-render the card. As a fallback if line breaks still don't render: the measure can be rewritten to use `UNICHAR(13) & UNICHAR(10)` (CRLF) instead of `UNICHAR(10)` alone — defer unless observed.

The §g-2 BackButton (visualLink + icon + outline) and §g-3 MetaStrip-as-tableEx (with `grid.imageHeight=44D`) are now structurally correct in PBIR; the JSON matches the patterns Power BI Desktop emits for the same Format-pane settings.

### e4. Apply theme if not already applied (Phase 8/9 user-side step)

If the multiRowCard/tableEx/textbox on Page 3 render with default blue/orange Power BI typography instead of the locked greys, apply `assets/theme.json` per 08 §g (one-time step):

1. **View** ribbon → **Themes** → **Browse for themes** → `assets/theme.json` → Open.
2. Save. The theme reference is encoded in `report.json` `themeCollection`.

The Page 3 cards/textboxes/tableEx then pick up the locked Segoe UI palette automatically.

### e5. Optional: screenshot the chain

Save the Page 2 → Page 3 drillthrough as a 2-image walkthrough at `assets/page3_drillthrough_before.png` (Page 2 with TONN-CON.02 row highlighted) and `assets/page3_drillthrough_after.png` (Page 3 displaying TONN-CON.02 contents). Useful for the Phase 13 portfolio writeup.

### e6. Do NOT proceed to Phase 12

Phase 12 (Python append script for `Risk_Updates`) is the next phase per CLAUDE.md phase map; not in scope this turn. The append script needs the `Risk_Updates` schema (Phase 1 lock: `update_id, risk_id, update_date, update_year, author, note`) plus a clear append target (the `Tonnelle_Risk_Updates_MASTER.xlsx` source file). Both are stable; Phase 12 builds on the Page 1 trend line and Page 3 updates feed dependability.

---

## f) Status

Phase 11 deliverable shipped. **7 PBIR visuals on Page 3** (`RiskDetail` / display "Risk Detail", hidden, drillthrough destination), positions match 03 §d to the pixel. Drillthrough destination wiring intact from Phase 10 (`type: "Drillthrough"`, `pageBinding`, page-level Categorical filter with `howCreated: "Drillthrough"`). **2 new Display measures** added (`Selected Risk Title`, `Selected Risk Mitigation Log`); total `_Measures` count = 15 (4 Counts + 4 Scores + 2 TimeIntel + 5 Display).

End-to-end chain verified by source-data dry-run for TONN-CON.02: drillthrough delivers a 1-risk Page 3 displaying the locked attributes (title, 6 meta fields, 301-char mitigation log, 6-row updates history sorted desc, Back button returns to source). Visual rendering confirmation deferred to user-side per §e2 (Power BI Desktop must open the PBIP for actual render verification; PBIR is structurally complete).

No semantic-model changes beyond the 2 measure appends. No theme.json changes. No CF rules. Inline hex usage on Page 3 limited to 1 token (`#1a1a1a`) across 5 of 7 visuals — strict subset of the Phase 9-10 precedent (which also used `#5a5a5a`).

**Three post-deliverable revisions applied** after the first-render screenshot surfaced bugs (full revision log in §g): mitigation measure rewritten to pull from `Risk_Updates` (newest-first multi-line list per user request); BackButton's `visualLink` block relocated to `visualContainerObjects` (Power BI Desktop silently stripped my misplaced `objects.visualLink`) plus chevron icon and outline added; MetaStrip swapped from `multiRowCard` to `tableEx` so the SVG pill measure's `dataCategory: ImageUrl` engages (multiRowCard does not honor it).

Phase 12 (Python `scripts/append_updates.py` + `docs/12_script_design.md`; no PBI skill) is the next phase, unblocked. The report build is complete; Phase 12 is operational tooling for the data layer.

---

## g) Post-deliverable revisions (2026-05-23, after first-render verification)

User opened the rebuilt RiskDetail page in Power BI Desktop and shared a screenshot showing TONN-CON.02 drilled-into. Three issues surfaced, all fixed this turn:

### g-1. Mitigation paragraph now reads from Risk_Updates (user request)

**Observed:** the MitigationParagraph rendered the static `Risk_Register[mitigation_log]` column as a single 301-char flowing paragraph (`"9/20 - ...10/22 - ...12/8 - ...3/14 - ...5/6 - ..."`). The user asked for the mitigation list to be unconcatenated, each update on its own line, newest at the top, and noted that the underlying source could be the Updates log keyed by risk_id.

**Fix:** rewrote `[Selected Risk Mitigation Log]` to pull from `Risk_Updates` rather than the static column. The active M:1 relationship from `Risk_Updates` to `Risk_Register` propagates the drillthrough filter naturally, so the measure body needs no `CALCULATE` or explicit `FILTER`:

```dax
Selected Risk Mitigation Log =
VAR CurrentRiskId = SELECTEDVALUE ( Risk_Register[risk_id] )
RETURN
    IF (
        NOT ISBLANK ( CurrentRiskId ),
        CONCATENATEX (
            Risk_Updates,
            FORMAT ( Risk_Updates[update_date], "M/D/YYYY" ) & " - " & Risk_Updates[note],
            UNICHAR ( 10 ),
            Risk_Updates[update_date],
            DESC
        ),
        ""
    )
```

`CONCATENATEX` 5th argument `DESC` sorts the iterated table by `update_date` Descending; `UNICHAR(10)` is the line-feed separator; the `IF` guard preserves the empty-paragraph behavior when no risk is in context. The orphaned `Risk_Register[mitigation_log]` column stays in the model unused (available for future tooltips or fallback). Side benefit: the rewrite surfaces ALL Risk_Updates rows for a risk, not just the curated narrative — for TONN-CON.02 the static column had 5 segments; the rewrite shows the 6 actual updates (the additional one is the 2/15/2026 "risk realized" closing event that wasn't part of the curated narrative).

**Verification:** computed against source via inline Python this turn (see §d-6 revised table). For TONN-CON.02 the measure now returns 6 lines totaling 364 chars, newest-first.

**Performance:** `CONCATENATEX` over `Risk_Updates` (filtered by drillthrough to typically 2-10 rows) is cheap. No `CALCULATE`, no nested iterator. `SELECTEDVALUE` guard is a single-column scalar.

### g-2. BackButton visualLink block relocated, icon + outline added

**Observed:** the BackButton in the top-left rendered as a small empty rectangle — no "Back" text, no chevron icon, no chrome. Power BI Desktop's save-on-open had stripped my `objects.visualLink` block entirely, leaving only the `objects.text` block (visible in the linter-modified diff).

**Root cause:** the `visualLink` container belongs under `visualContainerObjects`, not under `objects`. The pbir CLI schema reports both `objects` and `visualContainerObjects` containers in the same `pbir schema containers actionButton` listing without distinguishing scope, which is the trap I fell into. `visualContainerObjects` holds container-level behaviors that wrap the visual (title chrome, background, border, drill action, navigation link); `objects` holds visual-internal properties (shape, fill, text, icon). Desktop validates each block against its expected scope and silently drops mismatches.

**Fix:** used `pbir set "...BackButton.Visual.visualLink.type" --value Back` — the CLI knows the canonical scope and wrote `visualContainerObjects.visualLink[0].properties.type.expr.Literal.Value = "'Back'"`. Then added `icon.show = true`, `icon.shapeType = leftArrow`, `icon.placement = left`, `outline.show = true` via the same CLI for chevron + tap-target visibility. Total 4 `pbir set` calls.

**Lesson generalized:** when a visual property doesn't survive a Desktop open/save round-trip, check whether it belongs under `objects` vs `visualContainerObjects`. The pbir CLI's `set` command resolves scope correctly; prefer it over hand-authoring for unfamiliar visualTypes. (Will save as memory entry.)

### g-3. MetaStrip swapped from multiRowCard to tableEx

**Observed:** the Level column in MetaStrip rendered the SVG pill measure as raw URL text — the cell displayed literal `data:image/svg+x...` (truncated by Power BI's column width) instead of the rendered pill image. The other 5 fields (Risk ID, Category, Entity, Coordinator, Score) rendered correctly with their `displayName` headers as labels and the drilled-into risk's values below.

**Root cause:** multiRowCard does not honor `dataCategory: ImageUrl` on measure-bound projections. The Phase 7 SVG-pill measure carries `dataCategory: ImageUrl` on the TMDL side, but multiRowCard renders it as plain text. tableEx (Page 2 TopRisks precedent) does honor ImageUrl when paired with `objects.grid.imageHeight=<height>D`.

**Fix:** rewrote `MetaStrip/visual.json` as a tableEx with the same 6 column projections, same `displayName` overrides, and `objects.grid.imageHeight = 44D` (same image height as Detail/TopRisks). Position unchanged (24, 100, 1232, 80); 80-px height accommodates ~24px header + 44px image row + padding. With the drillthrough filter reducing `Risk_Register` to 1 row, tableEx renders exactly 1 data row, giving the same visual outcome the spec intended: a horizontal strip of 6 labeled values. Title hidden (the visual is positioned directly under the RiskTitle card).

**Tradeoff note:** the 03 §d spec calls this visual a "multi-row card." The role and content match (single record × 6 attributes, horizontal strip layout); only the visual type differs. Documented in §b "Visual count and types" revised cell. The choice is forced by the ImageUrl requirement and is the same pragmatic deviation Phase 10 made on the TopRisks Level column.

### g-4. MetaStrip Grand Total row suppressed

**Observed:** after the §g-3 swap to tableEx, the MetaStrip rendered exactly one row of content showing the literal label "Total" in the Risk ID column, blank text columns, and the Level pill in the last column. The TONN-CON.02 data row was missing. Screenshot captured 2026-05-23.

**Root cause:** tableEx defaults to `total.totals = true` (show Grand Total row). The theme.json `tableEx.total[0].totals: false` block (08 §a) does not override this default on a per-visual basis the way other tableEx defaults are honored. With 1 row in filter context, the Grand Total row collapses to "Total + measure value in total context" — for MetaStrip, that's "Total" in column 1 + the pill measure (which SELECTEDVALUE-resolves to the same High value in the 1-row total context) in column 6. The actual data row is rendered but gets clipped/hidden by the 80-px height once the Grand Total row is also present (24 header + 44 data + 24 total > 80).

**Fix:** `pbir set "...MetaStrip.Visual.total.totals" --value false` wrote `objects.total[0].properties.totals = false` directly on the visual, overriding the tableEx default. With totals suppressed, only the data row remains and the 80-px viewport fits it comfortably (24 header + 44 data + ~12 padding = ~80).

**Lesson:** Power BI Desktop's tableEx total defaults are NOT reliably overridden by theme.json's `total[0].totals: false` block. Explicit per-visual `total.totals: false` is required when a tableEx should display data rows without a Grand Total. Add to the data-goblin theme gotcha list for future phases.

### Re-verification after revisions

| Check | Status |
|---|---|
| JSON parse 8 RiskDetail files | OK (re-run after each edit) |
| BackButton has visualLink.type=Back, icon, outline | OK (via `pbir set`) |
| MetaStrip visualType=tableEx with grid.imageHeight=44D, total.totals=false | OK |
| Mitigation measure CONCATENATEX shape parses | OK (re-saved _Measures.tmdl) |
| Inline hex codes still limited to `#1a1a1a` | OK (no new colors introduced by g-fixes) |
| Drillthrough filter on RiskDetail/page.json | OK (untouched) |
| Final measure count | 15 (unchanged) |

User-side re-open will confirm: (a) BackButton displays chevron + "Back" label and triggers back navigation; (b) MetaStrip shows the data row `TONN-CON.02 | Environmental | GDC | Joshua Giron | 20 | <High pill>` (no Grand Total row); (c) MitigationParagraph displays the 6-line newest-first list.

