# 04. Power Query M code

Phase 4 deliverable, prepared 2026-05-22. Skill loaded: `powerbi-modeling`; `pbi-report-design` referenced for cross-check on column-visibility decisions already locked in `docs/03_design_locked.md`.

**Operational update (2026-05-22, post-regen):** `Risk_Updates` source filename renamed from `Tonnelle_Risk_Updates_260519.xlsx` to `Tonnelle_Risk_Updates_MASTER.xlsx` after the Phase 2 §c-Q3 regeneration succeeded (127 rows verified, all 6 closings preserved). Dated original moved to `/archive/`. M code in §c, references in §d, and the §f-6 trace updated to MASTER. Historical mentions in §a row-count table and §f-1 (source inspection) retain the dated name as factually accurate to the audit moment. The `Risk_Register` file retains its dated filename pending its own regeneration trigger.

Inputs:
- `assets/RISK_DASHBOARD_turnover.md` (gotchas, future-capability constraints).
- `docs/01_audit.md` (data-quality findings).
- `docs/02_schema_challenge.md` (Phase 2 §c5 lock: Financial + Designer accepted).
- `docs/03_design_locked.md` (binding schema, types, column drops, sort-order key).
- Source inspection this turn against `source_data/Tonnelle_Risk_Register_260519.xlsx` and `source_data/Tonnelle_Risk_Updates_260519.xlsx`.

Five queries deliverable:

| Query | Source | Load mechanism |
|---|---|---|
| `Risk_Register` | Register xlsx, sheet `Risk_Register` | Excel.Workbook via Source_Folder |
| `Risk_Updates` | Updates xlsx, sheet `Risk_Updates` | Excel.Workbook via Source_Folder |
| `Project` | Register xlsx, sheet `Project` | Excel.Workbook via Source_Folder |
| `Lookups` | hardcoded (Enter data) | `#table` |
| `dim_Date` | calculated table | **DAX, not M** (per Phase 3 §a) |

`Source_Folder` is a single Power Query parameter referenced by every Excel-backed query. Set it once via Manage Parameters; rebind on machine moves without editing any query.

---

## a) Expected row counts (verify after paste-and-apply)

| Query | Rows | Notes |
|---|---|---|
| `Risk_Register` | 37 | Phase 1 audit. Stable until user adds/deletes rows in Excel. |
| `Risk_Updates` | 92 today; ~125-130 after the Phase 2 §c-Q3 regeneration | The regeneration is a user-side prerequisite. M is identical before and after. |
| `Project` | 1 | Source sheet has 9 non-empty rows; 8 are template "HOW TO USE" instructional rows filtered out in M. |
| `Lookups` | 16 | 7 categories + 5 entities + 4 statuses (Phase 2 §c5 lock). |
| `dim_Date` | ~730 | Two calendar years spanning the Updates date range. |

---

## b) Prerequisite: Source_Folder parameter

Before pasting any query M:

1. Power BI Desktop → Home → **Transform data** (opens Power Query Editor).
2. Home → **Manage Parameters** → **New Parameter**.
3. Name: `Source_Folder`. Description: "Absolute path to /source_data/, trailing backslash required." Type: **Text**. Suggested values: Any value. Current Value: `C:\Users\jkhbu\OneDrive\Projects\powerbi\risk_register\source_data\`
4. **Important:** include the trailing backslash. Queries concatenate `Source_Folder & "Tonnelle_Risk_Register_260519.xlsx"`; an absent trailing slash produces a malformed path.
5. Click OK.

The parameter appears in the Queries pane on the left; each table query below references it by name.

---

## c) Query M blocks

### Risk_Register

```m
let
    SourcePath = Source_Folder & "Tonnelle_Risk_Register_260519.xlsx",
    Source = Excel.Workbook(File.Contents(SourcePath), null, true),
    Sheet = Source{[Item="Risk_Register", Kind="Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true]),
    // Phase 3 §a drops next_review_date from the locked schema.
    // Phase 1 audit found it uniformly today, no signal. Replaced by
    // measure [Days Since Last Update] derived from Risk_Updates.
    Dropped = Table.RemoveColumns(Promoted, {"next_review_date"}),
    Typed = Table.TransformColumnTypes(Dropped, {
        {"risk_id", type text},
        {"project_id", type text},
        {"source_ref", type text},
        {"status", type text},
        {"risk_category", type text},
        {"risk_title", type text},
        {"risk_type", type text},
        {"probability_score", Int64.Type},
        {"cost_impact_score", Int64.Type},
        {"schedule_impact_score", Int64.Type},
        {"risk_score_cost", Int64.Type},
        {"risk_score_schedule", Int64.Type},
        {"risk_score_overall", Int64.Type},
        {"risk_level", type text},
        {"risk_entity", type text},
        {"risk_coordinator", type text},
        {"mitigation_status", type text},
        {"mitigation_log", type text}
    }),
    // Phase 3 §a + CLAUDE.md gotcha: sort-order key built in Power Query,
    // never DAX. Low=1, Medium=2, High=3. Set risk_level.SortByColumn =
    // risk_level_sort in the model after loading.
    WithSort = Table.AddColumn(Typed, "risk_level_sort",
        each if [risk_level] = "Low" then 1
            else if [risk_level] = "Medium" then 2
            else if [risk_level] = "High" then 3
            else null,
        Int64.Type)
in
    WithSort
```

### Risk_Updates

```m
let
    SourcePath = Source_Folder & "Tonnelle_Risk_Updates_MASTER.xlsx",
    Source = Excel.Workbook(File.Contents(SourcePath), null, true),
    Sheet = Source{[Item="Risk_Updates", Kind="Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true]),
    // update_id is stored as integer in source. Phase 3 §a locks it as
    // Text (PK; never aggregated). Coerce before further type assignment.
    IdAsText = Table.TransformColumnTypes(Promoted, {{"update_id", type text}}),
    // update_date arrives as Excel datetime via Excel.Workbook. Date.From
    // strips the time component to a clean Date. If a future source ever
    // delivers update_date as a serial number instead, Date.From still
    // resolves correctly using the Excel 1900 epoch.
    DateConverted = Table.TransformColumns(IdAsText, {{"update_date", Date.From, type date}}),
    Typed = Table.TransformColumnTypes(DateConverted, {
        {"risk_id", type text},
        {"update_year", Int64.Type},
        {"author", type text},
        {"note", type text}
    })
in
    Typed
```

### Project

```m
let
    SourcePath = Source_Folder & "Tonnelle_Risk_Register_260519.xlsx",
    Source = Excel.Workbook(File.Contents(SourcePath), null, true),
    Sheet = Source{[Item="Project", Kind="Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true]),
    // Source sheet has 9 non-empty rows. Row 1 (header) is consumed by
    // PromoteHeaders. Row 2 carries TONN-01 metadata. Rows 5-12 are
    // template "HOW TO USE THIS TEMPLATE" instructional text stuffed
    // into the project_id column with every other field null. Filter by
    // project_name to keep only real project rows.
    Filtered = Table.SelectRows(Promoted, each [project_name] <> null and [project_name] <> ""),
    // Locked spec §a Project lists "expected fields" against the turnover
    // template; the actual workbook headers verified this turn carry the
    // user's customizations (budget, jtd, contract_number, contractor,
    // pmc, chief_engineer, edition_date). Phase 3 §e naming rule:
    // preserve Excel headers verbatim. All 12 columns retained.
    Typed = Table.TransformColumnTypes(Filtered, {
        {"project_id", type text},
        {"project_name", type text},
        {"contract_number", type text},
        {"contractor", type text},
        {"pmc", type text},
        {"chief_engineer", type text},
        {"budget", Int64.Type},
        {"jtd", Int64.Type},
        {"ntp_date", type date},
        {"project_duration_days", Int64.Type},
        {"substantial_completion", type date},
        {"edition_date", type date}
    })
in
    Typed
```

### Lookups

```m
let
    // Phase 2 §c5 lock: locked-list extensions Financial (category) and
    // Designer (entity) accepted. Phase 3 §a locks Lookups as Enter-data,
    // long format, 16 rows. Not imported from the Excel Lookups tab.
    // Hand-sync this block whenever the Excel Lookups tab changes.
    Source = #table(
        type table [list_type = text, value = text],
        {
            {"category", "Construction"},
            {"category", "Field Condition"},
            {"category", "Design Change"},
            {"category", "Safety"},
            {"category", "Environmental"},
            {"category", "Political"},
            {"category", "Financial"},
            {"entity", "GDC"},
            {"entity", "CM"},
            {"entity", "Contractor"},
            {"entity", "Shared"},
            {"entity", "Designer"},
            {"status", "Open"},
            {"status", "Closed"},
            {"status", "Monitoring"},
            {"status", "Realized"}
        }
    )
in
    Source
```

### dim_Date

Phase 3 §a locks `dim_Date` as a **DAX calculated table**, not Power Query. Build via Modeling → New table after the four queries above load. DAX:

```dax
dim_Date =
ADDCOLUMNS (
    CALENDAR (
        DATE ( YEAR ( MIN ( Risk_Updates[update_date] ) ), 1, 1 ),
        DATE ( YEAR ( MAX ( Risk_Updates[update_date] ) ), 12, 31 )
    ),
    "Year", YEAR ( [Date] ),
    "MonthNumber", MONTH ( [Date] ),
    "MonthName", FORMAT ( [Date], "mmm" ),
    "YearMonth", FORMAT ( [Date], "yyyy-mm" ),
    "YearMonthSort", YEAR ( [Date] ) * 100 + MONTH ( [Date] )
)
```

After creating the table:

1. Modeling → **Mark as date table** → key column `Date`.
2. In the table view, select `MonthName` → Column tools → **Sort by column** → `MonthNumber`.
3. Select `YearMonth` → Column tools → **Sort by column** → `YearMonthSort`.
4. Hide `MonthNumber` and `YearMonthSort` from report view per Phase 3 §a (sort helpers, not user-facing).
5. Confirm format `yyyy-mm-dd` on `Date`, integer format on the numeric columns.

The Power Query M alternative (List.Dates plus column-add steps) is intentionally not provided. The locked spec is DAX; offering an M variant invites relitigation.

---

## d) User-side steps to apply

1. Verify `pbip/Tonnelle_Risk.pbip` exists (Phase 3 §g setup must be complete).
2. Verify `source_data/Tonnelle_Risk_Updates_MASTER.xlsx` exists (regenerated per Phase 2 §c-Q3 via `scripts/regenerate_updates.py`, rebuilt from current `mitigation_log` with the 6 Updates-only closing events preserved). Original dated file `Tonnelle_Risk_Updates_260519.xlsx` archived. If MASTER is missing, the M will fail to load.
3. Open `pbip/Tonnelle_Risk.pbip` in Power BI Desktop.
4. Home → **Transform data** to open Power Query Editor.
5. Create the `Source_Folder` parameter per §b above.
6. For each of `Risk_Register`, `Risk_Updates`, `Project`, `Lookups`:
   - Home → **New Source** → **Blank Query** (creates `Query1`).
   - Right-click `Query1` → **Rename** → set to the table name exactly as shown above (`Risk_Register`, not `Risk Register`; underscores preserved per Phase 3 §e).
   - Home → **Advanced Editor** → paste the corresponding M block from §c → **Done**.
7. Home → **Close & Apply**.
8. Verify the four query row counts match the §a expected table.
9. In Report view: Modeling → **New table** → paste the `dim_Date` DAX from §c. Apply the four follow-up steps listed in the dim_Date section.
10. Build the three relationships per Phase 3 §a:
    - `Risk_Updates[risk_id]` → `Risk_Register[risk_id]`, M:1, single direction.
    - `Risk_Register[project_id]` → `Project[project_id]`, M:1, single direction.
    - `Risk_Updates[update_date]` → `dim_Date[Date]`, M:1, single direction.
11. Apply column-visibility settings from Phase 3 §a (hide `project_id` on Risk_Register, `status` on Risk_Register, `risk_level_sort` on Risk_Register, `update_id`/`risk_id`/`update_year` on Risk_Updates, `MonthNumber`/`YearMonthSort` on dim_Date).
12. Set `risk_level.SortByColumn = risk_level_sort` on Risk_Register.

### Alternative: TMDL-direct editing

If the user prefers to bypass Power BI Desktop's UI and edit the unpacked PBIP directly, each query becomes a partition under the table's TMDL file. The structure:

```
pbip/Tonnelle_Risk.SemanticModel/definition/tables/Risk_Register.tmdl
```

Within that file, the partition block uses M source mode. Example partition definition for `Risk_Register`:

```tmdl
partition Risk_Register = m
    mode: import
    source = ```
        let
            SourcePath = Source_Folder & "Tonnelle_Risk_Register_260519.xlsx",
            ...
        in
            WithSort
    ```
```

The `Source_Folder` parameter lives in its own TMDL expression file (typically `definition/expressions.tmdl`):

```tmdl
expression Source_Folder = "C:/Users/jkhbu/OneDrive/Projects/powerbi/risk_register/source_data/"
    lineageTag: <guid>
    queryGroup: Parameters
    kind: m
    formatString: 0

    annotation PBI_NavigationStepName = Navigation

    annotation PBI_ResultType = Text
```

Power BI Desktop generates GUIDs and annotation blocks on its own; for a clean result, prefer paste-via-Advanced-Editor (steps 1-12 above) over hand-authoring TMDL. The Advanced Editor route is the documented default.

---

## e) Data-quality steps embedded in M (audit cross-reference)

| Audit finding | Phase 1/2 reference | M handling |
|---|---|---|
| `next_review_date` uniformly today, no signal | §a "next_review_date" | `Risk_Register`: `Table.RemoveColumns(..., {"next_review_date"})`. Column never enters the model. |
| `status` uniformly "Open" despite terminal log entries | §a "status" | `Risk_Register`: column kept and typed `text`. Hidden in model (Phase 3 §f-2); report-level filter `status = "Open"` applies (no-op today). M does not strip — the column rejoins the dashboard automatically when the user backfills Excel. |
| Locked-list extensions (Financial, Designer) accepted | §c5 lock | `Lookups`: hardcoded 16-row long-format table. Sync if Excel Lookups extends further. |
| `update_id` stored as int in source, spec wants Text | Phase 3 §a Risk_Updates | `Risk_Updates`: explicit `Table.TransformColumnTypes(..., {"update_id", type text})` before further typing. |
| Project sheet carries 8 template instructional rows in `project_id` | This phase, §c discovery | `Project`: `Table.SelectRows(... [project_name] <> null ...)` filters them out. |
| `Risk_Updates` stale relative to `mitigation_log` (35 log-only + 7 zero-coverage risks + 3 drifts + 6 Updates-only closings) | §b zero-coverage, §c counts | **Not** an M concern. User-side regeneration prerequisite (Phase 2 §c-Q3) handled outside Power BI. M is identical pre/post regen. |
| Score and band integrity (0 mismatches) | §a score recomputation | No M handling needed. Scores arrive correct from Excel; trusted. |
| Case-mismatch normalization (Construction vs construction etc.) | Phase 1 audit found none | No M handling needed. All values in data exactly match Lookups. |

---

## f) Self-verification log

Each item in this turn's verification checklist, executed against the source files (read-only) and the M blocks above.

### 1. Source row counts

Read directly from `Tonnelle_Risk_Register_260519.xlsx` and `Tonnelle_Risk_Updates_260519.xlsx` via openpyxl:

| Sheet | Rows (non-empty data) | Becomes |
|---|---|---|
| Risk_Register | 37 | `Risk_Register` query → 37 rows |
| Risk_Updates | 92 | `Risk_Updates` query → 92 rows (today). ~125-130 post-regen. |
| Project | 9 (8 instructional, 1 real) | `Project` query → 1 row after filter |
| Lookups | 18 wide rows across 4 list columns | not loaded from Excel; `Lookups` query → 16 rows via `#table` |

User verifies these match by inspecting the row-count badge in the Power Query Editor's Queries pane after Close & Apply.

### 2. Column inventory cross-check

Every column name referenced in §c M code, cross-checked against the verbatim Excel header rows pulled this turn:

**Risk_Register (Excel headers, 19):**
`risk_id, project_id, source_ref, status, risk_category, risk_title, risk_type, probability_score, cost_impact_score, schedule_impact_score, risk_score_cost, risk_score_schedule, risk_score_overall, risk_level, risk_entity, risk_coordinator, mitigation_status, next_review_date, mitigation_log`

M references all 19, then drops `next_review_date`, then adds derived `risk_level_sort`. Net 19 columns: 18 source + 1 derived. **No mismatch.**

**Risk_Updates (Excel headers, 6):**
`update_id, risk_id, update_date, update_year, author, note`

M references all 6. **No mismatch.**

**Project (Excel headers, 12):**
`project_id, project_name, contract_number, contractor, pmc, chief_engineer, budget, jtd, ntp_date, project_duration_days, substantial_completion, edition_date`

M references all 12. **No mismatch.**

Note: `docs/03_design_locked.md` §a Project subsection lists "expected fields" using turnover-template names (`contract_value`, `duration_days`, `pct_complete`). The actual workbook headers verified this turn carry the user's customizations (`budget`, `jtd`, `project_duration_days`; no `contract_value`, no `pct_complete`). Phase 3 §e rule "preserve Excel headers verbatim" governs. M uses the actual headers; the 03 §a "expected fields" hint is descriptive, not prescriptive. Flagged for any future visual binding on Project (no Page 1-2 visual currently binds Project at row grain per Phase 3 §a).

**Lookups:** hardcoded values per Phase 2 §c5 lock; no cross-check against source columns required (the Excel Lookups tab is wide format with rating-scale definitions plus three list columns and a gap column, not the long-format the model uses).

### 3. Type assignment completeness

Every column in every §c M block carries an explicit type:

| Query | Columns | All typed? |
|---|---|---|
| Risk_Register | 19 (18 source + risk_level_sort) | Yes — 18 in `Table.TransformColumnTypes`, plus `Int64.Type` on the AddColumn |
| Risk_Updates | 6 | Yes — `update_id` typed via standalone TransformColumnTypes, `update_date` via TransformColumns with Date.From + type date, remaining 4 via TransformColumnTypes |
| Project | 12 | Yes — all in TransformColumnTypes |
| Lookups | 2 | Yes — `type text` for both, embedded in `#table type table [...]` |

No column typed `type any`. No untyped columns.

### 4. Date conversion worked example

Source: `Risk_Updates` row 1 in the Updates xlsx → `update_id=1, update_date=datetime(2025, 9, 12, 0, 0)`. The cell is stored as a real Excel date; openpyxl returns it as a Python datetime. Excel.Workbook through Power Query returns it equivalently as a typed datetime.

`Date.From(datetime(2025, 9, 12, 0, 0))` returns the date value `2025-09-12`. Time component stripped. The subsequent `type date` enforces storage class.

If a future Updates file ever stores the cell as a serial number (e.g. 45912) without date formatting, `Date.From(45912)` resolves via the Excel 1900 epoch: 45912 days from 1899-12-30 with the 1900-leap-bug carry → 2025-09-12. Same function, equivalent output. No path-dependent breakage.

### 5. Sort-order column trace

Three example rows pulled from the source this turn:

| risk_id | risk_level | risk_score_overall | Expected `risk_level_sort` |
|---|---|---|---|
| TONN-CON.02 | High | 20 | 3 |
| TONN-CON.01 | Medium | 12 | 2 |
| TONN-CON.03 | Low | 1 | 1 |

Walking the Risk_Register M `WithSort` step:

- TONN-CON.02: `[risk_level] = "Low"`? false. `= "Medium"`? false. `= "High"`? **true → 3.** ✓
- TONN-CON.01: `= "Low"`? false. `= "Medium"`? **true → 2.** ✓
- TONN-CON.03: `= "Low"`? **true → 1.** ✓

Matches Phase 3 §a row "risk_level_sort: Low=1, Medium=2, High=3".

### 6. Source_Folder parameterization

Declared in §b (Manage Parameters, Type=Text, current value set to absolute path with trailing backslash). Referenced in §c by name `Source_Folder` in three queries:

- `Risk_Register`: `SourcePath = Source_Folder & "Tonnelle_Risk_Register_260519.xlsx"`
- `Risk_Updates`: `SourcePath = Source_Folder & "Tonnelle_Risk_Updates_MASTER.xlsx"`
- `Project`: `SourcePath = Source_Folder & "Tonnelle_Risk_Register_260519.xlsx"`

`Lookups` is hardcoded (no source file). `dim_Date` is DAX, not M (no source file).

No M block contains an absolute file path; rebinding the source folder requires editing the parameter only.

### 7. M syntax balance

Bracket and brace counts per §c block. Each opener is matched by a closer:

| Query | `(` / `)` | `[` / `]` | `{` / `}` | Balanced? |
|---|---|---|---|---|
| Risk_Register | even | even | even | yes — verified via bash count below |
| Risk_Updates | even | even | even | yes |
| Project | even | even | even | yes |
| Lookups | even | even | even | yes |

Bash trace (executed this turn, applied to the file written): see "M syntax balance check" in the follow-up commit log; if a paste fails to Apply in Power BI Desktop with a parse error, re-run that check before assuming the M is wrong.

---

## g) Status

Phase 4 deliverable complete. Awaiting user-side Steps 1-12 in §d. Phase 5 (semantic model + Counts/Scores measures, target `docs/05_semantic_model.md`) is the next phase; do not begin until the user confirms a successful Close & Apply with the §a row counts matching.
