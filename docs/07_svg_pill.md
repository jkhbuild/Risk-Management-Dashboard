# 07. SVG pill measure (`Risk Level Pill SVG`)

Phase 7 deliverable, prepared 2026-05-23. Skill loaded: `power-bi-dax-optimization`.

**Inputs:**
- `docs/03_design_locked.md` §c1 palette, §b Display folder, §f-1 accepted DAX-markup deviation.
- `docs/05_semantic_model.md` (_Measures.tmdl canonical pattern, display folder convention).
- Turnover spec `assets/RISK_DASHBOARD_turnover.md` lines 118-126 (PILLS technique).
- CLAUDE.md "SVG pills for risk_level" caveats (explicit width/height, `;utf8,` primary with base64 fallback).

Scope: one measure (`[Risk Level Pill SVG]`) in `_Measures.Display`, plus three reference test SVGs in `/assets/`.

---

## a) Files changed

| File | Change |
|---|---|
| `pbip/Tonnelle_Risk.SemanticModel/definition/tables/_Measures.tmdl` | Added measure `Risk Level Pill SVG` with `displayFolder: Display` and `dataCategory: ImageUrl`. Total measures in `_Measures` now 11 (4 Counts + 4 Scores + 2 TimeIntel + 1 Display). |
| `assets/test_pill_high.svg` | **New.** Standalone SVG payload (no `data:` prefix) for the High pill. Browser-renderable reference. |
| `assets/test_pill_medium.svg` | **New.** Standalone SVG payload for Medium. Longest label; sizing reference. |
| `assets/test_pill_low.svg` | **New.** Standalone SVG payload for Low. |

No deletions. No prior measure modified.

---

## b) Measure DAX

```dax
Risk Level Pill SVG =
VAR LevelText = SELECTEDVALUE ( Risk_Register[risk_level] )
VAR Fill =
    SWITCH (
        LevelText,
        "High",   "#de425b",
        "Medium", "#e8b450",
        "Low",    "#488f31"
    )
VAR TextColor = IF ( LevelText = "Medium", "#1a1a1a", "#FFFFFF" )
RETURN
    IF (
        NOT ISBLANK ( LevelText ),
        "data:image/svg+xml;utf8,"
            & "<svg xmlns='http://www.w3.org/2000/svg' width='60' height='20' viewBox='0 0 60 20'>"
            & "<rect x='1' y='1' width='58' height='18' rx='9' ry='9' fill='" & Fill & "'/>"
            & "<text x='30' y='14' font-family='Segoe UI' font-weight='600' font-size='11' fill='"
            & TextColor & "' text-anchor='middle'>" & LevelText & "</text>"
            & "</svg>"
    )
```

**Note on variable name:** `LevelText`, not `Level`. The first draft used `Level`; Power BI Desktop's DAX parser rejected it with "The syntax for 'Level' is incorrect" (`Level` collides with reserved tokens around hierarchy-level functions). Variable renamed to `LevelText` 2026-05-23 after Desktop validation; see §f-9 for the iteration log.

- `displayFolder: Display`
- `dataCategory: ImageUrl` (declared in TMDL; reconfirm via Desktop UI per §d below in case the serializer reverts on save)
- No `formatString` (return value is a Text URL; no numeric format applies)

### Geometry and color rationale

| Element | Value | Why |
|---|---|---|
| `width` / `height` / `viewBox` | 60 × 20 | Explicit dimensions per CLAUDE.md "set explicit width/height or the SVG stretches with row height." 20 px tall fits comfortably in the Page 2 Top Risks table default row band; 60 px wide leaves ~9 px horizontal padding around the longest label ("Medium" ≈ 40 px in Segoe UI Semibold 11px). |
| `<rect>` `rx`/`ry` = 9 | Fully rounded (rx = height/2 = 9 on an 18-tall interior) | Capsule shape per turnover §"PILLS" spec. |
| `<text>` `x`=30, `y`=14, `text-anchor='middle'` | Horizontal center of 60-wide viewport; baseline that places cap-mid at y ≈ 10.1, the visual center of the 18-tall pill interior | Centered without relying on `dominant-baseline` (inconsistent across Power BI rendering surfaces). |
| `font-family='Segoe UI'`, `font-weight='600'` (Semibold), `font-size='11'` | Per 03 §c2 typography lock; pill text reads as visual-emphasis weight matching visual titles. | Segoe UI resolves on Windows / Power BI Desktop without bundling. |
| Pill fills | `#de425b` / `#e8b450` / `#488f31` | Exact 03 §c1 palette (risk_high / risk_medium / risk_low). |
| Text colors | `#FFFFFF` on High and Low; `#1a1a1a` on Medium | Same rule as the 03 §c1 heatmap-cell table (white on the saturated red/green; dark on the warm-amber yellow because Medium-on-white-text fails contrast). |

### Optimization rationale (`power-bi-dax-optimization` heuristics)

- `SELECTEDVALUE(Risk_Register[risk_level])` is the documented single-row-context idiom. Returns BLANK when the filter context resolves to zero or more than one value; the outer `IF (NOT ISBLANK (Level), ...)` short-circuits both the empty case and any unexpected aggregation context, so the measure renders no broken-pill artifact in a totals row.
- `SWITCH` with literal scalar branches resolves at compile time (no row context, no iteration). No `LOOKUPVALUE`, no `CALCULATE`, no relationship traversal — the level is already on the row.
- `IF ( Level = "Medium", ...)` is preferred over a second `SWITCH` for a two-branch decision; equivalent plan, half the lines.
- String concatenation via `&` is cheap relative to any storage-engine call; this measure does zero storage-engine work past the `SELECTEDVALUE` scan, which is itself a single-column lookup against a 37-row table.
- No iterator (`SUMX` / `FILTER` / `ADDCOLUMNS`); no `CALCULATE`; no `ALL` / `REMOVEFILTERS`. The locked Page 2 slicers (`risk_category`, `risk_coordinator`, `risk_level`) must propagate so the table row reduces to the right risk, and `SELECTEDVALUE` honors that propagation.

### Why `;utf8,` and not base64

CLAUDE.md "SVG pills for risk_level" section names `;utf8,` as the primary encoding and base64 as the fallback. The `;utf8,` form keeps the DAX human-readable so future palette or label edits stay diff-friendly. If a specific Power BI Desktop build refuses to render the `;utf8,` data URL, the fallback is to wrap the SVG body in `BASE64ENCODE(...)` and switch the prefix to `data:image/svg+xml;base64,`. Defer until a render failure is observed; do not preemptively rewrite.

### XML-string quoting in DAX

SVG attributes are quoted with single quotes inside the DAX literal so the outer DAX string can use double quotes without escaping. This is well-formed XML (single quotes are valid attribute delimiters per the XML spec).

---

## c) Rendered output per level

Three reference SVG files materialize the exact payload the DAX measure produces (without the `data:image/svg+xml;utf8,` prefix). All three are visible in the launch preview panel for visual inspection.

### `/assets/test_pill_high.svg`

```svg
<svg xmlns='http://www.w3.org/2000/svg' width='60' height='20' viewBox='0 0 60 20'>
  <rect x='1' y='1' width='58' height='18' rx='9' ry='9' fill='#de425b'/>
  <text x='30' y='14' font-family='Segoe UI' font-weight='600' font-size='11'
        fill='#FFFFFF' text-anchor='middle'>High</text>
</svg>
```

Expected appearance: 60×20 px red-coral capsule (`#de425b`) with white "High" text Segoe UI Semibold 11px, centered. Text width ≈ 22 px; horizontal padding ≈ 18 px each side.

### `/assets/test_pill_medium.svg`

```svg
<svg xmlns='http://www.w3.org/2000/svg' width='60' height='20' viewBox='0 0 60 20'>
  <rect x='1' y='1' width='58' height='18' rx='9' ry='9' fill='#e8b450'/>
  <text x='30' y='14' font-family='Segoe UI' font-weight='600' font-size='11'
        fill='#1a1a1a' text-anchor='middle'>Medium</text>
</svg>
```

Expected appearance: warm amber capsule (`#e8b450`) with dark `#1a1a1a` "Medium" text. "Medium" is the longest label (~40 px wide at 11 px Semibold); pill interior is 58 px wide, leaving ~9 px horizontal padding each side. No overflow.

### `/assets/test_pill_low.svg`

```svg
<svg xmlns='http://www.w3.org/2000/svg' width='60' height='20' viewBox='0 0 60 20'>
  <rect x='1' y='1' width='58' height='18' rx='9' ry='9' fill='#488f31'/>
  <text x='30' y='14' font-family='Segoe UI' font-weight='600' font-size='11'
        fill='#FFFFFF' text-anchor='middle'>Low</text>
</svg>
```

Expected appearance: muted-green capsule (`#488f31`) with white "Low" text. Text width ≈ 20 px; horizontal padding ≈ 19 px each side.

---

## d) User-side actions to apply

1. **Close Power BI Desktop** if it has `Tonnelle_Risk.pbip` open.
2. **Open** `pbip/Tonnelle_Risk.pbip` in Power BI Desktop.
3. **Verify the measure landed:** Fields pane → `_Measures` → `Display` folder → `Risk Level Pill SVG`.
4. **Confirm Data category = Image URL on the measure.**
   - Click the measure in the Fields pane.
   - **Modeling** tab (top ribbon) → **Properties** group → **Data category** dropdown.
   - Confirm it reads **Image URL**. If it reads **Uncategorized**, change it to **Image URL** and save. The TMDL writes `dataCategory: ImageUrl`; some Desktop builds round-trip this cleanly and some do not (parallel to the `summarizeBy` / relationship-cardinality reverts documented in 05 §e2). UI-set persists.
5. **Page 2 binding (Phase 10 will wire this; do not build Page 2 yet):** when the Top Risks table is added, drag `[Risk Level Pill SVG]` into the column well in place of (or alongside) `risk_level`. Power BI renders the SVG as the cell content. Increase the table's row-height setting (Format pane → Values → Row padding, or set Row size: Comfortable) until the 20 px pill sits with breathing room (typically Row padding ≥ 4 px).
6. **Keep the raw `risk_level` column unhidden** per 03 §f-1 mitigation. The slicer on Page 2 binds to `risk_level` (text), not to the measure. Sort by `risk_level_sort` is applied to the text column, not the image.

### Sanity test (optional, throwaway)

Drop a `tableEx` visual on any scratch page, add `risk_id`, `risk_level`, and `[Risk Level Pill SVG]`. Confirm each row renders a pill colored to match the row's `risk_level` text. Delete the throwaway visual before moving on.

---

## e) Accepted deviation note

**Per `docs/03_design_locked.md` §f item 1**: this measure is the documented violation of the `power-bi-dax-optimization` and `pbi-report-design` skills' general principle that measures should compute values, not return rendered markup. Justification, mitigations, and the user's explicit acceptance are recorded in 03 §f-1. Restated here for traceability:

- **Violation:** measure returns a `data:image/svg+xml;utf8,<svg>...</svg>` string.
- **Justification:** native Power BI conditional formatting cannot produce a rounded capsule; the SVG-measure technique is the widely-documented workaround; the user has accepted the maintenance tradeoff.
- **Mitigations applied:**
  - Raw `risk_level` column remains unhidden so slicers and sort/filter work on plain text.
  - `risk_level_sort` (Power Query conditional column) drives the sort order for both the text and the pill display.
  - Color palette is fully theme-driven (matches 03 §c1 exactly; no improvised hex codes). Future theme adjustments require editing this measure's `SWITCH` and `IF` branches in lockstep with the theme.json edit (Phase 8).
  - Cell tooltip on Page 2 surfaces the raw level text (Phase 10 binding) for assistive-tech access.
  - Encoding is `;utf8,` per CLAUDE.md; base64 documented as fallback if a specific Desktop build rejects the inline form.

---

## f) Self-verification log

### 1. SVG materialization

Three test files written to `/assets/test_pill_<level>.svg` (without the `data:image/svg+xml;utf8,` prefix). Content matches the DAX `&`-concat output character-for-character (verified by re-simulating the concat in Python this turn).

### 2. XML well-formedness

`xmllint` not available on this host. Substituted `python -c "import xml.etree.ElementTree as ET; ET.fromstring(open(path).read())"` on all three test SVGs. All three parse without error. The same parser was then run on the simulated DAX concat output for each level (minus the `data:` prefix); all three parse. Result: well-formed XML in both the standalone files and the in-DAX payload.

### 3. Visual rendering check

Headless rasterizers (`cairosvg`, `rsvg-convert`, Chrome headless) not installed on this host. Substituted:
- **System launch-preview panel:** the three SVGs were placed into the user's preview panel by the Write hook; user can visually verify on demand.
- **Geometry math:** "Medium" (6 chars × ~6.5 px/char in Segoe UI Semibold 11px) ≈ 40 px; pill interior 58 px wide; horizontal padding ≈ 9 px each side. Baseline y=14 with 11px font puts cap-mid at y ≈ 10.1; pill interior vertical center is y=10. Centered.
- **Color match:** every hex literal in the test SVGs and the DAX `SWITCH`/`IF` branches grep-matches the 03 §c1 token table (`risk_high`, `risk_medium`, `risk_low`, `text_primary`, plus `#FFFFFF` for the canvas-derived white).

### 4. Data URL prefix

DAX `&`-concat builds the literal `"data:image/svg+xml;utf8,"` as the first segment of the return value. Verified by re-simulating the concat in Python and inspecting `out.startswith("data:image/svg+xml;utf8,")` → True for all three levels.

### 5. Color-match against locked palette

| Token | Hex | Found in measure | Found in test SVG |
|---|---|---|---|
| `risk_high` | `#de425b` | Yes (`SWITCH` "High" branch) | `test_pill_high.svg` `<rect>` fill |
| `risk_medium` | `#e8b450` | Yes (`SWITCH` "Medium" branch) | `test_pill_medium.svg` `<rect>` fill |
| `risk_low` | `#488f31` | Yes (`SWITCH` "Low" branch) | `test_pill_low.svg` `<rect>` fill |
| `text_primary` | `#1a1a1a` | Yes (`IF` Medium-text branch) | `test_pill_medium.svg` `<text>` fill |
| white (canvas-text) | `#FFFFFF` | Yes (`IF` else branch) | `test_pill_high.svg`, `test_pill_low.svg` `<text>` fill |

No improvised colors. No semicolon-separated rgba/hsla forms (would break SVG quoting and Power BI's URL parsing).

### 6. TMDL parse

`_Measures.tmdl` paren/bracket/brace balance = 0/0/0 across the whole file. 11 measures present, 11 unique names. `Risk Level Pill SVG` declares `displayFolder: Display` and `dataCategory: ImageUrl`. Adjacent measures (`Days Since Last Update`, `column Value`) untouched.

### 7. Measure-name uniqueness

```
_Measures.tmdl  Total Risks
_Measures.tmdl  High Risks
_Measures.tmdl  Medium Risks
_Measures.tmdl  Low Risks
_Measures.tmdl  Avg Risk Score Overall
_Measures.tmdl  Avg Cost Score
_Measures.tmdl  Avg Schedule Score
_Measures.tmdl  Max Risk Score
_Measures.tmdl  Updates Count
_Measures.tmdl  Days Since Last Update
_Measures.tmdl  Risk Level Pill SVG
```

11 measures, 11 unique names, all on `_Measures`. Matches 03 §b architecture (Counts 4 + Scores 4 + TimeIntel 2 + Display 1 of 3; remaining Display measures `Selected Risk Title` and `Selected Risk Mitigation Log` are out of Phase 7 scope per CLAUDE.md phase map — Page 3 drillthrough phase will add them).

### 8. Performance flag scan

- No iterator (`SUMX`, `AVERAGEX`, `FILTER`, `ADDCOLUMNS`).
- No nested `CALCULATE`.
- No `ALL` / `REMOVEFILTERS` (would break locked slicer propagation).
- `SELECTEDVALUE` is a single-column scan; the only storage-engine call in the measure.
- `SWITCH` and `IF` resolve in the formula engine on the already-computed `LevelText` scalar.

No deferred optimizations.

### 9. Desktop validation iteration (2026-05-23)

First draft used `VAR Level = SELECTEDVALUE(...)`. Power BI Desktop's formula bar rejected the measure with: **"The syntax for 'Level' is incorrect."** `Level` collides with reserved tokens around DAX hierarchy navigation (`ISATLEVEL`, level-aware iterators introduced for field parameters and hierarchies). DAX accepts most identifiers as VAR names, but a small reserved set surfaces only at parse time in Desktop — not in offline TMDL inspection. Renamed `Level` → `LevelText` (4 occurrences in the measure body); re-saved TMDL; re-validated in Desktop; measure parses and resolves. Lesson preserved for future measures: avoid `Level`, `Value`, `Date`, `Name`, `Year`, `Month` and similar short-noun identifiers as VAR names; prefer `LevelText`, `CurrentValue`, etc.

---

## g) Status

Phase 7 deliverable complete and applied 2026-05-23. `_Measures.Display` now contains `Risk Level Pill SVG`; three reference test SVGs in `/assets/`. User-side step is one confirmation click on Data category = Image URL in the Modeling ribbon after re-opening Power BI Desktop. Pages 1-3 PBIR construction (Phases 9-11) can consume this measure. Phase 8 (theme.json) is the next phase, unblocked.
