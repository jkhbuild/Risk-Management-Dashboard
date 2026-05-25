# Claude Code Prompt Set: Tonnelle Risk Dashboard

Reference document. Each numbered phase below is one Claude Code session. Copy that session's prompt into Claude Code as the opening message, and produce the listed deliverable. Do not skip phases. Do not combine phases in one session unless explicitly noted.

---

## Project-management notes (read once, before Phase 0)

### Skill installation sequence

Install these in your skills folder before Phase 0:

```
npx skills add https://github.com/github/awesome-copilot --skill power-bi-report-design-consultation
npx skills add https://github.com/data-goblin/power-bi-agentic-development --skill pbi-report-design
npx skills add https://github.com/github/awesome-copilot --skill power-bi-modeling
npx skills add https://github.com/github/awesome-copilot --skill power-bi-dax-optimization
```

The first two conflict and must not be active at the same time. The prompts below specify which is loaded in which phase.

### Project folder layout (Phase 0 creates this)

```
/Tonnelle_Risk_Dashboard
├── CLAUDE.md                       # auto-loaded context
├── RISK_DASHBOARD_turnover.md      # spec, treat as source of truth
├── /source_data
│   ├── Tonnelle_Risk_Register_260519.xlsx
│   └── Tonnelle_Risk_Updates_260519.xlsx
├── /assets
│   ├── risk_dashboard_mockup.png
│   └── theme.json                  # produced in Phase 8
├── /docs                           # all 01-13 deliverables land here
├── /pbip                           # PBIP project lives here after Phase 3
│   └── (Tonnelle_Risk.Report, Tonnelle_Risk.SemanticModel, Tonnelle_Risk.pbip)
└── /scripts
    ├── append_updates.py           # produced in Phase 12
    └── requirements.txt
```

### Session hygiene rules baked into every prompt

1. Read the listed inputs first. Do not start work without confirming the files exist.
2. Produce only the listed deliverable. Do not expand scope.
3. Ask before any destructive change: deleting files, rewriting locked design specs, modifying the source Excel files.
4. End each session with a chat-only summary of the top three findings or decisions. Do not pad.
5. If a question cannot be resolved from the files alone, add it to an "Open Questions" section in the deliverable and stop on that point.
6. When the listed deliverable for the phase is complete, summarize in chat and stop. Do not begin the next phase. This rule is repeated at the end of every phase prompt for redundancy.

### What this prompt set assumes about format and tooling

- Final file format is PBIP with the new PBIR (preview). Phase 3 covers conversion.
- powerbi-modeling-mcp is held in reserve. It is not used until Phase 6 (measure verification). All earlier sessions edit files only.
- The user is on Windows, Power BI Desktop Microsoft Store version, personal Microsoft account, no Power BI service publishing.

### What this prompt set is NOT

It is not a substitute for design judgment. Claude Code is instructed in each phase to challenge specifics. Expect to negotiate.

---

## Phase 0 — Project bootstrap

**Skills loaded:** none.

**Prompt:**

```
You are bootstrapping a project folder. The user has placed these files in the working directory:

- RISK_DASHBOARD_turnover.md
- Tonnelle_Risk_Register_260519.xlsx
- Tonnelle_Risk_Updates_260519.xlsx
- risk_dashboard_mockup.png

This session is setup only. No design work. No data inspection beyond confirming files exist.

Tasks:

1. Create the following folder structure at project root:
   /source_data, /assets, /docs, /pbip, /scripts.
   Move the two Excel files into /source_data and the mockup PNG into /assets.

2. Create CLAUDE.md at project root with this content:
   - One-line project description: Tonnelle Avenue Bridge Relocation risk dashboard, single contract, internal Naik leadership audience, portfolio deliverable.
   - Source of truth: RISK_DASHBOARD_turnover.md.
   - Style: legal-memo concision, no em-dashes, no marketing language.
   - Constraints: ask before destructive changes; do not modify files under /source_data; do not modify locked design specs in /docs.
   - Skill loading reminder: each phase prompt specifies which skill to load; do not activate skills outside the specified phase.

3. Create .gitignore appropriate for a PBIP plus Python plus Excel project. Exclude Excel temp lock files (~$*.xlsx), Python __pycache__, .DS_Store, and Power BI Desktop user state (CustomVisuals cache, etc.). Keep PBIP folders tracked.

4. Verify the four installed skills are present in the skills directory:
   - power-bi-report-design-consultation (awesome-copilot)
   - pbi-report-design (data-goblin)
   - power-bi-modeling (awesome-copilot)
   - power-bi-dax-optimization (awesome-copilot)
   List which are present, which are missing. Do not install missing ones; the user installs.

5. Confirm RISK_DASHBOARD_turnover.md is present at project root and readable.

Deliverable: no markdown file this phase. Output a chat-only summary of:
- Folder structure created (file tree)
- Files moved (from-to)
- CLAUDE.md key clauses
- Skills present vs. missing
- Anything the user must hand-fix before Phase 1

Stop after summary. Do not begin audit.
```

---

## Phase 1 — Data audit and reconciliation

**Skills loaded:** none.

**Prompt:**

```
Read these inputs:

- /RISK_DASHBOARD_turnover.md (source of truth for spec)
- /source_data/Tonnelle_Risk_Register_260519.xlsx (3 tabs: Project, Risk_Register, Lookups)
- /source_data/Tonnelle_Risk_Updates_260519.xlsx
- /assets/risk_dashboard_mockup.png (visual target; built for prior 2-contract project, adapt to 1)

This session is discovery only. Do not propose schema changes. Do not write DAX. Do not touch the PBIP folder. Do not modify source files.

Produce /docs/01_audit.md covering:

a) Risk_Register state.
   - Row count, column inventory.
   - Distribution of risk_level (High/Medium/Low counts) and verify these match the formula risk_score_overall = probability * MAX(cost_impact, schedule_impact) and the bands High>=15, Medium 8-14, Low 1-7.
   - Distribution by risk_category and by risk_entity.
   - Reconcile risk_category values in the Register against the category_list in the Lookups tab AND against the locked category list in turnover. Flag any category present in data but not in turnover's locked list.
   - Reconcile risk_entity values the same way.
   - Blank required fields (status, risk_coordinator, probability_score, cost_impact_score, schedule_impact_score).
   - next_review_date column: confirm Excel serial date interpretation, list any dates outside a reasonable window.

b) Risk_Updates state.
   - Row count, date range (after converting update_date from Excel serial).
   - Distribution by update_year (per turnover, year disambiguation should already be done; verify).
   - Orphan rows: any risk_id in Updates that is not in Register.
   - Coverage: which Register risks have zero Updates entries.

c) Cross-file reconciliation: Register mitigation_log column vs. Updates note column.
   For each risk, compare the dated notes in mitigation_log against the matching update_date rows in Updates. Flag any divergence in text content for the same date. Hypothesize which file is the lead source.

d) Risk Score Trend feasibility check. The mockup Page 1 shows "Risk Score Trend Over Time" as a line chart of avg overall score by month. The data model only stores CURRENT scores on Register, and EVENTS (not score deltas) on Updates. Document explicitly: with the current schema, what does a line chart of "score over time" actually plot? List the candidate interpretations:
   1. Avg score of risks that had any update in month M
   2. Count of updates per month
   3. Cumulative risks identified by update_date
   4. Something else
   Do not pick one. Surface this as the single biggest open question for the user.

e) Open questions section. List anything ambiguous that the user must answer before Phase 2 can proceed.

End the session with chat-only summary of the top three audit findings. Stop. Do not begin Phase 2.
```

---

## Phase 2 — Schema challenge (exploratory)

**Skills loaded:** `power-bi-report-design-consultation` (awesome-copilot). The data-goblin design skill must NOT be active this session.

**Prompt:**

```
Load the power-bi-report-design-consultation skill. Confirm it is the only Power BI design skill active. If pbi-report-design (data-goblin) is loaded, unload it first.

Read:

- /RISK_DASHBOARD_turnover.md
- /docs/01_audit.md
- The user's chat answers to your open questions from Phase 1 (in the prior chat turn; if no answers, ASK the user before proceeding).
- /source_data/* if you need to verify specifics.

This is the exploratory pass. Be generous with alternatives, raise questions, do NOT lock anything down. The next session locks the design under the stringent skill.

Produce /docs/02_schema_challenge.md covering:

a) Current implied schema. Diagram in plain text:
   - Fact-like tables: Risk_Register, Risk_Updates.
   - Dim-like: Project (single row), Lookups (rebuilt in Power BI via Enter data per turnover).
   - Relationships: Risk_Updates -> Risk_Register on risk_id (M:1); Risk_Register -> Project on project_id (M:1).
   - No date table currently.

b) Challenge it. For each decision below, present for/against and a recommendation:

   1. Risk_Register as a wide fact-like table vs. decomposing into a star with separate dim_Category, dim_Entity, dim_Coordinator. Consider: dataset is ~37 rows, star schema adds modeling overhead, but coordinator workload visuals on Page 2 benefit from a proper dim.
   2. Lookups rebuilt in Power BI via "Enter data" vs. imported from the Excel Lookups tab. Per turnover, Excel Lookups serves dual duty (dropdown source AND in-Power BI reference). Confirm this is still correct.
   3. Score columns as Excel formulas vs. DAX measures vs. Power Query calculated columns. Per turnover they are Excel formulas; defend or challenge.
   4. Sort-order columns as Power Query conditional columns (per turnover gotcha) vs. DAX. Confirm this is right for risk_level Low/Medium/High ordering.
   5. Date table strategy. The trend chart needs time intelligence. Options: DAX CALENDAR + relationship to update_date; M-generated date table; live date column on Updates with no separate dim. Recommend.
   6. Risk_level pill rendering. Turnover demands SVG measure with column Data category Image URL. The consultation skill may have an opinion on markup-in-DAX. Surface the tradeoff.

c) Open design questions for the user about visual identity and target audience:

   1. Audience is internal Naik leadership / portfolio view. Does the visual identity follow Naik brand colors, MTA brand colors (mockup shows MTA navy header), or a neutral professional palette? Ask the user.
   2. Density preference: dense informational vs. spacious executive.
   3. Drillthrough page (Page 3) layout philosophy: single-column readable narrative, two-column reference layout, or compact card grid.
   4. The Risk Score Trend Over Time chart. Per Phase 1's open question, what does the line plot? Push the user to pick one of the candidate interpretations. If the user is unsure, present your recommendation with reasoning.
   5. The Excel data shows categories Financial and entity Designer that are NOT in the turnover's locked lists but ARE in the Lookups tab. Ask the user: extend the locked lists to include these, or correct the data.

d) Mockup deviations. The mockup was built for the prior 58 Devices 2-contract program. List deviations to apply for Tonnelle:
   - Drop project slicer (single contract).
   - Trend chart is one line, not two.
   - Header bar title and subtitle.
   - Category labels use the new Tonnelle list, not the mockup's Const: Others etc.

End document with: "These options remain open. Lock under stringent skill in Phase 3."

End chat with top three challenges. Stop. Do not lock anything.
```

---

## Phase 3 — Design lock (stringent) and PBIP setup direction

**Skills loaded:** `pbi-report-design` (data-goblin). Unload the awesome-copilot consultation skill before starting.

**Prompt:**

```
Unload power-bi-report-design-consultation. Load pbi-report-design from data-goblin. Confirm only one design skill is active.

Read:

- /RISK_DASHBOARD_turnover.md
- /docs/01_audit.md
- /docs/02_schema_challenge.md
- The user's chat answers to your Phase 2 open questions. If any remain unanswered, ASK now; do not assume.

This session locks the spec. After this point, downstream phases reference this file and do not revisit decisions.

Apply the data-goblin pbi-report-design skill rules to every decision. Any deviation from the skill's rules must be explicitly documented with justification.

Produce /docs/03_design_locked.md covering:

a) Locked schema. Tables (name, role: fact/dim/parameter/helper), columns (name, type, format string, default summarization), relationships (from -> to, cardinality, cross-filter direction, active/inactive flag), date table strategy. Each major decision: cite the data-goblin rule applied.

b) Locked measure architecture. List measure groups and the measures within each. One-line intent per measure. NO DAX YET, just signatures and intent. Suggested groups:
   - _Measures.Counts (Total Risks, High Risks, Medium Risks, Low Risks, Open Risks, Closed Risks)
   - _Measures.Scores (Avg Risk Score Overall, Avg Cost Score, Avg Schedule Score, Max Risk Score)
   - _Measures.TimeIntel (Avg Score by Update Month or whatever Page 2 question 4 resolved to)
   - _Measures.Display (SVG_Pill_Risk_Level)

c) Locked theme. Color palette with hex values, typography, visual default formatting standards. Per the user's answer to audience question. Build the table of palette tokens that theme.json (Phase 8) will implement.

d) Locked page-by-page layout. For each of 3 pages, in reading order: visual type, position (rough grid), data binding (fields, measures, sort, top N, slicers, filters). No JSON yet.

e) Locked file and naming conventions.
   - PBIP project name: Tonnelle_Risk
   - PBIR format: enabled (preview)
   - Folder: /pbip/
   - DAX naming: snake_case for columns, Title Case With Spaces for measures, [Brackets] always.
   - TMDL display folder names match the measure group names from section (b).

f) Deliberately accepted rule violations. The SVG pill measure violates the skill's likely "no markup in DAX" rule. Document the tradeoff and the user's accepted choice.

g) Required user-side actions before Phase 4 starts:
   1. Open Power BI Desktop. Enable preview features: Power BI Project (.pbip) save option, AND the new PBIR enhanced metadata format.
   2. Create a blank PBIX in Power BI Desktop. Save As > Power BI project files > /pbip/Tonnelle_Risk.pbip.
   3. Power BI Desktop will prompt to upgrade to PBIR; accept.
   4. Close Power BI Desktop. Confirm /pbip/Tonnelle_Risk.Report and /pbip/Tonnelle_Risk.SemanticModel folders exist with TMDL and JSON contents.

End chat with: "Locked. Awaiting user confirmation and PBIP setup before Phase 4." Wait for user explicit approval before stopping. Do not modify any file outside /docs/.
```

---

## Phase 4 — Power Query (M) code

**Skills loaded:** `power-bi-modeling` (awesome-copilot).

**Prompt:**

```
Load power-bi-modeling. The pbi-report-design skill may remain loaded for cross-check; design is locked, but its rules still inform any modeling decision.

Read:

- /RISK_DASHBOARD_turnover.md
- /docs/03_design_locked.md (the binding spec)
- /source_data/Tonnelle_Risk_Register_260519.xlsx
- /source_data/Tonnelle_Risk_Updates_260519.xlsx

This session: write Power Query M expressions for every table in the locked schema. Output to /docs/04_power_query.md. One fenced ```m block per table, with the table name as an h3 heading.

Tables to deliver per /docs/03_design_locked.md (verify):
- Risk_Register (Excel source, Risk_Register sheet)
- Risk_Updates (Excel source, Risk_Updates sheet)
- Project (Excel source, Project sheet)
- Date (calculated table or M-generated; per locked spec)
- Any dimensions locked in Phase 3 (dim_Category, dim_Entity, dim_Coordinator if locked)

Rules for every M block:
- Type every column explicitly. No null typed columns.
- Column names match locked conventions in /docs/03_design_locked.md.
- Sort-order keys as conditional columns in M, per turnover gotcha. risk_level_sort: High=3, Medium=2, Low=1 (or whatever the locked spec says).
- Excel serial date columns (update_date, next_review_date) converted to proper Date type using Date.From.
- Data-quality steps from /docs/01_audit.md (e.g., normalize Construction vs. construction case if any was flagged) applied here, with a comment line noting the audit finding being addressed.
- Source path: parameterize at top of each query so the user can change folder location without editing every query. Use a Source_Folder parameter.

After the M blocks, include a section "User-side steps to apply":
1. Open /pbip/Tonnelle_Risk.pbip in Power BI Desktop.
2. Home > Transform data > Advanced Editor for each table.
3. Paste the corresponding M block.
4. Apply changes, verify row counts match audit findings.
5. Set the Source_Folder parameter to the absolute path of /source_data/.

Alternative: if the user prefers TMDL-direct editing, document the partition file paths and the partition.tmdl syntax for each query. But default to Advanced Editor paste-in.

Do not modify the Excel files. Do not modify the PBIP folder this session. Output is /docs/04_power_query.md only.

## Self-verification (run before declaring the deliverable complete)

Use bash, openpyxl, pandas, or the extract-text tool to inspect the source Excel files directly. Do not rely on the M expressions you wrote; verify against the actual source.

1. Source row counts. Read Risk_Register, Risk_Updates, and Project. Count data rows excluding header. Document these as EXPECTED post-load row counts in /docs/04_power_query.md. The user verifies these match after pasting into Power BI Desktop.
2. Column inventory match. For each M expression, list the source columns referenced. Cross-check every name exists in the source Excel sheet. Any mismatch is a bug; fix before declaring done.
3. Type assignment completeness. Every column in every M block must have an explicit Type assignment. Grep your M output for any column without a type or typed as `type any`. Any such case is a deficiency; explain in the deliverable if intentional.
4. Date conversion check. Sample one update_date value from the source (e.g., 45912). Verify the M expression converts it correctly using Date.From and the 1900 date system. Document one worked example.
5. Sort-order column trace. For risk_level_sort, hand-trace one example per level (High, Medium, Low) and verify the conditional column produces the expected sort key per /docs/03_design_locked.md.
6. Source path parameterization. Confirm a Source_Folder parameter is declared at the top and every absolute path references it.
7. M syntax balance. For each M block, verify `(`/`)`, `[`/`]`, `{`/`}` balance via bash count.

If any check fails, iterate. If a check cannot run in this environment, document the gap explicitly and tell the user to run it manually.

End chat with summary of any data-quality steps included and any row-count expectations that must hold. Stop. Do not begin Phase 5.
```

---

## Phase 5 — Semantic model and core measures

**Skills loaded:** `power-bi-modeling` and `power-bi-dax-optimization`. Both active.

**Prereq:** User has applied the M code from Phase 4 to the PBIP.

**Prompt:**

```
Load power-bi-modeling and power-bi-dax-optimization. Confirm both active.

Read:

- /docs/03_design_locked.md
- /docs/04_power_query.md
- /pbip/Tonnelle_Risk.SemanticModel/* (TMDL files; if not yet present, ASK the user to confirm Phase 4 is complete before proceeding)

This session: edit TMDL directly. Two deliverables.

A) Model structure edits in /pbip/Tonnelle_Risk.SemanticModel/:
   1. Relationships per /docs/03_design_locked.md. Edit relationships.tmdl (or the equivalent).
   2. Hidden columns for foreign keys not exposed in visuals.
   3. Display folders for measure organization, matching the group names from /docs/03_design_locked.md section (b).
   4. _Measures helper table per turnover gotcha. Create via TMDL: a table with one hidden dummy column, then all measures attached. If TMDL syntax for "Enter data" is awkward, document the user-side click instead.
   5. Mark the Date table as a date table.

B) Core measures in DAX. Write measures from /docs/03_design_locked.md groups _Measures.Counts and _Measures.Scores only. For each measure:
   - Place in the correct display folder.
   - One-line block comment with intent and the visual(s) that will consume it.
   - Apply data-goblin DAX optimization heuristics: prefer SUMX over iterating tables when avoidable; use CALCULATE with simple filter args; avoid unneeded ALL.

Do NOT write yet:
- Time intelligence measures (Phase 6)
- SVG pill measure (Phase 7)

Output:
- TMDL file edits directly in /pbip/Tonnelle_Risk.SemanticModel/.
- /docs/05_semantic_model.md log of: every file changed, what was added, any user-side step required.

Ask before deleting any existing TMDL content. If a TMDL file has user-created measures not in the spec, ASK before touching them.

## Self-verification (run before declaring the deliverable complete)

1. TMDL syntax parse. Hand-parse every file edited for: balanced braces, every measure has a definition expression, every relationship declares fromTable, fromColumn, toTable, toColumn, and cardinality.
2. Measure name uniqueness. Grep all measure definitions across TMDL files; no duplicates.
3. Display folder coverage. Every measure has displayFolder matching one of the locked groups in /docs/03_design_locked.md section (b). Any measure without a display folder is a deficiency.
4. Relationship match. For each relationship locked in /docs/03_design_locked.md, find the corresponding TMDL block and verify every property matches. Document any deviation.
5. Expected test values. Using openpyxl/pandas against the source Excel, compute the expected value of each _Measures.Counts and _Measures.Scores measure. Example: [High Risks] should equal the count of Register rows where risk_level = "High". Document expected values in /docs/05_semantic_model.md as a table: measure name, expected value, source-data computation. The user verifies these in Power BI after refresh.
6. MCP cross-check (optional). If the powerbi-modeling-mcp is active and Power BI Desktop has the project open, query the live model for each measure and compare to the expected values. Document any mismatch.

If TMDL parse fails or expected-value computation cannot be done, iterate or document the gap.

End chat with: list of measures created, list of relationships set, any verification step the user must run in Power BI Desktop (e.g., open the file, check that visuals can find the measures). Stop. Do not begin Phase 6.
```

---

## Phase 6 — Time intelligence and trend measures

**Skills loaded:** `power-bi-dax-optimization`. Optionally start the powerbi-modeling-mcp server now to test measures live.

**Prompt:**

```
Load power-bi-dax-optimization.

Optional: if the user has the powerbi-modeling-mcp server configured and Power BI Desktop open on /pbip/Tonnelle_Risk.pbip, you may use the MCP to query the live model and validate measures. If not, file edits only.

Read:

- /docs/03_design_locked.md (specifically the trend chart locked interpretation from Phase 2 question 4)
- /docs/05_semantic_model.md
- /pbip/Tonnelle_Risk.SemanticModel/* (current TMDL state)

This session: build only the time-intelligence layer that drives the Page 1 Risk Score Trend Over Time line chart.

Per /docs/03_design_locked.md, the locked interpretation of the trend chart is [verify in the locked doc]. Build the measures that implement that interpretation. Examples depending on the lock:

- If locked as "avg score of risks updated in month M": measure that filters Risk_Updates to month M, gets distinct risk_id, joins to Risk_Register, returns AVERAGE of risk_score_overall.
- If locked as "count of updates per month": COUNTROWS(Risk_Updates) with date filter.
- If locked as "cumulative risks identified by month": running total of distinct risk_id over Date.

For each measure:
- Place in _Measures.TimeIntel display folder.
- Header comment with intent.
- Optimization pass: identify expensive patterns (CALCULATE inside iterators, SUMX over fact table) and rewrite where the data-goblin optimization skill flags an alternative.

Verify the Date table is wired correctly:
- Marked as date table.
- Relationship Date[date_key] to Risk_Updates[update_date] active.
- Date table covers the full Updates date range plus a buffer.

If MCP is active: run a DAX query to evaluate each measure across the actual month range. Report results in the deliverable.

Output:
- TMDL edits to /pbip/Tonnelle_Risk.SemanticModel/.
- /docs/06_time_intel.md with: measure DAX, intent, verification results if MCP used, any performance flags.

## Self-verification (run before declaring the deliverable complete)

1. Date table coverage. Compute min and max of update_date from Risk_Updates source. Date table must span at least this range plus the locked buffer per /docs/03_design_locked.md.
2. Date table marking. Grep SemanticModel TMDL for the date-table marker (dataCategory or equivalent). Must be present.
3. Active relationship to Date. The relationship from Risk_Updates[update_date] to Date[date_key] (or equivalent) must be active. Verify in TMDL.
4. Pre-computed trend values. Using pandas or openpyxl, group Risk_Updates by month and compute the locked trend interpretation. Document these expected monthly values in /docs/06_time_intel.md as a table. The Page 1 line chart should reproduce these exactly when bound to the measure.
5. MCP cross-check (optional). If MCP is active, evaluate the time-intel measure for each month and compare to the expected values above.
6. Performance flags. Scan each measure for known antipatterns: SUMX over a fact table without context filter, nested CALCULATE, ALL applied unnecessarily. Apply data-goblin optimization rules. Document any deferred optimizations.

Iterate or document gaps.

End chat with summary of the trend chart data signature (what the line will actually plot, with example values from real months). Stop. Do not begin Phase 7.
```

---

## Phase 7 — SVG pill measure

**Skills loaded:** `power-bi-dax-optimization`.

**Prompt:**

```
Read:

- /docs/03_design_locked.md (color palette tokens; SVG pill section)
- /docs/05_semantic_model.md

This session has ONE deliverable: the SVG pill measure for risk_level on the Page 2 Top Risks table.

Requirements:
- DAX measure returns an SVG string. Format: data:image/svg+xml;utf8,<svg ...>...</svg>.
- A rounded <rect> as the pill background. Fill color keyed to High / Medium / Low per locked palette.
- Centered <text> showing the risk_level label. Font: Segoe UI (resolves on Windows and in Power BI rendering).
- Text width should not overflow on the longest label (Medium). Pill width sized accordingly.
- Place measure in _Measures.Display.

Test before delivering:
1. Render the SVG output for each level (High, Medium, Low) by writing the SVG content (without the data: prefix) to /assets/test_pill_high.svg, _medium.svg, _low.svg.
2. Open each in a browser or describe the rendered output. Confirm centering, fill, text contrast.
3. If you have access to render in the chat, do so.

User-side step: in Power BI Desktop, select the column that consumes the measure (typically the risk_level column on the Top Risks visual), set Data category to "Image URL", and increase row height so the pill is visible.

Output:
- TMDL edit (the measure added to _Measures.Display).
- 3 test SVG files in /assets/.
- /docs/07_svg_pill.md with: measure DAX, rendering screenshots or descriptions, the user-side Data category instruction, and the explicit note that this is the accepted deviation from "no markup in DAX" per /docs/03_design_locked.md section (f).

## Self-verification (run before declaring the deliverable complete)

1. SVG materialization. For each of three risk_level values (High, Medium, Low), evaluate the DAX measure logic and write the resulting SVG to /assets/test_pill_<level>.svg (without the `data:image/svg+xml;utf8,` prefix).
2. XML well-formedness. Run `xmllint --noout` on each test SVG file. Must parse without error.
3. Visual rendering check. Render each SVG to PNG using a headless tool (e.g., `cairosvg`, `rsvg-convert`, or Chrome headless). Inspect or describe:
   - Pill background fill matches the locked High/Medium/Low palette hex.
   - Text is horizontally and vertically centered.
   - Text does not overflow the pill bounds for the longest label (Medium).
4. Data URL prefix. The full measure output must start with `data:image/svg+xml;utf8,`. Verify the DAX concatenation produces this prefix.
5. Color-match against locked palette. Grep the SVG output for each fill color and confirm exact hex match against /docs/03_design_locked.md palette. No improvised colors.

If any test fails, iterate the DAX until it passes. If browser/PNG rendering is unavailable in the environment, document the expected appearance in writing and tell the user to verify visually after Power BI loads.

End chat with one sentence: pill measure shipped, ready for Page 2 binding. Stop. Do not begin Phase 8.
```

---

## Phase 8 — Theme JSON

**Skills loaded:** `pbi-report-design` (data-goblin).

**Prompt:**

```
Load pbi-report-design.

Read:

- /docs/03_design_locked.md (theme section, palette tokens)
- /assets/risk_dashboard_mockup.png (for layout intent and feel; do NOT copy the old category labels)
- /pbip/Tonnelle_Risk.Report/ to understand current report-level theme state

This session: produce /assets/theme.json, a Power BI custom theme file.

Use the locked palette from /docs/03_design_locked.md. Reference the mockup for visual feel only (KPI card style, header bar style, table density), not for any data labels.

Required sections in theme.json:
- name (Tonnelle_Risk_Naik or per locked spec)
- dataColors (semantic High/Medium/Low plus 3-5 neutral series)
- background, foreground, tableAccent, secondBackground
- visualStyles for the visual types used in the 3 pages: card, table, matrix, lineChart, barChart (stacked horizontal), slicer
- KPI card defaults that match the mockup's compact style (large value, label above, sub-label below)
- typography: font family, sizes for title/header/label/data per locked spec

Validate:
- JSON parses (no trailing commas, valid Power BI schema). Run a JSON linter.
- Hex colors match the locked palette exactly. No improvisation.
- The visualStyles block does not over-specify formatting that would conflict with future Page 1/2/3 visual-level settings.

Output:
- /assets/theme.json
- /docs/08_theme.md documenting palette choices with hex values, font choices, and the data-goblin rules being applied.

User-side step (one click): in Power BI Desktop, View > Themes > Browse for themes > select /assets/theme.json.

Do not modify the PBIP report files this session. Theme application is a single user-side click.

## Self-verification (run before declaring the deliverable complete)

1. JSON parse. Run `python -c "import json; json.load(open('/assets/theme.json'))"`. Must succeed.
2. Hex exactness. Grep every hex value in theme.json. Cross-check against the /docs/03_design_locked.md palette table. Any color not in the locked palette is a deviation; document why or remove.
3. Trailing commas. Grep for `,]` or `,}` patterns; must return zero matches.
4. dataColors length. Confirm the array contains at least 8 entries for chart series fallback. List them in /docs/08_theme.md.
5. visualStyles coverage. List the visualType keys present in visualStyles. Cross-reference against the visuals actually used across Pages 1, 2, and 3 per /docs/03_design_locked.md. Remove any unused entries. Note any visual type used but missing from visualStyles (these fall back to Power BI defaults).
6. Schema sanity. The Power BI custom theme JSON schema is documented at learn.microsoft.com/power-bi/create-reports/desktop-report-themes. Spot-check that no required keys are misspelled and no unrecognized keys are present.

Iterate or document gaps.

End chat with one sentence: theme shipped, ready for Page 1. Stop. Do not begin Phase 9.
```

---

## Phase 9 — Page 1: Executive Overview

**Skills loaded:** `pbi-report-design`.

**Prompt:**

```
Load pbi-report-design.

Read:

- /docs/03_design_locked.md (Page 1 locked layout, visual list with bindings)
- /docs/05_semantic_model.md, /docs/06_time_intel.md (measures available)
- /docs/08_theme.md (theme tokens)
- /pbip/Tonnelle_Risk.Report/definition/pages/ (current PBIR state)
- /assets/risk_dashboard_mockup.png (visual reference)

This session: build Page 1 of the report. Edit PBIR files under /pbip/Tonnelle_Risk.Report/definition/pages/. Verify the PBIR format on read; PBIR splits per-visual JSON across files, do not assume the legacy single-JSON layout.

Page 1 visuals per /docs/03_design_locked.md (verify):
1. Header bar (title, subtitle, page indicator 1 of 3)
2. KPI cards: Total Risks, High, Medium, Low, Avg Risk Score
3. Probability-Impact Matrix (5x5 grid, count per cell, color by risk score band)
4. Risks by Category stacked horizontal bar split by risk level
5. Risk Score Trend Over Time line chart (bound to the time-intel measure from Phase 6)

For each visual:
- Bind to the measures from Phase 5-6.
- Apply theme defaults (the theme should handle most styling).
- Apply "Show items with no data" via the right-click menu on the field in the well, where the locked spec requires it.
- Cross-filter behavior: clicking a category bar filters KPIs and matrix; clicking a matrix cell filters the category bar and trend chart. Verify cross-filter direction does not collapse the trend chart to single-month.
- Page background, gridlines, spacing per /docs/08_theme.md.

Do NOT build Page 2 or Page 3 this session.

Output:
- Direct PBIR file edits.
- /docs/09_page1.md log of: visual list shipped, measures bound, any user-side click required in Power BI Desktop (some PBIR JSON features still need a UI click to take effect).

User-side step at end: open the PBIP, refresh, confirm Page 1 renders. Take a screenshot and save to /assets/page1_built.png if the user can.

## Self-verification (run before declaring the deliverable complete)

1. PBIR JSON parse. For every JSON file edited or created under /pbip/Tonnelle_Risk.Report/definition/pages/ for Page 1, run JSON parse. Must succeed.
2. Measure name resolution. Grep every measure reference in Page 1 PBIR. Cross-check each against the measure list in /docs/05_semantic_model.md and /docs/06_time_intel.md. Any unresolved name is a bug.
3. Visual count and types. Confirm the locked visual list from /docs/03_design_locked.md Page 1 section matches the PBIR (visual count and visual types).
4. Cross-filter sanity. For one slicer interaction (e.g., filtering category), hand-trace whether the trend chart preserves its monthly grain. Document one example.
5. Theme-driven colors. Grep Page 1 PBIR JSON for inline hex codes. None should appear; all colors should derive from the loaded theme.json. Any hardcoded hex is a deviation; document why.
6. Field-well configuration. Confirm any "Show items with no data" settings called for by locked spec; if PBIR does not represent these fully, list as user-side click required.

Iterate or document gaps.

End chat with: list of visuals shipped, any open follow-up the user needs to verify in Desktop. Stop. Do not begin Phase 10.
```

---

## Phase 10 — Page 2: Risk Register Detail

**Skills loaded:** `pbi-report-design`.

**Prompt:**

```
Load pbi-report-design.

Read:

- /docs/03_design_locked.md (Page 2 layout)
- /docs/05_semantic_model.md, /docs/06_time_intel.md, /docs/07_svg_pill.md (measures, including the SVG pill)
- /docs/08_theme.md
- /docs/09_page1.md (for style continuity)
- /pbip/Tonnelle_Risk.Report/definition/pages/
- /assets/risk_dashboard_mockup.png

This session: build Page 2 only. Edit PBIR files.

Page 2 visuals per /docs/03_design_locked.md:
1. Header bar (same style as Page 1, page indicator 2 of 3)
2. Top Risks table sorted by risk_score_overall desc, top N per locked spec. Columns per locked spec. The risk_level column binds to the SVG pill measure (Phase 7), and its Data category must be set to Image URL.
3. Risk Count by Coordinator horizontal bar
4. Recent Risk Updates feed, sorted by update_date desc, top N per locked spec
5. Slicers: risk_category, risk_coordinator (no project slicer; single contract)

Wire right-click drillthrough from the Top Risks table to the Page 3 Risk Detail page. The drillthrough filter field is risk_id (or whatever locked spec says). PBIR JSON for drillthrough config: verify on read; this may need a user-side click in Power BI Desktop's Visualizations pane to fully activate.

Phase 3 (Risk Detail page) does not exist yet; it is built in Phase 11. But the drillthrough source-side wiring must exist on Page 2 now so Phase 11 receives a working chain.

User-side step at end: open PBIP, select Top Risks table > right-click a row > Drill through, confirm Risk Detail destination appears (even if the page itself is blank until Phase 11).

Also user-side: select the risk_level column on Top Risks > Column tools > Data category > Image URL.

Output:
- Direct PBIR file edits.
- /docs/10_page2.md log.

## Self-verification (run before declaring the deliverable complete)

1. PBIR JSON parse for all Page 2 files. Must succeed.
2. Measure name resolution including the SVG pill measure from /docs/07_svg_pill.md.
3. Visual count and types match the locked Page 2 spec.
4. Drillthrough source wiring. The Top Risks table must declare a drillthrough action targeting Page 3 (Risk Detail). Locate in PBIR JSON. If PBIR does not fully represent drillthrough config, document the user-side click required as an explicit checklist item.
5. Slicer field bindings. Category and coordinator slicers bind to risk_category and risk_coordinator. No project slicer.
6. SVG pill column configuration. The risk_level column on Top Risks references the SVG pill measure. Document the user-side step to set Data category to Image URL if PBIR cannot represent it.
7. Sort and top-N. Top Risks sorted by risk_score_overall desc, top N per locked spec.
8. Theme-driven colors. Same check as Phase 9; no inline hex codes.

Iterate or document gaps.

End chat with: visuals shipped, drillthrough source-side wired, list of user-side clicks required. Stop. Do not begin Phase 11.
```

---

## Phase 11 — Page 3: Risk Detail drillthrough

**Skills loaded:** `pbi-report-design`.

**Prompt:**

```
Load pbi-report-design.

Read:

- /docs/03_design_locked.md (Page 3 layout)
- All prior 0X_*.md
- /pbip/Tonnelle_Risk.Report/definition/pages/
- /assets/risk_dashboard_mockup.png

This session: build Page 3 (Risk Detail, the drillthrough destination). Edit PBIR files.

Page 3 structure per /docs/03_design_locked.md:
1. Hidden page named "Risk Detail" (hidden from page tabs, reachable via drillthrough from Page 2).
2. Drillthrough filter field: risk_id (or risk_title per locked spec).
3. On the page:
   - Header showing selected risk_id, risk_title, category, level (use the SVG pill measure here too).
   - Full attribute block: probability, cost_impact, schedule_impact, scores (overall, cost, schedule), entity, coordinator, status, mitigation_status, next_review_date.
   - Proposed mitigation text section: the full mitigation_log column rendered as long-form readable text (the turnover notes mitigation text is too long for a table cell; use a multi-row card or a text-bound visual that wraps).
   - Updates history: a table or list visual filtered to the selected risk's update rows from Risk_Updates, sorted by update_date desc, columns: update_date, author, note.
   - Back button: Power BI auto-creates one on drillthrough pages; verify placement and that styling matches the theme.

Layout philosophy per /docs/03_design_locked.md section (c) Page 3 lock (single-column readable narrative vs. multi-column reference). Apply.

Verify the drillthrough chain end-to-end:
1. Page 2 right-click on a Top Risks row > Drill through > Risk Detail.
2. Page 3 receives the risk_id filter.
3. Every visual on Page 3 displays data for that one risk.
4. Back button returns to Page 2.

If PBIR alone cannot fully wire the drillthrough config (Power BI Desktop sometimes requires a UI click), document the user-side step clearly.

Output:
- PBIR file edits.
- /docs/11_page3.md log including a screenshot or written walkthrough of the chain working end-to-end.

## Self-verification (run before declaring the deliverable complete)

1. PBIR JSON parse for all Page 3 files. Must succeed.
2. Page hidden flag. The Risk Detail page must be hidden from the page tab strip. Verify in PBIR.
3. Drillthrough filter declaration. Page 3 must declare a drillthrough filter on risk_id (or whatever locked spec says). Verify in PBIR.
4. Visual data bindings. Every visual on Page 3 binds to Risk_Register or Risk_Updates with correct filtering. The Updates history visual must filter to the drilled-through risk_id.
5. Back button presence. Power BI auto-creates a Back button on drillthrough pages; confirm it exists in the PBIR.
6. End-to-end chain dry-run. Mentally simulate the chain for one real risk (e.g., TONN-CON.02). Document expected Page 3 contents: header text, attribute block values, mitigation text, and the count of Updates rows that should display (compute from source data).
7. Theme-driven colors. Same check as Phase 9; no inline hex codes.

Iterate or document gaps.

End chat with: drillthrough chain verified or pending verification, any user-side click required. Stop. Do not begin Phase 12.
```

---

## Phase 12 — Python append script (Risk_Updates auto-append)

**Skills loaded:** none (Power BI skills not needed here).

**Prompt:**

```
No Power BI skills required this session. Plain Python.

Read:

- /RISK_DASHBOARD_turnover.md (the FUTURE CAPABILITY section)
- /docs/01_audit.md (data quality findings)
- /source_data/Tonnelle_Risk_Register_260519.xlsx
- /source_data/Tonnelle_Risk_Updates_260519.xlsx

This session: produce the Python script the turnover deferred. Goal: detect changes in Risk_Register and append rows to Risk_Updates.

Constraints per turnover and design lock:
- Risk_Updates remains append-only flat: update_id, risk_id, update_date, update_year, author, note.
- risk_id format unchanged (TONN-CON.NN).
- The script reads Risk_Register, reads Risk_Updates, computes a diff, appends new rows.
- No side effects on the multi-tab Register workbook.

Design choices you must make explicit in your output:

1. Change detection signal. The Register's mitigation_log column holds prose-with-dates. The user adds a new dated note like "5/22 - new event." The script must:
   - Parse mitigation_log into dated entries (regex the same way the original split was done).
   - Compare against Risk_Updates rows for that risk_id.
   - Append any entry in mitigation_log not represented in Risk_Updates.
   Document the parse regex and the matching key (risk_id + update_date + first N chars of note, or hash).

2. State storage. The "what's already been processed" state is implicit: Risk_Updates IS the state. No sibling state file needed.

3. Date inference. Dated entries in mitigation_log use M/D format (year ambiguous). The script must infer year using:
   - Default: current calendar year.
   - If inferred date is more than 6 months in the future, use prior year instead.
   Document this rule with examples and a --year-override CLI flag for manual override.

4. Author inference. Default to risk_coordinator from Register. CLI flag --author to override.

5. Failure modes:
   - --dry-run: print the rows that would be appended without writing.
   - --backup: before writing, copy Risk_Updates to a timestamped backup file alongside.
   - On parse failure for a mitigation_log entry: log the entry, continue, do not crash.

Library constraints:
- Use openpyxl for Excel I/O. No pandas requirement unless openpyxl is genuinely insufficient.
- Python 3.10+ standard library otherwise.

Output:
- /scripts/append_updates.py
- /scripts/requirements.txt (openpyxl plus whatever else)
- /docs/12_script_design.md explaining the design and limits, with example dry-run output for two synthetic register changes.

User-side step: run python /scripts/append_updates.py --dry-run after editing the Register, review output, then run without --dry-run to commit.

Do not modify the PBIP project. Do not modify the source Excel files.

## Self-verification (run before declaring the deliverable complete)

1. Static compile. Run `python -m py_compile /scripts/append_updates.py`. Must succeed.
2. Linting. Run `python -m pyflakes /scripts/append_updates.py` (or `ruff check`) if available. Fix flagged issues.
3. Unit tests. Create /scripts/test_append_updates.py with pytest cases covering:
   - Parsing a synthetic mitigation_log with two dated entries.
   - Detecting a new entry not in Risk_Updates and producing one append row.
   - Year inference (current-year default; prior year for entries inferred more than 6 months in the future).
   - Dry-run mode produces no file write.
   - Backup mode produces a timestamped backup file.
   - Malformed entry does not crash; logs and continues.
   Run `pytest /scripts/test_append_updates.py`. All tests must pass.
4. Dry-run on real data. Run `python /scripts/append_updates.py --dry-run` against /source_data/ files. Capture output and include in /docs/12_script_design.md. Manually inspect for sanity.
5. Idempotency. Run dry-run twice in succession. Output must be identical.
6. CLI surface. Confirm --dry-run, --backup, --year-override, --author flags are wired and documented. Run `--help` and include output in deliverable.

End chat with summary of: parse regex used, example dry-run output, any limits the user must know about. Stop. Do not begin Phase 13.
```

---

## Phase 13 — README and portfolio writeup

**Skills loaded:** none.

**Prompt:**

```
Read every /docs/0X_*.md, /pbip/* (folder structure only), /scripts/*, /assets/theme.json, /assets/*.png.

This session: produce two final deliverables.

A) /README.md at project root. Audience: future-you opening this project in 6 months. Style: legal-memo concision, no em-dashes, no marketing language. Cover:
   1. What this project is (Tonnelle Avenue Bridge Relocation risk dashboard, single contract, internal Naik leadership audience).
   2. File map. PBIP folder structure. Where to find what.
   3. Refresh workflow. User edits Register or Updates in Excel > saves > opens PBIP in Power BI Desktop > Home > Refresh.
   4. Adding a new update. Two ways: manual edit of Updates file, or run /scripts/append_updates.py after editing mitigation_log in the Register.
   5. Known limits. PBIR preview format dependency, SVG pill measure quirks, Risk_Updates schema constraints driven by future-script compatibility.
   6. Future enhancements list (Monte Carlo / contingency tie-in per AACE RP series if the user pursues that; tornado diagram for top risks; etc.).

B) /docs/13_portfolio_writeup.md. Audience: a Senior Estimator or Project Controls hiring manager at a GC reviewing your portfolio. Style: legal-memo prose, no em-dashes, no marketing language ("leveraged," "robust," "best-in-class," "spearheaded" all banned). Plain factual professional description. Cover:
   1. Problem statement: single-contract risk visibility for project controls, internal leadership audience.
   2. Approach: Excel as data-entry layer; Power BI Desktop as display layer; PBIP with new PBIR format for source-controlled iteration; modular AI-assisted build with explicitly scoped skill packs governing each phase.
   3. Technical features that distinguish this work:
      - Native Power BI drillthrough page wired from a row-level table for full risk detail (rather than bookmark-modal or tooltip workarounds).
      - SVG pill measure rendering risk_level as a styled badge via DAX returning an SVG data URL with Image URL data category. Document this as the chosen tradeoff over conditional formatting.
      - Python append-script architecture for future automated reconciliation of mitigation_log to Risk_Updates, preserving append-only fact table integrity.
      - Schema decisions: which star elements were and were not implemented, with reasoning.
   4. Outcomes:
      - Final file count and line counts (DAX lines, M lines, Python lines, JSON lines).
      - Screenshots of the three pages.
      - Time elapsed and rough phase count.
   5. AI disclosure section: which parts were Claude-Code-assisted, which skills were applied at which phase, what was the user's design judgment vs. the model's. Honest about the contribution split.

Both deliverables should be in the same voice as RISK_DASHBOARD_turnover.md: short sentences, technical, no sales language.

Do not modify any PBIP files this session. Do not modify source data. Documentation only.

## Self-verification (run before declaring the deliverable complete)

1. File reference integrity. Grep both deliverables for every file path or filename mentioned. Run `ls` or `test -f` on each. Any reference to a nonexistent file is a bug; fix the doc.
2. Line counts. For every quantitative claim (DAX lines, M lines, Python lines, JSON lines, total file count), run `wc -l` on the actual file and verify the cited number. Round to nearest 10 if you prefer; do not state false specifics.
3. Screenshot presence. The portfolio writeup references screenshots; confirm each named PNG exists in /assets/.
4. Banned-term grep. Grep both docs for: leveraged, robust, best-in-class, spearheaded, synergy, seamlessly, cutting-edge, world-class. Any hit means the writeup violated its own style rule; rewrite the sentence.
5. Em-dash grep. Grep both docs for the em-dash character. Any hit is a violation of locked style; replace with comma, semicolon, or period.
6. Markdown sanity. Confirm both files parse as valid markdown (headings nested correctly, code fences balanced, no broken links).

If any check fails, fix and re-verify.

End chat with: file list of deliverables, line counts for each, and one closing observation about what worked and what did not in this build process. Stop. This is the final phase. Do not propose follow-up work.
```

---

## After Phase 13

Two follow-up paths the user may pursue, not in this prompt set:

1. **AACE RP alignment.** If this dashboard is to support AACE-governed deliverables, the qualitative P x I matrix needs to be paired with quantitative methods (expected value, Monte Carlo on contingency). The current build is qualitative screening only. The turnover flags this. A separate project would extend the model with a quantitative layer; do not retrofit it into this build.

2. **Multi-project rollup.** This build is single-contract by design. A portfolio version would require: a project dim with multiple rows, project slicers on every page, and a careful review of which measures need re-aggregation across projects. Not in scope here.
