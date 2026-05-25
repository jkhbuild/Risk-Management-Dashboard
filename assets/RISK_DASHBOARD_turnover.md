# Risk Dashboard — Project Turnover (Tonnelle Avenue Bridge Relocation)

Hand this to a fresh chat to build the risk dashboard. Self-contained — no prior context needed.

## What this project is

A Power BI dashboard for a construction risk register, for the **Tonnelle Avenue Bridge
Relocation Project** — a SINGLE contract (unlike the prior 58 Devices project, which had two).
The user is a Senior Project Controls Engineer; this is a project-controls skill-building
deliverable and also goes on the user's portfolio site.

The user will PROVIDE a filled-in risk register Excel for Tonnelle Avenue (using the template
described below). The new chat does NOT invent risk data — it works from the user's file.

## What the user provides vs. what the new chat generates

- USER PROVIDES: `Tonnelle_Risk_Register_TEMPLATE.xlsx`, filled in — Project metadata,
  ~25-40 risks with probability/cost/schedule scores, and a `mitigation_log` text column
  containing dated update notes.
- NEW CHAT GENERATES: a separate **Risk_Updates** file, by splitting the `mitigation_log`
  column from the filled register into one row per dated update (regex-split on date markers
  like "1/13 -", "3/3 -"). Same technique used successfully on the prior 58 Devices project.

## The template (delivered: Tonnelle_Risk_Register_TEMPLATE.xlsx)

ONE workbook, THREE tabs:

1. **Project** — contract metadata (budget, JTD, NTP, durations, completion). One stub row,
   project_id `TONN-01`, name pre-filled, rest blank for the user. Also carries a short
   "how to use" note.
2. **Risk_Register** — 30 blank numbered rows (risk_id TONN-CON.01..30). Columns:
   - Inputs (blue): status, risk_category, risk_title, risk_type, probability_score,
     cost_impact_score, schedule_impact_score, risk_entity, risk_coordinator,
     mitigation_status, next_review_date, mitigation_log.
   - Formulas (black, do not edit): risk_score_cost = P*C, risk_score_schedule = P*S,
     risk_score_overall = P*MAX(C,S), risk_level = IF(overall>=15,"High",IF(>=8,"Medium","Low")).
   - Dropdown validation already applied (category, entity, status, and 1-5 / 0-5 numeric).
   - `mitigation_log` is where the user writes dated update notes — this is the SOURCE the
     new chat splits into the Risk_Updates table.
3. **Lookups** — rating scales (Probability/Cost/Schedule definitions, Risk Level bands) plus
   the dropdown source lists. Categories: Construction, Field Condition, Design Change, Safety,
   Environmental, Political. Entities: GDC, CM, Contractor, Shared. Statuses: Open, Closed,
   Monitoring, Realized.

### Recommended risk count
~25-40 risks for a good single-contract dashboard. Below ~20 the charts look thin; above ~50
the Top Risks table and matrix get crowded. Template ships with 30 rows; user adds/deletes freely.

## Risk scoring methodology (locked)

Risk Score = Probability x MAX(Cost Impact, Schedule Impact). Probability 1-5; Cost & Schedule
0-5. Store risk_score_cost and risk_score_schedule separately too, so the dashboard can show
cost-risk vs schedule-risk independently. Risk level bands: High >=15, Medium 8-14, Low 1-7.
Standards note: the P x I matrix is a qualitative screening tool (PMBOK / ISO 31000 / AACE
qualitative guidance). AACE's deeper emphasis is QUANTITATIVE risk (expected value, Monte Carlo,
contingency via the RP series). If this becomes an AACE-governed deliverable, verify methodology
against the actual AACE RP the user's firm references — do not cite an RP number without the source.

## Platform decision (locked)

- Power BI Desktop, Windows, personal Microsoft account (no work M365, no SharePoint, no
  Power BI service publishing).
- Excel is the data-entry layer; Power BI only displays. Humans edit Excel, never Power BI.
- Files live in a local folder; dashboard exports to PDF / screenshot as the deliverable.
- File structure: Project + Risk_Register + Lookups stay as TABS in the one provided workbook.
  Risk_Updates is generated as a SEPARATE file (it grows, it is edited often, isolate it).
  Lookups also gets rebuilt inside Power BI via "Enter data"; the Lookups tab additionally
  serves as the dropdown-validation source for data entry. Both uses are intentional.

## FUTURE CAPABILITY — do not break this

The user plans to add, LATER and via a Python script they write themselves in Claude Code,
an auto-update capability: a script that detects changes in Risk_Register and appends rows to
Risk_Updates. The new chat must NOT build this script. More importantly, NOTHING in the data
model or dashboard design may make this harder:
  - Risk_Updates must stay a plain, append-only flat table (update_id, risk_id, update_date,
    update_year, author, note). A script must be able to append a row with no side effects.
  - risk_id is the stable join key between Risk_Register and Risk_Updates. Do not change its
    format or make it a computed value.
  - Do not bury Risk_Updates inside the multi-tab workbook — it stays a separate file the
    script can open and write independently.

## Dashboard design — target (see risk_dashboard_mockup.png)

Two pages. NOTE: the mockup was built for the prior two-contract project; for Tonnelle it is
ONE contract — drop the per-project comparison (e.g. the trend chart has ONE line, not two;
no "by project" slicer). ALSO: the mockup shows the OLD category names (Const: Others, etc.).
Tonnelle uses NEW categories — Construction, Field Condition, Design Change, Safety,
Environmental, Political — and entities GDC, CM, Contractor, Shared. Use the categories/entities
from the user's filled template, not the mockup image.

**Page 1 — Executive Overview**
- KPI cards: Total Risks, High, Medium, Low, Avg Risk Score.
- Probability-Impact matrix, 5x5 heat grid, count per cell, red/amber/green by score band.
- Risks by Category, stacked horizontal bar split by risk level.
- Risk Score Trend Over Time — line chart, avg overall score by month (ONE line for Tonnelle),
  powered by Risk_Updates. Headline new capability.

**Page 2 — Risk Register Detail**
- Top Risks table sorted by overall score.
- Risk Count by Coordinator — horizontal bar (workload view).
- Recent Risk Updates — feed from Risk_Updates, most recent dated entries.
- Slicers: Category, Coordinator (no Project slicer — single contract).

**Page 3 — Risk Detail (DRILLTHROUGH page)**
The user wants to click a risk and read its full mitigation plan / update history (the
mitigation text is too long to show in a table cell). Implement this as a native Power BI
DRILLTHROUGH page — NOT a bookmark-modal (doesn't scale per-record) and not just a tooltip
(hover-only, size-capped).
  - Create a hidden report page "Risk Detail".
  - Add risk_id (or risk_title) to its Drillthrough filter well.
  - On it, show: the selected risk's full fields, the complete proposed mitigation text, and
    that risk's entire Risk_Updates history as a dated list/table.
  - From the Page 2 Top Risks table, right-click a row -> Drill through -> Risk Detail.
  - Include a Back button (Power BI adds one automatically on drillthrough pages).
This is the native, sustainable way to do "click a row, read the whole record."

### Risk-level styling — PILLS (user wants these)
The user wants rounded "pill" badges for the risk_level column, as shown in the mockup.
This IS achievable in Power BI, NOT natively but via an SVG measure:
  - Write a DAX measure that returns an SVG string (a rounded <rect> + <text> with the level
    text and a fill color keyed to High/Medium/Low).
  - Set that column's Data category to "Image URL" so Power BI renders the SVG.
  - This is a real, supported technique (widely shown in tutorials). It is a workaround, not a
    native setting, so expect ~20-30 min to get right and the measure is markup-in-DAX to
    maintain. The user has accepted this tradeoff and wants the pills.
  - Build the SVG pill measure for risk_level on the Page 2 Top Risks table.
  - Colored cell background is the simpler fallback if the SVG measure misbehaves, but the
    user's stated preference is the pills — deliver the pills.

## Known Power BI gotchas (from the prior build — apply preemptively)

- Sort-order columns -> build as Power Query CONDITIONAL COLUMNS, never DAX calculated columns.
  DAX calculated columns for sort keys throw circular dependency errors.
- Table fan-out: pull related attributes through the row's own foreign key (LOOKUPVALUE)
  rather than dragging fields straight from a dimension table. A measure showing the same
  value on every row = a cross-filter direction problem; set the relationship to Both if a
  fact table needs to be filtered from its dimension.
- Put all measures in a dedicated `_Measures` table (Enter data, hide the dummy column).
- "Show items with no data" is a right-click option on the field in the well, not a format setting.
- Page-level Format pane (Canvas settings) only shows when nothing is selected.

## Status / next steps for the new chat

1. User uploads the FILLED Tonnelle_Risk_Register_TEMPLATE.xlsx.
2. Generate the separate Risk_Updates file by splitting the mitigation_log column into dated
   rows. Flag any year-ambiguous dates for the user to verify.
3. Confirm validation is intact on the filled register.
4. Build Power BI: connect to the workbook tabs, model relationships, measures, Page 1, Page 2.
   - Relationship: Risk_Updates -> Risk_Register (many-to-one on risk_id).
   - Risk_Register -> Project (many-to-one on project_id) — trivial, single project, but keep it.
5. Build the SVG pill measure for risk_level.
6. Build the Page 3 Risk Detail drillthrough page (full mitigation text + that risk's
   Risk_Updates history); wire right-click drillthrough from the Page 2 Top Risks table.

## Files
- Tonnelle_Risk_Register_TEMPLATE.xlsx — the blank template the user fills (3 tabs).
- risk_dashboard_mockup.png — visual target (built for 2 contracts; adapt to 1).
- This turnover sheet.
