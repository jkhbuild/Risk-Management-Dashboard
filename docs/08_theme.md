# 08. Theme JSON

Phase 8 deliverable. Skill active: `pbi-report-design` (data-goblin). Inputs: locked palette and typography in `docs/03_design_locked.md` §c, layout intent from `assets/risk_dashboard_mockup.png` (KPI compactness, table density, header-bar feel), current report theme state (`pbip/Tonnelle_Risk.Report/definition/report.json` references `CY26SU05`, a Microsoft default base theme). Output: `assets/theme.json` plus this doc.

The deliverable is a Power BI custom theme JSON to be applied once via Desktop's View > Themes > Browse for themes. Report files are not modified this phase; theme application is a one-click user-side step. Per-visual formatting (positions, page header textbox content, conditional formatting on the P-I matrix, etc.) is Phase 9-11 territory.

---

## a) Palette mapping

All 10 tokens from 03 §c1 are reproduced verbatim. No improvisation. Every hex in `theme.json` is one of these 10 values; verified by grep.

| 03 §c1 token | Hex | Theme.json role |
|---|---|---|
| `risk_high` | `#de425b` | `dataColors[2]`, `bad`, `maximum` |
| `risk_medium` | `#e8b450` | `dataColors[1]`, `neutral`, `center` |
| `risk_low` | `#488f31` | `dataColors[0]`, `tableAccent`, `good`, `minimum` |
| `palette_tint_low` | `#8cbcac` | `dataColors[3]` |
| `palette_tint_high` | `#ec9c9d` | `dataColors[4]` |
| `palette_neutral` | `#f1f1f1` | `secondBackground`, `tableEx.columnHeaders.backColor` |
| `text_primary` | `#1a1a1a` | `foreground`, `dataColors[6]`, all primary text fills |
| `text_secondary` | `#5a5a5a` | `dataColors[5]`, axis labels, KPI category labels, legend |
| `canvas` | `#FFFFFF` | `background`, card/slicer fills |
| `border` | `#e0e0e0` | `dataColors[7]`, card/slicer/table outlines, axis line |

### dataColors ordering rationale

Eight entries (DG floor for chart-series fallback). Slot 0 = `risk_low` (`#488f31`) because the two single-series charts on the locked pages bind to this color: Page 1 #9 Risk Activity line, Page 2 #6 Risks by Coordinator bar. Slots 1-2 hold Medium and High in **risk-band gradient order** (low → medium → high) so the Page 1 #8 Risks by Category clustered bar picks up correct per-series colors from theme slot binding alone (the `risk_level` series sorts by `risk_level_sort`: Low=1, Medium=2, High=3, mapping to slots 0,1,2). Slots 3-4 are the tints. Slots 5-6 are neutral dark fillers. Slot 7 is `#e0e0e0` for the lightest fallback.

```
[0] #488f31  low / brand accent (single-series fill; clustered bar series=Low)
[1] #e8b450  medium (clustered bar series=Medium)
[2] #de425b  high (clustered bar series=High)
[3] #8cbcac  low tint (sage)
[4] #ec9c9d  high tint (pink)
[5] #5a5a5a  text_secondary / neutral dark series
[6] #1a1a1a  text_primary / very dark
[7] #e0e0e0  border / lightest gray
```

**2026-05-23 update:** the original slot 1=#de425b / slot 2=#e8b450 ordering (08 §a v1) intended visual-level CF on RisksByCategory to bind series colors. Phase 9 attempted CF via pbir CLI but hit two Power BI Desktop errors on open: `Missing_References` (when CF used `Left.Measure` wrapper for a Column field) and then `RepeatedIndicesProjectionsOrGroupBy` (when CF used `Left.Column` wrapper, conflicting with the same column being in the Series projection). The CF-rules approach pbir CLI generates is not compatible with column-bound series color binding. Theme slot order is the right mechanism. Slots 1-2 swapped so series sort (Low/Medium/High) maps cleanly to colors (green/yellow/red).

The P-I matrix (Page 1 #7) drives cell color by score band via conditional formatting at the visual level (rules use `#488f31` / `#e8b450` / `#de425b`), not from theme dataColors. **Phase 9 also deferred matrix CF to user-side Desktop UI** after hitting the same RepeatedIndices error; see `docs/09_page1.md` §e4.

### Semantic / divergent slots

`good`, `neutral`, `bad` map to low/medium/high per 03 §c1 ("colors that implicitly encode meaning ... unless using them for that encoding"). `minimum`/`center`/`maximum` mirror these so any divergent gradient (heatmap continuous fill, if Phase 9+ wants one) defaults to the locked endpoints.

---

## b) Typography

Per 03 §c2. textClasses define the four classes Power BI honors across visuals:

| textClass | Family | Size | Color | Mapped 03 §c2 role |
|---|---|---|---|---|
| `callout` | Segoe UI Semibold | 32 | `#1a1a1a` | KPI value |
| `title` | Segoe UI Semibold | 14 | `#1a1a1a` | Visual title |
| `header` | Segoe UI Semibold | 11 | `#1a1a1a` | Table/matrix column headers, slicer header |
| `label` | Segoe UI | 11 | `#1a1a1a` | KPI category label, table cell, slicer item |

Smaller per-visual overrides for 10pt (axis, legend, data labels) and 9pt (multiRowCard category labels on the Page 3 meta strip) are written into the relevant `visualStyles` blocks because textClasses do not span those sub-properties.

Report title (Semibold 22pt) and page subtitle (regular 11pt) live inside textbox rich-text inline formatting and are not driven by the theme; they will be set at Phase 9 in the Page 1/2 header textboxes. Theme cannot style textbox content from a global setting.

11pt body floor (vs DG's 12pt minimum) is the deviation documented in 03 §f-6.

---

## c) visualStyles coverage

Eight `visualStyles` entries: one wildcard plus seven visual-specific. Each maps to a visual type used on the locked pages.

| visualStyles key | Used on | Settings |
|---|---|---|
| `*` (wildcard) | Every visual | Title (Semibold 14pt, left-aligned, `#1a1a1a` on `#FFFFFF`), background off, border off, drop shadow off, lock-aspect off. Establishes the "transparent visual on white canvas" default. |
| `card` | Page 1 KPIs (5), Page 3 mitigation paragraph | Category label `#5a5a5a` 11pt, value `#1a1a1a` 32pt Semibold, `#FFFFFF` fill, `#e0e0e0` border, visual-title off (KPI label suffices). Mirrors mockup compact KPI block. |
| `multiRowCard` | Page 3 meta strip | Data label 16pt Semibold, category label 10pt `#5a5a5a`, "Bottom only" outline `#e0e0e0` so the six meta fields read as a single row with subtle dividers. |
| `tableEx` | Page 2 Top Risks, Page 2 Recent Updates, Page 3 Updates History | Horizontal gridlines `#e0e0e0` 1px, no vertical gridlines, headers Semibold 11pt on `#f1f1f1`, cells regular 11pt on `#FFFFFF`, no row banding (banding via `backColorSecondary = #FFFFFF`), totals off. "Subtract don't add" per DG. |
| `pivotTable` | Page 1 P-I matrix | Both gridlines off (heatmap cells carry their own conditional fill at Phase 9); headers Semibold 11pt centered, row headers Semibold right-aligned, subtotals and grand totals off. Cell text Semibold 11pt `#1a1a1a` (overridden to white inside the conditional formatting rule for High and Low cells at Phase 9). |
| `lineChart` | Page 1 Risk Activity | Continuous category axis (locked per 03 §d), gridlines off, axis line `#e0e0e0`, axis labels 10pt `#5a5a5a`, legend top-positioned 10pt, no axis titles, data labels off (single-series line reads from position). |
| `clusteredBarChart` | Page 1 Risks by Category, Page 2 Risks by Coordinator | Category axis labels 10pt `#1a1a1a` (left side of horizontal bar reads as the primary label), value axis hidden (data labels carry the magnitude), data labels on at "Outside end" 10pt, gridlines off. |
| `slicer` | Page 2 Category, Coordinator, Risk Level slicers | Vertical orientation, header Semibold 11pt with bottom-only `#e0e0e0` rule, items regular 11pt, search off, `#FFFFFF` fill, `#e0e0e0` border. Compact three-across slicer row per 03 §d. |

### Visual types not styled

- **textbox** (Page 1 #1, Page 2 #1, Page 3 #2/#4/#6): content is rich-text inline; the theme cannot style textbox text. Phase 9 sets the report title (Semibold 22pt) and subtitle (regular 11pt) directly in the textbox paragraph runs.
- **actionButton** (Page 3 #1 back button): single instance, default button styling is acceptable, theme override would be over-reach.

These two visual types fall back to Power BI defaults intentionally.

### Visual types not used on the locked pages

`columnChart`, `clusteredColumnChart`, `barChart` (stacked), `scatterChart`, `donutChart`, `pieChart`, `funnel`, `gauge`, `treemap`, KPI visual, decomposition tree, smart narrative, etc. None of these appear on Pages 1-3 per 03 §d, so they are not styled. They will render with Power BI defaults if a future phase adds one; that is a known fall-back, not a defect.

---

## d) Data-goblin rules applied

Rules from the `pbi-report-design` skill that the theme operationalizes (the model-layer and layout-layer rules are not reproduced here; this section is theme-scope only).

| DG rule | Theme implementation |
|---|---|
| #4 Custom theme over default | `name: Tonnelle_Risk_Naik` replaces `CY26SU05` once user runs View > Themes > Browse. |
| #9 Muted, soft colors | All 10 palette tokens are desaturated by construction; the locked palette was chosen with this rule in mind. |
| #9 Color encodes meaning (red=bad, green=good); use only when that is the encoding | This report uses risk_low/medium/high precisely as the risk encoding. Semantic slots `good`/`bad`/`neutral` make the mapping explicit. |
| #10 Pre-attentive attributes intentional | Title weight (Semibold), KPI value scale (32pt vs 11pt labels), and color tokens carry the visual hierarchy. No decoration. |
| #11 Segoe UI / Segoe UI Semibold only | textClasses and every per-visual font setting use only these two. |
| Minimum readable 12pt | **Deviation documented in 03 §f-6.** Body floor is 11pt; axis and data labels 10pt; multiRowCard category label 9pt. Justified by "dense informational" density on a 1280-wide canvas. |
| Minimize drop shadows (vestibular) | `*.*.dropShadow.show = false` wildcard. |
| Transparent visual backgrounds | `*.*.background.show = false` wildcard. `card`, `multiRowCard`, `slicer` re-enable `#FFFFFF` fill where the visual needs to read as a discrete object on the white canvas. |
| Visual titles left-aligned, Semibold 14pt | `*.*.title` wildcard. |
| Subtract don't add (tables) | `tableEx.grid.gridVertical = false`, no row banding (`backColorSecondary = #FFFFFF`), totals off, header background a single subtle `#f1f1f1`. |
| Minimal axis ornamentation | `lineChart.categoryAxis.gridlineShow = false`, `valueAxis.gridlineShow = false`, axis titles off; same for `clusteredBarChart`. |
| Sort by value descending (charts) | Per-visual, not theme-driven. Phase 9 sets sort orders on the two bar charts and the table. |
| 3-30-300 detail gradient, equal spacing | Layout-layer, not theme. Phase 9 sets positions. |

---

## e) Self-verification

Run from project root.

1. **JSON parse.**
   ```
   python -c "import json; json.load(open(r'assets/theme.json')); print('OK')"
   ```
   Result: `OK`. File parses.

2. **Hex exactness.** Grep extracted 84 hex tokens from `assets/theme.json`. Distinct set: `{#488f31, #de425b, #e8b450, #8cbcac, #ec9c9d, #f1f1f1, #1a1a1a, #5a5a5a, #FFFFFF, #e0e0e0}` — exactly the 10 locked tokens in 03 §c1, no others.

3. **Trailing commas.** Regex `,\s*[\]\}]` against the file returns zero matches.

4. **dataColors length.** Array has 8 entries (DG floor). Order documented in §a above.

5. **visualStyles coverage.** Eight entries: `*`, `card`, `multiRowCard`, `tableEx`, `pivotTable`, `lineChart`, `clusteredBarChart`, `slicer`. Each maps to a visual type that appears at least once across Pages 1-3 per 03 §d. `textbox` and `actionButton` are intentionally absent; see §c above.

6. **Schema sanity.** Top-level keys (`name`, `dataColors`, `background`, `foreground`, `tableAccent`, `secondBackground`, `good`, `neutral`, `bad`, `minimum`, `center`, `maximum`, `textClasses`, `visualStyles`) all appear in the Microsoft theme JSON reference (learn.microsoft.com/power-bi/create-reports/desktop-report-themes). Per-visual property names (`title`, `categoryLabels`, `labels`, `grid`, `columnHeaders`, `values`, `legend`, `categoryAxis`, `valueAxis`, `header`, `items`, etc.) match Power BI Desktop's formatting card names. Unrecognized properties are silently ignored by Power BI, so a stray name does not break theme application; the worst case is that one setting falls back to default.

---

## f) Known caveats

1. **Visual-level overrides will trump theme defaults.** Phase 9 may set conditional formatting on the High Risks KPI value color (per 03 §d Page 1 #3: tint to `#de425b` when value > 10), and conditional fill on the P-I matrix cells (per 03 §c1 heatmap table). These overrides are expected and do not reflect a theme problem.

2. **multiRowCard property names vary across Power BI Desktop builds.** `card.outline`, `card.barShow`, and `cardPadding` are documented but periodically renamed. If the Phase 11 Page 3 meta strip renders with default styling, the fix is at the visual level, not the theme.

3. **Line chart marker properties.** Markers on/off and marker size are set per-visual in Phase 9 (line-styles formatting card), not via theme. The theme leaves marker defaults untouched.

4. **No textbox/actionButton styling.** See §c "Visual types not styled."

5. **Header bar styling from the mockup.** The mockup shows a dark navy header bar across the top of each page. The theme does not encode this; the page header is a textbox (Page 1/2 #1, Page 3 #2) and any solid-fill banner styling is set inline in the textbox at Phase 9 if the user wants the mockup's banner feel. Theme-driven page-level backgrounds are not used (light canvas only, per 03 §c1).

---

## g) User-side step

One click in Power BI Desktop:

1. Open `pbip/Tonnelle_Risk.pbip`.
2. **View** ribbon > **Themes** > **Browse for themes**.
3. Navigate to `assets/theme.json` > Open.
4. Power BI swaps the active theme. Save (`Ctrl-S`).
5. Confirm `pbip/Tonnelle_Risk.Report/definition/report.json` now references the new theme under `themeCollection`.

Phase 9 (Page 1 layout) is unblocked once the theme is applied.
