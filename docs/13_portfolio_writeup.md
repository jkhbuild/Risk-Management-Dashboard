# 13. Portfolio writeup, Tonnelle Risk Dashboard

Prepared 2026-05-23. Audience: a Senior Estimator, Project Controls lead, or Risk Manager at a general contractor reviewing this portfolio piece. The dashboard itself opens from `/pbip/Tonnelle_Risk.pbip`. Operational instructions are in [README.md](../README.md). This writeup explains what was built, why, and how.

---

## 1. Problem statement

A single highway construction contract (Tonnelle Avenue Bridge Relocation, project ID `TONN-01`) needs risk visibility for project controls. Internal Naik leadership wants three things at a glance.

1. **Today's risk posture.** Count of risks at each level (High, Medium, Low). Average overall risk score. The 5x5 probability-impact heatmap of where current risks sit.
2. **Operational detail.** Top risks by score, with the owning coordinator and the time since last update. Filterable by category, coordinator, and risk level.
3. **Per-risk depth.** Drillthrough into one risk to see its full attributes, complete mitigation log as a newest-first list, and full dated update history.

The existing process was an Excel-based risk register maintained by the risk manager (RM) and emailed periodically to leadership as a screenshot. The dashboard replaces the screenshot with a refreshable Power BI report that reads the same Excel directly. The data-entry layer is unchanged; humans never edit Power BI.

Out of scope, considered and deferred: multi-project comparison, cost-loaded schedule integration, Monte Carlo contingency simulation, web-published service render. Each is listed as a future enhancement in [README.md](../README.md).

## 2. Approach

### Data layer, Excel as source of truth

Two workbooks live in [/source_data/](../source_data/).

- [Tonnelle_Risk_Register_MASTER.xlsx](../source_data/Tonnelle_Risk_Register_MASTER.xlsx), sheet `Risk_Register`: 37 risks, 19 columns. The three score columns are Excel formulas (`risk_score_overall = probability_score * MAX(cost_impact_score, schedule_impact_score)`), so the math is visible and auditable in Excel without opening Power BI.
- [Tonnelle_Risk_Updates_MASTER.xlsx](../source_data/Tonnelle_Risk_Updates_MASTER.xlsx), sheet `Risk_Updates`: 127 dated update events, append-only flat table with columns `update_id, risk_id, update_date, update_year, author, note`.

Excel owns validation (dropdown lists for categories and entities, formula scores), so the dashboard does not need to enforce those rules. The dashboard renders what Excel says.

### Display layer, Power BI Desktop with PBIP and PBIR

The project uses Power BI Project format (`.pbip`), Microsoft's plain-text unpacked save format. The semantic model serializes as TMDL (Tabular Model Definition Language) and the report serializes as PBIR JSON. Both are diff-friendly and source-controllable.

Practical effect: each visual is a per-file JSON; each measure is a TMDL stanza. A bad change to one visual is a one-file revert, not a full-binary rollback. This is the same property a development team would get from a code repository, applied to a BI artifact.

### Build process, modular AI-assisted phases

The build was structured as 13 sequential phases per [assets/claude_code_prompts.md](../assets/claude_code_prompts.md): data audit, schema challenge, design lock, Power Query, semantic model with Counts/Scores measures, time-intelligence measures, SVG pill measure, theme JSON, three layout phases (one page each), a Python operational script, and this writeup.

Each phase has:

- A defined input set (prior phase docs, the turnover spec, source data).
- A defined deliverable (a locked phase doc plus the corresponding TMDL, PBIR, or Python artifact).
- A scoped skill assignment. Two competing Power BI design skill packs are available: `pbi-report-design` (data-goblin, strict) and `power-bi-report-design-consultation` (awesome-copilot, exploratory). They conflict and were never loaded together. Phases that wanted to explore alternatives used the consultation skill; phases that needed to lock decisions used the data-goblin one.

Once a phase doc landed in [docs/](../docs/), it was treated as locked. Mechanical updates (filenames, counts, dates) get a brief changelog note but the design analysis stays. This prevented later phases from quietly re-litigating earlier decisions.

Six rule violations were accepted as deliberate trade-offs and documented in [docs/03_design_locked.md](03_design_locked.md) §f, with a seventh added in [docs/11_page3.md](11_page3.md) §g-3. Each violation lists the rule, the violation, the justification, and the mitigation. Visible trade-offs beat hidden ones.

## 3. Technical features

### a. Native drillthrough page for per-risk detail

Power BI offers three common patterns for "show me this one risk in detail":

1. **Tooltip page**, triggered on hover. Quick but cluttered, no interaction.
2. **Bookmark plus button**, opening a hand-built overlay. Flexible but brittle to maintain.
3. **Native drillthrough page**, right-click on a row, navigates to a hidden destination page with a filter applied. Built-in Power BI feature with a working back button.

This project uses option 3. The destination page [RiskDetail/page.json](../pbip/Tonnelle_Risk.Report/definition/pages/RiskDetail/page.json) is hidden from the page tab strip (`visibility: HiddenInViewMode`) and registered as a drillthrough destination on the `risk_id` column. Right-clicking any visual that contains `risk_id` (currently the Top Risks table on Page 2) surfaces a "Drill through, Risk Detail" submenu. Clicking navigates to Page 3 with `risk_id = <selected row>` applied as a page-level filter.

Three pieces of metadata in `RiskDetail/page.json` are required, and all three were necessary:

- `type: "Drillthrough"` at the page root.
- `pageBinding.parameters[].boundFilter` binding the drillthrough parameter to the filter by name.
- A page-level `filterConfig.filters[]` Categorical filter on `Risk_Register[risk_id]` with `howCreated: "Drillthrough"`.

Authoring only the filter (without the `type` and `pageBinding`) registered no destination; the right-click action did not appear. The `pbir-cli` command `pbir pages drillthrough --table Risk_Register --field risk_id` writes all three pieces in one call.

The destination page has its own 7-visual single-column narrative layout: BackButton, RiskTitle, MetaStrip (6 fields plus the SVG pill), Mitigation label and paragraph, Updates History label and table. The mitigation paragraph is fed by a DAX measure that pulls from `Risk_Updates` (the event log) rather than the static `Risk_Register[mitigation_log]` text column:

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

The active M:1 relationship from `Risk_Updates` to `Risk_Register` propagates the drillthrough filter naturally; the measure body needs no `CALCULATE` or `FILTER`. The result is a newest-first multi-line list rather than a concatenated paragraph blob.

### b. SVG pill measure for risk_level rendering

The Page 2 Top Risks table and the Page 3 MetaStrip both display each risk's level (Low, Medium, High) as a colored capsule rather than a plain text cell or a conditionally-filled rectangle.

The pill is rendered by a DAX measure that returns a `data:image/svg+xml;utf8,<svg ...>...</svg>` data URL. The measure carries `dataCategory: ImageUrl` so Power BI renders the cell as an image rather than as a text URL. Full DAX in [docs/07_svg_pill.md](07_svg_pill.md) §b; the SVG geometry is 60x20 with a rounded `<rect>` (rx=9, fully-capsule shape) and a centered `<text>` element. Colors follow the risk encoding convention (`#488f31` green, `#e8b450` amber, `#de425b` red); text color contrasts per band (white on green and red, dark on amber for accessibility on the yellow background).

**Why SVG-in-DAX instead of conditional formatting:**

Power BI's native conditional formatting fills the rectangular cell. The visual identity wanted a capsule shape, which native CF cannot produce. The accepted trade-off, documented in [docs/03_design_locked.md](03_design_locked.md) §f-1:

- The cell renders as an image. Screen readers see "image", not "High".
- Native sort, filter, and slicer operate on the raw `risk_level` text column, which stays unhidden in the model. The pill measure replaces only the display column in the two tables that show it.
- A measure that returns rendered markup mixes presentation with logic. Future palette edits require editing both the theme JSON and the measure's `SWITCH` branches in lockstep.

Mitigations applied: the text column stays live for assistive tech, the palette stays consolidated in the theme + measure pair, the fallback encoding (`base64` body) is documented if a future Power BI Desktop build rejects the `;utf8,` prefix.

One additional surprise emerged during Phase 11: `multiRowCard` does NOT honor a measure's `dataCategory: ImageUrl`. The Page 3 MetaStrip was originally specified as a `multiRowCard` but rendered the SVG as raw URL text. It was rewritten as a `tableEx` with `objects.grid.imageHeight = 44D` (same pattern as the Page 2 Top Risks Level column). Same data, different visual type, pill renders correctly.

### c. Python append-script architecture

[scripts/append_updates.py](../scripts/append_updates.py) (447 lines) reconciles new dated entries in `Risk_Register.mitigation_log` against existing rows in `Risk_Updates`. Workflow:

1. Risk manager emails a dated copy of the Register (`Tonnelle_Risk_Register_<YYMMDD>.xlsx`).
2. Owner archives the dated file to [archive/](../archive/), overwrites [Tonnelle_Risk_Register_MASTER.xlsx](../source_data/Tonnelle_Risk_Register_MASTER.xlsx) with the same content, runs the script with `--dry-run`.
3. Script proposes append rows and flags any row dated more than 45 days from today for review.
4. Owner re-runs without `--dry-run`. The script auto-archives the previous Updates MASTER (dated by the most recent `update_date` in the pre-write file) and writes the new MASTER.
5. Owner refreshes Power BI Desktop.

Key design choices:

- **Append-only preservation.** `Risk_Updates` remains the flat table the Phase 1 schema locked. The script appends new rows; it never rewrites existing rows or modifies the Register.
- **Exact-date fingerprint dedupe.** The key is `(risk_id, ISO date, normalize(note)[:120])`. Same risk plus same full date plus same first-120-char normalized note prefix is the same event. Distinct text on the same date appends as separate rows. Distinct text on the same M/D in different years appends correctly.
- **Bootstrap calibration for cold start.** Phase 2's separate regeneration script anchored historical years via calibration against an earlier Updates file. This append script uses a simpler "today's year plus 6-month roll-back" forward inference. A literal exact-date dedupe would have re-proposed every historical entry on the first run. The fix: before declaring an entry new, also check the fingerprint at every historical year known for that risk's (M, D). The cold-start dry-run produces zero false positives against the live MASTER (verified 2026-05-23).
- **Discrepancy flag.** Any proposed row dated more than 45 days from today, in either direction, gets a `[FLAG]` marker plus a `DISCREPANCY:` summary block. The script still writes; the flag is informational. Catches RM-side date typos and forgotten backdated entries.
- **Auto-archive with semantic naming.** Pre-write archive filename is `Tonnelle_Risk_Updates_<YYMMDD>.xlsx` where `YYMMDD` is the most recent `update_date` in the file being archived, not the wall-clock run time. The filename describes what the file contains. A second run on the same day appends `_HHMMSS` for disambiguation.

The script ships with [32 pytest cases](../scripts/test_append_updates.py) covering parse, year inference, dedupe, calibration, archive, dry-run, and discrepancy flagging. Smoke-tested 2026-05-23 against a live entry on `TONN-CON.02`; the test row was preserved in the MASTER as evidence of human verification.

### d. Schema decisions, what is and is NOT in the model

A central choice every Power BI model makes is how far to decompose data into a star schema. With 37 risks across 7 categories, 5 entities, and 6 coordinators, this project deliberately stays wide.

**What is NOT in the model:**

- **No `dim_Category`, `dim_Entity`, `dim_Coordinator`.** These three attributes live as text columns on `Risk_Register`. Decomposing into dim tables would add 3 tables, 3 relationships, 3 sort-key columns, and a layer of indirection without supporting any visual that the wide form cannot drive equally well. At 37 rows, cardinality compression buys nothing. The rationale is in [docs/02_schema_challenge.md](02_schema_challenge.md) §b1 and [docs/03_design_locked.md](03_design_locked.md) §f-3. The trigger to revisit: dataset growing past ~200 rows, or a second contract joining the workbook.

**What IS in the model:**

- **`dim_Date`** as a DAX-calculated calendar table seeded from the `Risk_Updates[update_date]` year range. Marked as the date table (`dataCategory: Time`, `isKey` on the Date column). Drives the Page 1 monthly continuous trend axis and unlocks future time-intelligence patterns (DATESBETWEEN, TOTALYTD, etc.) if scope grows. ~6 lines of DAX.
- **`dim_Probability` and `dim_Impact`** as DAX-calculated 1-to-5 tables, added in Phase 9 to drive the P-I matrix axes. The matrix needed to display all 25 (P, I) cells including the ones with no underlying `Risk_Register` row. Binding the axes to `Risk_Register` columns directly produced empty cells; binding to the dim tables (M:1 single-direction back to `Risk_Register`) plus a `Cell Total Risks = COUNTROWS(Risk_Register) + 0` Values measure produces a full 25-cell heatmap with conditional fill rendering correctly on empty cells.
- **`_Measures` helper table** holding all 15 measures organized into 4 display folders (Counts, Scores, TimeIntel, Display). Built with Power BI's canonical pattern (column `Value` with `isNameInferred: true`, partition source `{BLANK()}`). The first Enter-data variant got reverted by Power BI Desktop's TMDL writer on save.
- **One DAX calculated column** on `Risk_Register` (`max_impact_score = IF(cost >= schedule, cost, schedule)`), introduced in Phase 9 to drive an earlier matrix-axis approach. Now unused by visuals (the dim_Impact approach replaced it) but kept in the model for potential reuse.

Each decision is preserved in the corresponding phase doc, so a future reviewer can see what was considered and why it landed where it did.

## 4. Outcomes

### File counts and line counts

Authored content across the project (auto-generated static resources and tool output excluded):

| Category | Lines | Files | Detail |
|---|---|---|---|
| Python | 2,112 | 8 scripts | append_updates.py (447), test_append_updates.py (572), audit_inspect.py (422), regenerate_updates.py (294), verify_phase6_measures.py (133), inspect_updates_format.py (114), verify_phase5_measures.py (74), debug_year_anchor.py (56) |
| TMDL (DAX measures + Power Query M + model metadata) | 1,108 | 13 files | model.tmdl, 8 table files (`Risk_Register`, `Risk_Updates`, `Project`, `Lookups`, `dim_Date`, `dim_Probability`, `dim_Impact`, `_Measures`), relationships.tmdl, expressions.tmdl, database.tmdl, cultures/en-US.tmdl |
| PBIR JSON (report layer) | ~5,200 | 29 files | 23 visual.json across 3 pages, 3 page.json files, pages.json, report.json, version.json |
| Theme JSON | 432 | 1 file | [assets/theme.json](../assets/theme.json) (10-token palette, 4 text classes, 8 visualStyles entries) |
| Phase docs (this and prior) | 4,111 | 14 files | [docs/01_audit.md](01_audit.md) through this file, plus [docs/cf_authoring.md](cf_authoring.md) |

Total: ~13,000 lines of source artifact across 187 source files. The `.pbip` envelope file, the `StaticResources/` theme references, the `.platform` markers, and the `.pbi/` settings are auto-generated by Power BI Desktop and not counted here.

Semantic model footprint:
- 8 tables (4 source-bound via Power Query, 3 DAX-calculated, 1 helper).
- 3 active relationships (all M:1 single direction).
- 15 explicit DAX measures (4 Counts, 4 Scores, 2 TimeIntel, 5 Display).
- ~5 DAX-calculated columns and tables beyond the source-bound columns.

Report footprint:
- 3 pages (Executive Overview, Risk Register Detail, Risk Detail).
- 23 visuals (9 + 7 + 7).
- 1 custom theme.
- 1 hidden drillthrough destination page.

### Visual reference

![Design reference, MTA-adapted layout for Tonnelle](../assets/risk_dashboard_mockup.png)

The current built state is structurally complete: right data, right measures, drillthrough wired, all 15 measures present, all 23 visuals positioned per the locked layout in [docs/03_design_locked.md](03_design_locked.md) §d. The styling layer is unpolished; the mockup above is the design target. A visual-polish phase to close the gap is listed in [README.md](../README.md) under future enhancements.

### Time and phase count

Build executed 2026-05-22 (Phase 0 bootstrap) through 2026-05-23 (Phase 12 Python script and this writeup as Phase 13). Two calendar days of intensive single-operator work. 13 phases total per [assets/claude_code_prompts.md](../assets/claude_code_prompts.md).

## 5. AI disclosure

This project was built in collaboration with Claude Code (Anthropic's Claude model accessed via CLI). The user (Joshua Giron) directed scope, accepted or rejected design alternatives, smoke-tested every change in Power BI Desktop or by running scripts against source data, and made every final call on schema, palette, density, and trade-off acceptance. Honest split below.

### Per-phase skill assignment

| Phase | Topic | Skills loaded | Claude role |
|---|---|---|---|
| 0 | Bootstrap (folders, CLAUDE.md) | none | Formatted scaffolding the user described |
| 1 | Data audit | none | Wrote [scripts/audit_inspect.py](../scripts/audit_inspect.py); both reviewed output |
| 2 | Schema challenge (exploratory) | `power-bi-report-design-consultation` | Proposed alternatives for 6 questions; user picked 4 of 6 answers, deferred 2 |
| 3 | Design lock | `pbi-report-design` (data-goblin) | Drafted [docs/03_design_locked.md](03_design_locked.md) from user answers; user reviewed and locked |
| 4 | Power Query M | `powerbi-modeling` | Wrote the M; user pasted into Power Query Editor and verified row counts |
| 5 | Semantic model + Counts/Scores measures | `powerbi-modeling`, `power-bi-dax-optimization` | Wrote TMDL + DAX; user re-applied UI-only settings (Don't summarize, hide columns) |
| 6 | Time-intelligence measures | `power-bi-dax-optimization` | Wrote 2 measures; user-side verified against source via Python script |
| 7 | SVG pill measure | `power-bi-dax-optimization` | Wrote the DAX + reference SVGs; user confirmed Data category = Image URL in Desktop |
| 8 | Theme JSON | `pbi-report-design` | Wrote [assets/theme.json](../assets/theme.json) from the locked palette and typography |
| 9 | Page 1 Executive Overview (PBIR) | `pbi-report-design` | Wrote PBIR JSON; multiple iterations to stabilize the heatmap; user verified renders |
| 10 | Page 2 Risk Register Detail (PBIR) | `pbi-report-design` | Wrote PBIR; TopN filter took 4 schema iterations before landing; user verified |
| 11 | Page 3 Risk Detail drillthrough (PBIR) | `pbi-report-design` | Wrote PBIR; 4 post-deliverable revisions after user feedback |
| 12 | Python append script | none | Wrote [scripts/append_updates.py](../scripts/append_updates.py) (447 lines) plus 32 pytest cases; user ran smoke test |
| 13 | README + portfolio writeup | `crafting-effective-readmes` | Drafting this and [README.md](../README.md); user is reviewing |

### User judgment vs model output

**Decisions the user made (not the model):**

- The single-contract scope and the "Excel is the data-entry layer, Power BI is display-only" architecture.
- The locked-list extensions: accepting **Financial** as a 7th risk category and **Designer** as a 5th risk entity, rather than refiling those rows under existing values.
- Dropping `next_review_date` from the model (uniformly today across all rows; no signal) and replacing it with `[Days Since Last Update]`.
- Hiding the `status` column until backfilled, rather than surfacing a stale field.
- The 5-color divergent palette plus the `#e8b450` yellow midpoint.
- "Dense informational" density tier over "spacious executive".
- "Bare KPI cards (no targets)" trade-off for a descriptive register vs a goal-driven dashboard.
- The mitigation paragraph rewrite from a static-column SELECTEDVALUE to `CONCATENATEX(Risk_Updates, ..., DESC)`. The user opened the first render, saw an unreadable concatenated blob, and requested a newest-first multi-line list pulled from the event log.
- Every keep/discard call on Claude's proposed measure names, measure additions beyond the original lock, and rule-deviation acceptances.
- Smoke-testing the Python append script with an actual live entry on `TONN-CON.02`. The test row stays in MASTER as evidence of human verification.

**Decisions Claude proposed (user accepted with or without modification):**

- The 13-phase build sequence, derived from the turnover spec.
- The wide `Risk_Register` over decomposition into dim tables (Claude pitched both; user agreed on wide).
- The DAX `dim_Date` over a Power Query date table.
- The canonical `_Measures` table pattern after the first Enter-data variant got silently reverted by Power BI Desktop's TMDL writer.
- Every DAX measure body (Claude drafted; user reviewed each in Power BI Desktop).
- The bootstrap-calibration logic in the Python append script.
- The post-deliverable Page 3 revisions, including the visual-type swap from `multiRowCard` to `tableEx` after the user's screenshot showed the SVG rendering as raw text.

**Iteration-heavy areas (where Claude got it wrong before getting it right):**

- The Page 1 P-I matrix conditional formatting. Three iterations before landing on the consolidated `objects.values[1]` CF entry, `Cell PI Score` basis, the `Cell Total Risks = COUNTROWS + 0` Values measure trick, and the dim-table axes that together get the full 25-cell heatmap rendering (including the 2 empty cells with no underlying risks).
- The Page 2 TopN filter on Recent Risk Updates. Four schema iterations: `VisualTopN`-with-fields rejected by Desktop's loader, `ItemCount`-only silently no-op, sibling `OrderBy` rejected, canonical subquery shape with an `update_id` tie-breaker finally accepted.
- The Page 3 drillthrough destination registration. Hand-authoring just the filter (without `type` and `pageBinding`) was silently insufficient; the page did not register as a destination and the right-click action never surfaced. Resolved via `pbir pages drillthrough --table Risk_Register --field risk_id` which writes the three required pieces correctly.
- The Page 3 BackButton chrome stripped by Power BI Desktop on save because the `visualLink` block was placed under `objects` instead of `visualContainerObjects`. Resolved via `pbir set` (the CLI knows the correct scope). Generalized lesson saved to project memory.
- The first Page 3 MetaStrip rendered with a "Total" label and missing data row, because the theme.json `tableEx.total[0].totals: false` block does not override per-visual defaults. Resolved with an explicit `objects.total[0].properties.totals = false` per visual.

These were Claude-side errors. Each was caught by the user during render verification and corrected through additional iterations. Each is preserved as an accepted iteration in the corresponding phase doc rather than airbrushed out, because the iteration log is itself useful information for a future maintainer.

The user's core contribution was judgment: what to accept, what to reject, what to verify, when to stop iterating. Claude's contribution was implementation throughput at low marginal cost per attempt. The combination compressed what would otherwise be a multi-week build into roughly two calendar days of focused work.

---

End of portfolio writeup.
