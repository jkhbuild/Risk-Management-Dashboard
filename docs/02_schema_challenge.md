# 02. Schema challenge and design exploration

Phase 2 exploratory pass, prepared 2026-05-22. Skill loaded: `power-bi-report-design-consultation`. **Nothing in this document is locked.** Phase 3 will fix decisions under the stringent design skill.

Inputs:
- Phase 1 audit (`docs/01_audit.md`).
- Turnover spec (`assets/RISK_DASHBOARD_turnover.md`).
- User answers to four of the six §e Phase 1 questions, captured this turn (locked-list extensions, status treatment, Risk_Updates regeneration, trend-chart interpretation). The remaining two (`next_review_date` treatment, three text drifts) are surfaced as open items in §b5 and §d8 below; the drift question is largely absorbed by the regeneration choice.

---

## a) Current implied schema

```
                    +------------------+
                    |     Project      |   Dim, 1 row
                    |  project_id PK   |   project_id = TONN-01
                    |  budget, NTP,    |
                    |  duration, ...   |
                    +--------+---------+
                             | 1
                             | M
                    +--------+---------+        +--------------------+
                    |  Risk_Register   |  no    |      Lookups       |
                    |  (Fact-like)     |  rel   |  Enum/validation,  |
                    |  risk_id PK      | ...... |  rebuilt in Power  |
                    |  project_id FK   |        |  BI per turnover.  |
                    |  19 cols,        |        |  category_list (7) |
                    |  37 rows         |        |  entity_list (5)   |
                    +--------+---------+        |  status_list (4)   |
                             | 1                |  prob/cost/sched   |
                             | M                |  rating defs       |
                    +--------+---------+        |  level_bands       |
                    |  Risk_Updates    |        +--------------------+
                    |  (Fact, events)  |
                    |  update_id PK    |
                    |  risk_id FK      |
                    |  update_date     |
                    |  update_year     |
                    |  author, note    |
                    |  ~92 rows now;   |
                    |  ~125-130 after  |
                    |  Phase 2 rebuild |
                    +------------------+
```

Relationships:
- `Risk_Updates[risk_id]` to `Risk_Register[risk_id]`, M:1. Default filter direction Register to Updates; reverse needed when a measure on Updates must be filtered by an attribute of Register (e.g., "updates this month for High-only risks"). Set cross-filter to Both at this fact/dim boundary per turnover gotcha, or use bidirectional CROSSFILTER inside the measure on a case-by-case basis (preferred over Both for predictability).
- `Risk_Register[project_id]` to `Project[project_id]`, M:1. Trivial with one project but retained per turnover (and useful if a second contract is ever added).

Lookups is not a key-joined dim. Categories/entities/statuses are stored as text values on Risk_Register that happen to match the Lookups enumerations. No referential integrity is enforced by Power BI; consistency relies on Excel dropdown validation.

There is no date dimension currently. `update_date` lives natively on `Risk_Updates`. `next_review_date` lives natively on `Risk_Register` (uniformly today per Phase 1 audit; non-signal).

Score columns (`risk_score_cost`, `risk_score_schedule`, `risk_score_overall`, `risk_level`) are Excel formulas on `Risk_Register`, stored as values. They are columns, not measures.

---

## b) Challenge it

Six decisions, presented as for/against with a recommendation. No decision is locked here.

### b1. Wide fact-like Risk_Register vs star with dim_Category, dim_Entity, dim_Coordinator

**For decomposing into a star:**
- Clean DAX patterns (USERELATIONSHIP, CROSSFILTER, TREATAS) become trivial against named dims.
- The Page 2 coordinator-workload visual gets a real dim with its own sort order and any descriptive long-form labels.
- Categories and entities can carry sort-order columns separate from the fact.
- Extensibility: if a second contract is added later, the dims are already in place.
- Stronger "I designed a proper model" story for the portfolio framing.

**Against:**
- 37 rows. The dataset will not benefit from dim compression at this size.
- 6 categories, 5 entities, 6 coordinators. Cardinality is so low that grouping on the fact is indistinguishable in performance from grouping via a dim.
- Modeling overhead: 3 new tables, 3 new relationships, 3 new sort-key columns, all to support visuals that already work against the fact's text columns.
- The user's stated workflow keeps everything in Excel; Power-BI-only dim tables fragment the mental model.

**Recommendation: stay wide.** Categories, entities, and coordinators live as columns on `Risk_Register`. The Page 2 coordinator-workload visual is `COUNTROWS(Risk_Register)` grouped by `risk_coordinator`; no dim required. Revisit decomposition if the dataset grows past ~200 rows, or if a second contract is ever added. The portfolio-piece counterargument is worth flagging for Phase 3: if the user values the "look at the star schema" narrative more than the build effort it requires, the choice flips.

### b2. Lookups: rebuilt via "Enter data" in Power BI vs imported from Excel Lookups tab

Per turnover §"Platform decision": Excel Lookups serves dual duty (dropdown-validation source AND Power BI reference) and Power BI rebuilds the lists via "Enter data."

**For "Enter data" (turnover):**
- Decouples Power BI from Excel tab structure. If the user reformats the Lookups tab (renames, reorders), Power BI doesn't break.
- No Power Query step; smaller refresh footprint.

**For importing the Excel Lookups tab:**
- Single source of truth. If the user extends the lists in Excel (e.g., adds a category for a new risk class), Power BI picks it up on next refresh.
- Eliminates the drift risk that already manifested once: Phase 1 caught Lookups extended with Financial + Designer, neither in the turnover-locked spec. With the extensions now accepted (§c5), drift risk persists for future additions.
- Consistent with the "Excel is the data-entry layer" framing.

**Recommendation: defer to turnover (Enter data) for the Phase 3 build, but flag the drift risk explicitly.** The Power-BI-side Lookups must be hand-synced to the Excel Lookups tab whenever either changes. If this becomes painful, switch to importing the Lookups tab in a later revision; the schema does not depend on which choice.

### b3. Score columns: Excel formulas vs DAX measures vs Power Query calculated columns

Per turnover and locked CLAUDE.md: Excel formulas.

**For Excel formulas (locked):**
- Scores are visible and auditable in Excel without opening Power BI. Necessary for the "Excel is the data-entry layer" workflow.
- Phase 1 audit verified 0 mismatches across 37 rows; formulas are intact.
- `risk_score_overall` and `risk_level` participate in slicers, sort keys, and conditional formatting as columns. Measures cannot.
- Single source of truth for score logic (the Excel cell formula).

**For DAX measures:**
- Recomputed in visual context; useful only if scores need to react to a slicer (out of scope).
- Hides the score formula from anyone opening Excel.
- A measure cannot be sorted on or used directly as a categorical sort key; a calculated column would still be needed downstream.

**For Power Query calculated columns:**
- Adds nothing over Excel here. Same formula; storage moves from Excel cells to PQ. Power BI now owns score logic that the user cannot see in Excel.

**Recommendation: defend the locked choice.** The only scenario that would justify moving scores out of Excel is a "what-if" simulator on Power BI, which is not in scope.

### b4. Sort-order columns: Power Query conditional columns vs DAX

Per turnover gotcha: PQ conditional columns. DAX calculated columns for sort keys trigger circular-dependency errors.

**Recommendation: confirm PQ.** Implementation:
- `risk_level_sort` in PQ: Low=1, Medium=2, High=3. Set `risk_level` "Sort by Column" to `risk_level_sort`.
- Same pattern if any other categorical column needs custom ordering (e.g., a non-alphabetical order for `risk_category` per §c5, or `status` if it ever returns to the dashboard).

Note: the SVG pill measure (§b6) renders `risk_level` as an image. The native `risk_level` column must remain in the model for sort, filter, and slicer purposes; only its display in the Page 2 Top Risks table is replaced by the pill measure.

### b5. Date table strategy

Page 1's monthly trend chart needs a continuous date axis. Phase 1 §d was resolved this turn: the chart shows **count of updates per month, relabeled** (working title "Risk Activity Over Time"), not a score trend. Decision in §c4 below.

**For a DAX CALENDAR-based dim_Date:**
- `dim_Date = CALENDAR(MIN(Risk_Updates[update_date]), MAX(Risk_Updates[update_date]))` with Year / MonthNumber / MonthName / MonthSortKey columns.
- Standard time intelligence available (DATESBETWEEN, TOTALYTD, etc.) if scope grows.
- Continuous axis: months with zero updates still appear on the line chart, avoiding "Sep, Nov, Jan" gaps that would falsely imply an inactive November.

**For an M-generated date table:**
- Functionally equivalent to CALENDAR; more code; uses Power Query.
- Slightly easier to extend with fiscal-year columns, holiday flags, etc., if ever needed.

**For no separate dim (use Updates[update_date] natively):**
- Simplest. Works for the count-by-month chart if the X-axis uses Power BI's Date Hierarchy at the Month level.
- Month-gap risk on the chart, see above.
- `next_review_date` and `update_date` cannot share an axis if both ever become relevant.

**Recommendation: build a lean DAX dim_Date.** One CALENDAR table; single active relationship to `Risk_Updates[update_date]`; an inactive relationship to `Risk_Register[next_review_date]` set up but unused for now. Cost is ~6 lines of DAX. The continuous-axis benefit alone justifies it for what the turnover calls the "headline new capability."

### b6. Risk-level pill rendering (SVG measure with Image URL data category)

The turnover demands it; the user has accepted the tradeoff per CLAUDE.md locked decisions. The consultation lens flags markup-in-DAX as an anti-pattern, so the tension is worth surfacing.

**For SVG-pill (turnover):**
- Matches mockup visual fidelity. Rounded shape is not achievable via Power BI's native conditional background formatting, which only fills the rectangular cell.
- Widely-used pattern; documented technique.
- User has explicitly accepted the tradeoff in locked decisions; relitigating is wasted effort.

**Against (consultation lens):**
- A DAX measure that mixes presentation (SVG markup) and logic (level-to-color mapping) violates separation of concerns. Changing a pill color means editing a DAX string with embedded `<svg>` tags.
- Accessibility: SVG-rendered cells render as images, not text. Screen readers see "image", not "High". Real concern against the consultation skill's accessibility checklist.
- Search and sort: an image cell is not searchable; the native `risk_level` column must stay in the model (already planned in §b4).
- Power BI version sensitivity: some Desktop versions reject the `data:image/svg+xml;utf8,` prefix and require base64. CLAUDE.md notes this; it is a real failure mode.

**Recommendation: build the SVG pill as specified, with three guardrails:**
1. Keep the native `risk_level` column in the model and available to slicers and filters; only the Top Risks table's display column is swapped for the pill measure.
2. Set the cell tooltip on the Top Risks table to display the raw `risk_level` text, giving screen-reader and copy-paste users a text fallback.
3. Consider building the pill base64-encoded as the primary path (broader compatibility) and reserving `;utf8,` as a fallback. This inverts CLAUDE.md's stated fallback order; flag for explicit confirmation in Phase 3.

If the SVG approach fails entirely on the user's Power BI Desktop build, the documented fallback is conditional background color on the rectangular cell. Less visually faithful but functional.

---

## c) Open design questions for the user

### c1. Visual identity / brand palette

Audience: internal Naik leadership plus the user's portfolio site. The mockup uses an MTA-style navy header bar.

| Option | For | Against |
|---|---|---|
| **Naik brand palette** | Aligns with internal-Naik audience; portfolio shows Naik as the client. | Requires the Naik brand-guide spec; may collide with construction-risk semantic colors (red/amber/green) for High/Medium/Low. |
| **MTA-derived palette (navy with yellow accents)** | Tonnelle is MTA-adjacent; mockup already implies this; reads as "transit project" to a portfolio viewer. | Naik may not want public deliverables visually branded as MTA. Same color-collision risk against semantic R/A/G. |
| **Neutral professional (grays plus one brand accent, plus semantic R/A/G)** | Lowest brand-coordination cost. Semantic colors get the full visual budget. Portfolio-ready without permission. | Less distinctive. Doesn't signal "Naik" or "MTA project" to a viewer. |

Decision needed.

### c2. Density preference

| Option | Character | Fits when |
|---|---|---|
| **Dense informational** | Tight padding, smaller fonts, more visuals per page. Reads like a project-controls report. | Audience reads in detail; report opens on a desktop monitor. |
| **Spacious executive** | Larger fonts, generous whitespace, fewer focal points per page. Reads like a board-pack one-pager. | Audience scans; report viewed projected, printed, or in portfolio thumbnail. |

The mockup leans dense informational. The portfolio framing might pull toward spacious executive (stronger visual impression in a thumbnail). Decision needed.

### c3. Drillthrough page (Page 3) layout philosophy

Page 3 shows: selected risk's full fields, complete proposed mitigation text, and that risk's full Updates history.

| Layout | Description | Good for |
|---|---|---|
| **Single-column narrative** | Risk header at top, mitigation as paragraph, updates as a dated list below. Reads top to bottom like a memo. | Reading depth. Matches the user's legal-memo style preference. |
| **Two-column reference** | Left: fields (status, scores, dates, coordinator). Right: mitigation text and Updates list. | Quick lookup; reference use. |
| **Compact card grid** | One card per field; mitigation and updates in a wide card spanning the bottom. | Dashboard-ish feel; better for mobile (not in scope here). |

Single-column narrative is the closest match to the user's stated tone. Decision needed.

### c4. Risk Score Trend Over Time chart interpretation

**Resolved this turn.** User selected **count of updates per month, relabeled**. The chart will be retitled to reflect activity (working title "Risk Activity Over Time"; final wording locks in Phase 3). One line: COUNT of `Risk_Updates` rows by month, axis driven by `dim_Date` per §b5.

Notes for Phase 3:
- X-axis must include zero-update months to avoid implying activity gaps that don't exist (the dim_Date justification in §b5).
- Y-axis integer format ("12 updates", not "12.0").
- Consider a faint reference line at the dataset's monthly mean for context.

### c5. Locked-list extensions (Financial, Designer)

**Resolved this turn.** User selected **accept both**. The locked sets are extended:
- Categories (7): Construction, Field Condition, Design Change, Safety, Environmental, Political, **Financial**.
- Entities (5): GDC, CM, Contractor, Shared, **Designer**.

Implications:
- Power BI Lookups (Enter data per §b2) must include all 7 categories and all 5 entities.
- Page 1's "Risks by Category" stacked bar has 7 bars, not 6. Financial has 2 risks; the bar will be short but present. Decide ordering rule (see below).
- The turnover spec in `assets/` is now out of sync with the locked sets. Either annotate the spec with the extension, or accept that CLAUDE.md and this doc are now the authoritative spec going forward. Flag for Phase 3.

Open within this question: **stacked-bar category sort order.** Three plausible rules:
- By count (data-driven, descending). Easy to read "where are most risks." Order changes as data changes.
- Alphabetical. Stable but uninformative.
- Fixed conceptual order, e.g., physical first (Construction, Field Condition, Design Change), then governance (Safety, Environmental, Political, Financial). Tells a story; requires a sort-order column. Decide in Phase 3.

---

## d) Mockup deviations

The mockup was built for the prior 58 Devices 2-contract program. Apply these deviations for Tonnelle:

1. **Drop the project slicer.** Single contract; no comparison axis.
2. **Trend chart: one line, not two.** Per turnover and §c4.
3. **Header bar title and subtitle.** Suggested title: "Tonnelle Avenue Bridge Relocation: Risk Register". Subtitle candidates: "Project TONN-01 | data as of [refresh date]" or "Project TONN-01 | [contract value] | as of [refresh date]". Final wording in Phase 3.
4. **Category labels:** use the Tonnelle list (Construction, Field Condition, Design Change, Safety, Environmental, Political, Financial). The mockup's "Const: Others" etc. is from the prior project and does not apply.
5. **Entity labels:** GDC, CM, Contractor, Shared, Designer. The mockup's prior entities do not apply.
6. **Coordinator names:** the prior project's coordinator names are placeholders. Tonnelle uses the actual six coordinators per Phase 1 audit (Anton Benedict, Eric Kautz, Justin Hwang, Joshua Giron, Yaseen Arshev, Vin Pallypis).
7. **Status field.** Per §b decision (user answer this turn), hide `status` until backfilled. Top Risks table on Page 2 omits the status column. Any mockup slicer or chip showing status is dropped.
8. **next_review_date.** Mockup may show a "next review" callout or column. Per Phase 1 audit the column is uniformly today (no signal). Three options for Phase 3: hide the field; replace it with "days since last update" derived from `Risk_Updates`; or ask the user to populate real per-risk review dates in Excel. Flag.
9. **Risk_Updates regeneration.** Phase 2 builds Power Query against a regenerated Updates file (per the user's §c-Q3 answer this turn): rebuilt from current `mitigation_log`, with the 6 Updates-only closing events carried forward. The regeneration produces ~125-130 rows; the model and visuals should be built against that, not the current 92-row file.

---

These options remain open. Lock under stringent skill in Phase 3.
