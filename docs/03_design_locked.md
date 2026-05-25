# 03. Design lock (binding spec)

Phase 3 stringent lock, prepared 2026-05-22. Skill active: `pbi-report-design` (data-goblin). After this point, downstream phases reference this file and do not revisit decisions. Any future deviation requires user-confirmed amendment to this doc.

**Inputs:**
- Turnover spec (`assets/RISK_DASHBOARD_turnover.md`).
- Phase 1 audit (`docs/01_audit.md`).
- Phase 2 exploration and four user answers (`docs/02_schema_challenge.md`).
- Six user answers captured this turn: visual identity (custom 5-color divergent palette plus a proposed yellow), density (dense informational), Page 3 drillthrough (single-column narrative), `next_review_date` treatment (replace with "Days Since Last Update"), KPI target approach (bare cards with documented deviation), background mode (light).

Citations of data-goblin rules use shorthand (e.g., "DG: 3-30-300", "DG: hidden keys", "DG: marked date table"). Section §f enumerates deliberately accepted rule violations.

---

## a) Locked schema

### Tables

| Name | Role | Source | Grain | Approx rows |
|---|---|---|---|---|
| `Risk_Register` | Fact-like | Excel `Tonnelle_Risk_Register_260519.xlsx` sheet `Risk_Register` | One row per risk | ~30-40 (37 today) |
| `Risk_Updates` | Fact (event log) | Excel `Tonnelle_Risk_Updates_MASTER.xlsx` sheet `Risk_Updates` (regenerated per Phase 2 §c-Q3; 2026-05-22) | One row per dated update | 127 post-regenerate |
| `Project` | Dim | Excel `Tonnelle_Risk_Register_260519.xlsx` sheet `Project` | One row per project | 1 |
| `dim_Date` | Dim | DAX calculated table | One row per day | ~365 x 2 years |
| `Lookups` | Reference | Enter data, mirrors Excel `Lookups` tab list values | Long format: list_type + value | 16 (7 categories + 5 entities + 4 statuses) |
| `_Measures` | Helper | Enter data, hidden dummy column | n/a | 0 user-facing |

Citations:
- Star-schema role classification per DG: "clear dimension vs fact classification."
- `_Measures` as dedicated measure-only table per DG: "Hide technical keys, IDs from report view" combined with CLAUDE.md gotcha "all measures live in a dedicated `_Measures` table."
- `dim_Date` as a marked date table per DG: "Dedicated marked date table."
- `Lookups` retained per turnover §"Platform decision" (intentional dual-duty with Excel). Hidden by default in PBI; unhide if a Phase 5+ visual requires it.

### Columns

#### `Risk_Register`

| Column | Type | Format | Default summarization | Hidden | Notes |
|---|---|---|---|---|---|
| `risk_id` | Text | none | Don't summarize | No | Primary key. Used as drillthrough filter on Page 3. |
| `project_id` | Text | none | Don't summarize | Yes | FK to `Project`. DG: hide technical keys. |
| `source_ref` | Text | none | Don't summarize | No | Shown on Page 3 meta strip. |
| `status` | Text | none | Don't summarize | **Yes** | Hidden per Phase 2 §c-Q2 lock; unhide when user backfills. Documented in §f. |
| `risk_category` | Text | none | Don't summarize | No | Sort by `risk_category` (alphabetical default; see §c5 below for sort rule). |
| `risk_title` | Text | none | Don't summarize | No | |
| `risk_type` | Text | none | Don't summarize | No | |
| `probability_score` | Whole number | `0` | Don't summarize | No | DG: integer scores, no aggregation default. |
| `cost_impact_score` | Whole number | `0` | Don't summarize | No | |
| `schedule_impact_score` | Whole number | `0` | Don't summarize | No | |
| `risk_score_cost` | Whole number | `0` | Don't summarize | No | Excel formula, stored. Locked per CLAUDE.md. |
| `risk_score_schedule` | Whole number | `0` | Don't summarize | No | Excel formula, stored. |
| `risk_score_overall` | Whole number | `0` | Don't summarize | No | Excel formula, stored. Top Risks table sorts on this. |
| `risk_level` | Text | none | Don't summarize | No | Sort by `risk_level_sort`. Display column on Page 2 swapped for `[Risk Level Pill SVG]`. |
| `risk_level_sort` | Whole number | none | Don't summarize | Yes | Power Query conditional column: Low=1, Medium=2, High=3. Per CLAUDE.md gotcha "Sort-order columns: Power Query conditional columns, never DAX." |
| `risk_entity` | Text | none | Don't summarize | No | |
| `risk_coordinator` | Text | none | Don't summarize | No | Drives Page 2 coordinator workload bar. |
| `mitigation_status` | Text | none | Don't summarize | No | |
| `mitigation_log` | Text | none | Don't summarize | No | Long text. Surfaced via `[Selected Risk Mitigation Log]` on Page 3 only; tooltip on Page 2. |

**Dropped from schema:** `next_review_date` (Phase 1 audit found uniformly today; Phase 2 §d-Q8 lock replaces it with measure `[Days Since Last Update]` derived from `Risk_Updates`).

#### `Risk_Updates`

| Column | Type | Format | Default summarization | Hidden | Notes |
|---|---|---|---|---|---|
| `update_id` | Text | none | Don't summarize | Yes | PK, no UI value. DG: hide technical keys. |
| `risk_id` | Text | none | Don't summarize | Yes | FK to `Risk_Register`. |
| `update_date` | Date | `yyyy-mm-dd` | Don't summarize | No | Active relationship to `dim_Date`. |
| `update_year` | Whole number | `0` | Don't summarize | Yes | Redundant with `dim_Date[Year]` (Phase 1 audit: matches on all 92 rows). Kept for source-faithfulness, hidden in PBI. |
| `author` | Text | none | Don't summarize | No | |
| `note` | Text | none | Don't summarize | No | |

#### `Project`

Columns mirror the Excel `Project` sheet headers verbatim. Exact names verified in Phase 4 M code. Expected fields (per turnover): `project_id` (Text, hidden, FK), `project_name` (Text), `contract_value` (Decimal, `$#,##0`), `ntp_date` (Date), `duration_days` (Whole number), `pct_complete` (Decimal, `0.0%`). Used for header-bar callouts only; not joined to anything Page 1-2 visual depends on at row grain.

#### `dim_Date`

| Column | Type | Format | Default summarization | Hidden | Notes |
|---|---|---|---|---|---|
| `Date` | Date | `yyyy-mm-dd` | Don't summarize | No | Key. Mark as date column. |
| `Year` | Whole number | `0` | Don't summarize | No | |
| `MonthNumber` | Whole number | `0` | Don't summarize | Yes | Sort helper. |
| `MonthName` | Text | none | Don't summarize | No | Sort by `MonthNumber`. |
| `YearMonth` | Text | none | Don't summarize | No | Display `yyyy-mm`. Sort by `YearMonthSort`. |
| `YearMonthSort` | Whole number | none | Don't summarize | Yes | `Year*100 + MonthNumber`. |

#### `Lookups`

| Column | Type | Format | Default summarization | Hidden | Notes |
|---|---|---|---|---|---|
| `list_type` | Text | none | Don't summarize | No | `category`, `entity`, or `status`. |
| `value` | Text | none | Don't summarize | No | One row per enumeration value. |

16 rows total: 7 categories (Construction, Field Condition, Design Change, Safety, Environmental, Political, Financial), 5 entities (GDC, CM, Contractor, Shared, Designer), 4 statuses (Open, Closed, Monitoring, Realized). Financial and Designer per Phase 2 §c-Q1 lock.

#### `_Measures`

One placeholder column `_dummy`, hidden. Table is the home for all measures organized by display folder.

### Relationships

| From | To | Cardinality | Cross-filter | Active |
|---|---|---|---|---|
| `Risk_Updates[risk_id]` | `Risk_Register[risk_id]` | M:1 | Single (Register filters Updates) | Yes |
| `Risk_Register[project_id]` | `Project[project_id]` | M:1 | Single (Project filters Register) | Yes |
| `Risk_Updates[update_date]` | `dim_Date[Date]` | M:1 | Single (dim_Date filters Updates) | Yes |

No bidirectional relationships. Per DG: "Single direction unless specifically needed." If Phase 5-7 finds a measure that requires Register-filtered-from-Updates context (e.g., "show only High-risk update counts on the trend line"), use CROSSFILTER inside the measure rather than enabling bidirectional at the relationship level.

`Lookups` is not joined to anything. It is a reference table only.

### Date table strategy

DAX calculated table:
```
dim_Date =
CALENDAR (
    DATE ( YEAR ( MIN ( Risk_Updates[update_date] ) ), 1, 1 ),
    DATE ( YEAR ( MAX ( Risk_Updates[update_date] ) ), 12, 31 )
)
```
Add calculated columns for `Year`, `MonthNumber`, `MonthName`, `YearMonth`, `YearMonthSort` per the table above. Mark `dim_Date[Date]` as the date column (Modeling > Mark as date table). Phase 4 deliverable includes the full DAX, not just the seed.

Citations: Phase 2 §b5 recommendation; DG: "Dedicated marked date table." Continuous-axis benefit for the Page 1 monthly trend.

---

## b) Locked measure architecture

13 measures total, organized into four TMDL display folders inside `_Measures`. No DAX in this section, only signatures and intent. DAX implementation is Phase 5.

### `Counts`

| Measure | Intent | Used on |
|---|---|---|
| `Total Risks` | Count of distinct `risk_id` in current filter context. | Page 1 KPI card; Page 2 implicit. |
| `High Risks` | Count of risks where `risk_level = "High"`. | Page 1 KPI card. |
| `Medium Risks` | Count of risks where `risk_level = "Medium"`. | Page 1 KPI card. |
| `Low Risks` | Count of risks where `risk_level = "Low"`. | Page 1 KPI card. |

### `Scores`

| Measure | Intent | Used on |
|---|---|---|
| `Avg Risk Score Overall` | Average `risk_score_overall` across filtered risks. | Page 1 KPI card. |
| `Avg Cost Score` | Average `risk_score_cost`. | Reserved for Phase 5+ analysis; not on locked pages. |
| `Avg Schedule Score` | Average `risk_score_schedule`. | Reserved for Phase 5+. |
| `Max Risk Score` | Max `risk_score_overall` in current context. | Reserved for Phase 5+. |

### `TimeIntel`

| Measure | Intent | Used on |
|---|---|---|
| `Updates Count` | Count of `Risk_Updates` rows in current filter (date and otherwise). | Page 1 trend line. |
| `Days Since Last Update` | Days between today (`TODAY()`) and the most-recent `update_date` for the current risk-row context. Returns blank if no updates exist for the risk. | Page 2 Top Risks table; Page 3. |

### `Display`

| Measure | Intent | Used on |
|---|---|---|
| `Risk Level Pill SVG` | Returns a `data:image/svg+xml;utf8,<svg>...</svg>` string rendering a rounded pill labeled with the current row's `risk_level`, colored from the §c palette (Low #488f31, Medium #e8b450, High #de425b). Column carrying this measure has Data Category = Image URL. | Page 2 Top Risks table; Page 3 meta strip. |
| `Selected Risk Title` | Single-value text of the drilled-into risk's `risk_title`. SELECTEDVALUE pattern with a "No risk selected" fallback. | Page 3 header text box. |
| `Selected Risk Mitigation Log` | Single-value text of the drilled-into risk's `mitigation_log`. SELECTEDVALUE with fallback. | Page 3 narrative paragraph. |

Citations: DG: "Explicit measures for business metrics." All 13 are explicit. Display measures are flagged in §f as a deliberate violation of DG: "thin report measures sparingly" / "measures should compute values, not markup."

---

## c) Locked theme

### c1. Color palette

Source: user-provided 5-color divergent scale plus a proposed yellow midpoint (`#e8b450`, warm muted amber chosen to match the saturation tone of `#488f31` and `#de425b`). Background mode: light.

| Token | Hex | Use |
|---|---|---|
| `risk_high` | `#de425b` | High risk pill, High heatmap cells, semantic-bad in any KPI conditional formatting. |
| `risk_medium` | `#e8b450` | Medium risk pill, Medium heatmap cells, semantic-warning. **Confirm hex during user review; easy to adjust before Phase 8 theme.json.** |
| `risk_low` | `#488f31` | Low risk pill, Low heatmap cells, semantic-good, brand accent for KPI value text. |
| `palette_tint_low` | `#8cbcac` | Sage tint. Stacked-bar Low segment, secondary fills. |
| `palette_tint_high` | `#ec9c9d` | Pink tint. Stacked-bar High secondary fills, alternate row banding accent. |
| `palette_neutral` | `#f1f1f1` | Alternate row banding on Page 2 tables; subtle hover fills. Avoid as foreground on the white canvas (insufficient contrast). |
| `text_primary` | `#1a1a1a` | Primary text, KPI value, table cells. |
| `text_secondary` | `#5a5a5a` | Axis labels, secondary metadata, footnote-style text. |
| `canvas` | `#FFFFFF` | Page background. |
| `border` | `#e0e0e0` | Card borders, table gridlines, axis lines. |

Citations: DG: "muted and soft" (palette is desaturated by construction); DG: "colors that implicitly encode meaning (red=bad, green=good) should be avoided unless using them for that encoding" (we use them precisely for risk encoding, which is the sanctioned case); DG: "Don't rely solely on color to convey meaning" (mitigated: SVG pills carry text labels; heatmap cells carry the count number; band labels appear in slicer and legend).

**Heatmap cell colors (Page 1 P-I matrix):** 3-band fill keyed to risk_level of the cell's score (P*MAX(C,S)). Cell text always overlaid in white (for High, Low) or `#1a1a1a` (for Medium).

| Score | Risk level | Cell fill | Cell text |
|---|---|---|---|
| 1-7 | Low | `#488f31` | `#FFFFFF` |
| 8-14 | Medium | `#e8b450` | `#1a1a1a` |
| 15-25 | High | `#de425b` | `#FFFFFF` |

Sequential 5-step gradient (`#488f31` → `#8cbcac` → `#e8b450` → `#ec9c9d` → `#de425b`) is reserved for any future continuous heat encoding (not used on locked pages).

### c2. Typography

Per DG: Segoe UI and Segoe UI Semibold only. No custom fonts.

| Role | Family | Size | Weight |
|---|---|---|---|
| Report title (header text box) | Segoe UI Semibold | 22pt | Semibold |
| Page subtitle | Segoe UI | 11pt | Regular |
| Visual title | Segoe UI Semibold | 14pt | Semibold |
| KPI value | Segoe UI Semibold | 32pt | Semibold |
| KPI label | Segoe UI | 11pt | Regular |
| Body text (cells, lists) | Segoe UI | 11pt | Regular |
| Data labels | Segoe UI | 10pt | Regular |
| Axis labels | Segoe UI | 10pt | Regular |
| Footnote / secondary | Segoe UI | 9pt | Regular |

Minimum body 11pt rather than DG's 12pt floor. Justified by Phase 2 §c2 lock to "dense informational." 11pt remains within readable range on a 1280-wide canvas; flagged in §f.

### c3. Visual default formatting

Per DG: drop shadows off, transparent visual backgrounds, minimal axis ornamentation.

- Drop shadow: off everywhere. DG: "minimize drop shadows (vestibular issues)."
- Visual background: transparent (canvas color shows through). 1px border `#e0e0e0` on cards and tables only; no border on charts.
- Visual title: left-aligned, `text_primary`, Segoe UI Semibold 14pt.
- Padding: 8px inner padding on cards, 4px on chart visuals.
- Axis: gridlines off; axis line `#e0e0e0`, 1px; tick marks off; axis labels `text_secondary` 10pt.
- Data labels: off by default; enable per visual where the value cannot be read from position alone.
- Conditional formatting: applied only where the rule says "encode by value" (heatmap cells, KPI value tint for High Risks card, sparingly elsewhere).

---

## d) Locked page-by-page layout

Page size: 1280 x 720 (DG standard). Page margin: 24px each side. Inter-visual gap: 16px. Visual positions in `(x, y, width, height)` pixels.

Visual count per page: Page 1 = 9, Page 2 = 7, Page 3 = 7. All under DG's 12-15 cap.

### Page 1 — Executive Overview

Reading order top-to-bottom, left-to-right per DG 3-30-300 detail gradient (KPIs top, charts middle, trend bottom).

| # | Visual | Type | Position (x, y, w, h) | Data binding |
|---|---|---|---|---|
| 1 | Page header | textbox | (24, 24, 1232, 60) | Static line 1: "Tonnelle Avenue Bridge Relocation — Risk Register" (Semibold 22pt). Static line 2 (subtitle, 11pt regular): "Project TONN-01  •  Data refreshed [refresh-date measure]". |
| 2 | Total Risks | card | (24, 100, 233, 100) | `[Total Risks]`. Label "Total Risks". |
| 3 | High Risks | card | (273, 100, 233, 100) | `[High Risks]`. Conditional value-color: if > 10, `risk_high`; else `text_primary`. Label "High". |
| 4 | Medium Risks | card | (522, 100, 233, 100) | `[Medium Risks]`. Label "Medium". |
| 5 | Low Risks | card | (771, 100, 233, 100) | `[Low Risks]`. Label "Low". |
| 6 | Avg Risk Score | card | (1020, 100, 236, 100) | `[Avg Risk Score Overall]`. Format `0.0`. Label "Avg Score". |
| 7 | Probability x Impact matrix | matrix visual (5x5 heatmap) | (24, 216, 480, 290) | Rows: `probability_score` (5..1 desc). Columns: `MAX(cost_impact_score, schedule_impact_score)` (1..5 asc). Values: COUNTROWS of `Risk_Register` per cell. Conditional fill by score band per §c1 heatmap table. Cell text: cell count, white or dark per band. Empty cells: `canvas` fill, no count. |
| 8 | Risks by Category | clustered horizontal bar | (520, 216, 736, 290) | Y-axis: `risk_category` sorted by COUNTROWS desc. X-axis: COUNTROWS of `Risk_Register`. Legend: `risk_level` (sort by `risk_level_sort`). Colors: `risk_low`/`risk_medium`/`risk_high` per `risk_level`. Data labels: on, value only. |
| 9 | Risk Activity Over Time | line | (24, 522, 1232, 174) | X-axis: `dim_Date[YearMonth]` (sorted by `YearMonthSort`), continuous (months with zero updates shown). Y-axis: `[Updates Count]`, integer format. Line color: `risk_low`. Markers: on, small. Title: "Risk Activity Over Time (updates per month)" — clarifies it is not a score trend, per Phase 2 §c-Q4 lock. |

Slicers on Page 1: **none**. Filter pane available for category, coordinator, date range. DG: "Maximum 3 slicers per page — use filter pane instead" for cleaner exec view.

Report-level filter: `status = "Open"` while status is hidden and unmaintained (currently a no-op; locks the dashboard semantics as "currently active risks" once status is backfilled).

### Page 2 — Risk Register Detail

| # | Visual | Type | Position (x, y, w, h) | Data binding |
|---|---|---|---|---|
| 1 | Page header | textbox | (24, 24, 1232, 60) | "Risk Register Detail" (Semibold 22pt). Subtitle: "Project TONN-01  •  Data refreshed [refresh-date]". |
| 2 | Slicer: Category | slicer (vertical list) | (24, 100, 280, 80) | `risk_category`. Single-select off. Sort: alphabetical. |
| 3 | Slicer: Coordinator | slicer (vertical list) | (320, 100, 280, 80) | `risk_coordinator`. |
| 4 | Slicer: Risk Level | slicer (vertical list) | (616, 100, 280, 80) | `risk_level` (sort by `risk_level_sort`). |
| 5 | Top Risks | tableEx (table visual) | (24, 196, 800, 360) | Columns in order: `risk_id`, `risk_title`, `risk_category`, `[Risk Level Pill SVG]` (Data category Image URL, column header "Level"), `risk_score_overall` (column header "Score", format `0`), `risk_coordinator`, `[Days Since Last Update]` (format `0` + " d"). Sort: `risk_score_overall` desc. Top N filter: none (table is scrollable; show all in filter context). Row tooltip: full `mitigation_log` preview (truncate to 500 chars). |
| 6 | Risk Count by Coordinator | clustered horizontal bar | (840, 196, 416, 360) | Y-axis: `risk_coordinator` sorted by COUNTROWS desc. X-axis: COUNTROWS of `Risk_Register`. Color: `risk_low` (single accent, no risk-level breakdown — keeps focus on workload not severity). Data labels: on. |
| 7 | Recent Risk Updates | tableEx | (24, 572, 1232, 124) | Columns: `update_date` (desc, header "Date"), `risk_id`, `author`, `note` (word-wrap on, truncate visual cell to 120 chars). Top N filter (visual-level): 20 most recent. Sort: `update_date` desc. |

Drillthrough: right-click any `risk_id` cell on visual #5 → Drill through → Risk Detail (Page 3). DG: "Drill-through Design — Clear visual cues for drill-through availability."

### Page 3 — Risk Detail (drillthrough, hidden page, single-column narrative)

Page hidden from navigation; reachable only via right-click drillthrough from Page 2 Top Risks `risk_id`. Drillthrough filter: `risk_id`.

| # | Visual | Type | Position (x, y, w, h) | Data binding |
|---|---|---|---|---|
| 1 | Back button | actionButton | (24, 24, 80, 32) | Auto-populated by Power BI drillthrough back-action. |
| 2 | Risk title | textbox (dynamic) | (120, 24, 1136, 60) | `[Selected Risk Title]` (Semibold 22pt). |
| 3 | Meta strip | multi-row card | (24, 100, 1232, 80) | Six fields in one row: `risk_id`, `risk_category`, `risk_entity`, `risk_coordinator`, `risk_score_overall` (label "Score"), `[Risk Level Pill SVG]` (label "Level"). Optional 7th: `source_ref`. |
| 4 | Section label "Mitigation" | textbox | (24, 196, 1232, 32) | Static "Mitigation" (Semibold 14pt, `text_primary`, divider line below). |
| 5 | Mitigation paragraph | card (text) | (24, 236, 1232, 200) | `[Selected Risk Mitigation Log]`. Word-wrap on. Font Segoe UI 11pt. Vertical scroll on overflow. |
| 6 | Section label "Updates History" | textbox | (24, 452, 1232, 32) | Static "Updates History" (Semibold 14pt). |
| 7 | Updates history | tableEx | (24, 492, 1232, 204) | Filtered by drillthrough `risk_id`. Columns: `update_date` (desc, header "Date"), `author`, `note` (word-wrap on, full text). Sort: `update_date` desc. No row limit. |

Page 3 is single-column narrative per Phase 2 §c-Q3 lock: reads top-to-bottom like a memo (title → meta → mitigation → updates).

### Cross-page constants

- All pages: 24px outer margin, 16px inter-visual gap. DG: "Equal spacing is mandatory."
- Refresh date on Page 1 and Page 2 headers: implemented via a measure that reads either the model's last-refresh timestamp (Power Query helper) or a hardcoded text in the textbox during Phase 4-5; final choice in Phase 5.
- Filter pane visible on all pages, default-collapsed.

---

## e) Locked file and naming conventions

### Project layout

- PBIP project name: `Tonnelle_Risk`.
- PBIR format: enabled (preview required).
- Folder: `/pbip/` (creates `/pbip/Tonnelle_Risk.pbip`, `/pbip/Tonnelle_Risk.Report/`, `/pbip/Tonnelle_Risk.SemanticModel/`).
- The legacy `riskregister.pbip` + folders at project root: not used for this build. Confirm with user during the §g setup step whether to archive or delete; default action is leave-in-place (out of scope for Phase 3 lock).

### Naming

- Source-derived columns: `snake_case` exactly as they appear in Excel (`risk_id`, `risk_score_overall`, etc.). Do not rename. Phase 4 M code preserves Excel headers verbatim.
- Helper/derived columns: `snake_case` (`risk_level_sort`).
- Dim table prefix: `dim_` (used for `dim_Date` only).
- Helper table prefix: `_` (used for `_Measures`).
- Measures: `Title Case With Spaces`, no abbreviations except universally-recognized ones (`Avg`, `Max`). Always referenced with square brackets in DAX (`[Total Risks]`).
- Column references in DAX: always fully qualified with bracketed column name (`Risk_Register[risk_score_overall]`). Table prefix optional on the same table.

### TMDL display folders inside `_Measures`

Match the measure group names from §b: `Counts`, `Scores`, `TimeIntel`, `Display`. Each measure carries a description field populated in Phase 5 (DG: "Documented descriptions on tables/columns/measures").

### Page names

- Page 1: `Overview` (display: "Executive Overview").
- Page 2: `Detail` (display: "Risk Register Detail").
- Page 3: `RiskDetail` (display: "Risk Detail", hidden from nav).

---

## f) Deliberately accepted rule violations

Each item lists the rule, the violation, the justification, and the mitigation.

1. **SVG markup in DAX (`Risk Level Pill SVG`).**
   - DG rule: "Thin report measures should be used sparingly" and the general principle that measures should compute values, not return rendered markup.
   - Violation: a measure returns a `data:image/svg+xml;utf8,<svg>...</svg>` string.
   - Justification: turnover and CLAUDE.md lock the SVG pill technique; native Power BI conditional formatting cannot produce a rounded pill shape; the user has explicitly accepted the tradeoff.
   - Mitigation: raw `risk_level` column remains unhidden and is what slicers/sorts/filters use; cell tooltip exposes the raw level text; `;utf8,` is the primary encoding per CLAUDE.md, base64 documented as fallback if specific Power BI Desktop versions reject the utf8 prefix.

2. **Hidden `status` column.**
   - DG rule: typical practice exposes a status field as a slicer and KPI breakdown.
   - Violation: column is hidden in the PBI model, and no Open/Closed/Realized/Monitoring slicer or KPI exists.
   - Justification: Phase 1 audit found all 37 rows mark status="Open" despite mitigation_log carrying terminal events on several. Surfacing a stale field would mislead. Phase 2 §c-Q2 user lock: hide until backfilled.
   - Mitigation: column kept in the model (hidden) so it can be unhidden with no rebuild once Excel is backfilled. Report-level filter is set to `status = "Open"` for forward-compat; currently a no-op.

3. **No dim_Category, dim_Entity, dim_Coordinator.**
   - DG rule: "Star Schema: Are tables properly classified as dimension or fact?" recommends decomposition.
   - Violation: `Risk_Register` carries category/entity/coordinator as text columns rather than via dim tables.
   - Justification: Phase 2 §b1 lock. 37 rows; cardinality of would-be dims is 7/5/6. Decomposition adds three tables, three relationships, three sort keys, and a layer of indirection without supporting any visual that the wide form can't drive equally.
   - Mitigation: revisit if rows pass ~200 or a second contract is added.

4. **KPI cards without target or gap.**
   - DG rule (cards-and-kpis): "Always include a target and gap. If no clear target exists, ask the user — do not leave KPIs bare."
   - Violation: Page 1 KPI cards display single numbers (`Total Risks`, `High`, `Medium`, `Low`, `Avg Score`). No targets.
   - Justification: user explicit choice this turn. Risk counts and average score in a construction risk register are descriptive, not goal-driven. Inventing targets would mislead. Sparkline alternative considered and rejected per user choice ("bare cards with documented deviation").
   - Mitigation: High Risks card carries a single conditional color cue (if >10, value text uses `risk_high`); cards are kept compact so a future target/gap addition does not require a layout rework. Revisit Phase 5+ if user defines static thresholds.

5. **Heatmap palette uses divergent-style ramp, not single-hue sequential.**
   - DG rule (visual-colors): single-hue sequential is the textbook heatmap pattern; divergent scales are for two-sided data.
   - Violation: P-I matrix cells use a 3-band map from the green→yellow→red ends of the user's diverging palette.
   - Justification: user-supplied palette is divergent; the report's overall semantic vocabulary is risk = low/medium/high, which maps naturally to the divergent palette's endpoints plus midpoint. Score is one-sided but maps onto these bands without distortion.
   - Mitigation: cell text always shows the count number (color is not the only encoding); slicer for risk level provides text-driven access.

6. **Body and chart-cell text at 11pt rather than DG's 12pt floor.**
   - DG rule: "Minimum readable: 12pt."
   - Violation: 11pt body text, 10pt axis and data labels.
   - Justification: user lock on "dense informational" density; 1280-wide canvas comfortably reads 11pt for a desktop-viewing audience.
   - Mitigation: KPI value (32pt), visual titles (14pt Semibold), and the Page 3 narrative paragraph (11pt with generous line height) carry the typographic weight. Revisit if Phase 5+ accessibility review flags low-vision concerns.

---

## g) Required user-side actions before Phase 4 starts

These steps put `/pbip/Tonnelle_Risk.pbip` on disk in a state Phase 4 can consume.

1. **Open Power BI Desktop.** Enable preview features:
   - File → Options and settings → Options → **Preview features**
   - Check **Power BI Project (.pbip) save option**.
   - Check **Store semantic model using TMDL format** (PBIR enhanced metadata).
   - Restart Power BI Desktop after enabling.
2. **Create a blank PBIX** (File → New blank report).
3. **Save As Power BI project files** → navigate to the repo `/pbip/` folder → filename `Tonnelle_Risk` → Save. Power BI writes `Tonnelle_Risk.pbip` plus the `Tonnelle_Risk.Report/` and `Tonnelle_Risk.SemanticModel/` folders.
4. **PBIR upgrade prompt:** when Power BI prompts to upgrade to the PBIR enhanced metadata format, accept.
5. **Close Power BI Desktop.**
6. **Verify on disk:**
   - `/pbip/Tonnelle_Risk.pbip` exists.
   - `/pbip/Tonnelle_Risk.Report/` exists with `report.json`, `definition/pages/`, etc.
   - `/pbip/Tonnelle_Risk.SemanticModel/` exists with `definition/model.tmdl`, `definition/tables/`, etc.
7. **Confirm** in chat that the setup completed successfully. Do not modify the legacy `/riskregister.pbip` + `riskregister.Report/` + `riskregister.SemanticModel/` at the repo root in this session; that decision is deferred.

---

Locked. Awaiting user confirmation and PBIP setup before Phase 4.
