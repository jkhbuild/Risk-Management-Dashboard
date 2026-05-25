# Conditional formatting JSON reference (PBIR)

Cross-cutting reference for hand-authoring Rules-based conditional formatting (CF) directly in `visual.json` files under `pbip/Tonnelle_Risk.Report/definition/pages/<page>/visuals/<visual>/visual.json`. Empirically verified on this project's Power BI Desktop build (2026-05-23) by reverse-engineering Desktop UI fx output.

## a. The breakthrough — the working shape

The renderer engages CF only when the JSON matches **Desktop UI fx's exact emission shape** for the given visual type. Multiple shapes load without parse error but do not render. The Power BI Desktop runtime is the validator; `objects.<container>[N].properties.<propName>` is schema-declared `additionalProperties: {}` (unrestricted), so invalid shapes are silently ignored. Ground truth for "did CF engage" is the visual's **Format pane > property > fx dialog** after re-opening the .pbip.

### Card visuals — `labels.color`

Active slot is **labels[0] WITHOUT a selector** in Pattern 2 And-bounded form. labels[1] holds a vestigial Pattern 1 duplicate Desktop preserves but doesn't actively render. `$schema` must be `visualContainer/2.9.0/schema.json` (not 2.7.0).

```json
"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json",
...
"objects": {
  "labels": [
    {
      "properties": {
        "color": {
          "solid": {
            "color": {
              "expr": {
                "Conditional": {
                  "Cases": [
                    {
                      "Condition": {
                        "And": {
                          "Left":  { "Comparison": { "ComparisonKind": 1, "Left": { "Measure": {...} }, "Right": { "Literal": { "Value": "10D" } } } },
                          "Right": { "Comparison": { "ComparisonKind": 3, "Left": { "Measure": {...} }, "Right": { "Literal": { "Value": "99D" } } } }
                        }
                      },
                      "Value": { "Literal": { "Value": "'#e5687c'" } }
                    }
                  ]
                }
              }
            }
          }
        }
      }
    },
    {
      "properties": {
        "color": {
          "solid": {
            "color": {
              "expr": {
                "Conditional": {
                  "Cases": [
                    {
                      "Condition": {
                        "Comparison": {
                          "ComparisonKind": 1,
                          "Left":  { "Measure": {...} },
                          "Right": { "Literal": { "Value": "10.0D" } }
                        }
                      },
                      "Value": { "Literal": { "Value": "'#de425b'" } }
                    }
                  ]
                }
              }
            }
          }
        }
      },
      "selector": {
        "data": [{ "dataViewWildcard": { "matchingOption": 1 } }]
      }
    }
  ]
}
```

**Both entries reference the same measure with the same threshold.** Use whatever upper bound Desktop's fx would pick (typically a comfortable round-up of the data range — `99D` for a value of 12). The second entry's threshold uses `10.0D` (decimal) while the first uses `10D` (integer); not functionally significant.

### Matrix / pivotTable visuals — `values.backColor` / `values.fontColor`

Different active-slot index. Active slot is **values[1]** with `dataViewWildcard` selector; values[0] is a non-CF switch toggle (e.g., `valuesOnRow`). Multi-case Conditional supported directly. See `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/PIMatrix/visual.json` (Phase 9 working CF) for a 3-case heatmap example with `[Cell PI Score]` thresholds.

### Other visual types

Active-slot index varies. Always reverse-engineer by: (1) authoring CF via Desktop UI fx on a clone of the target visual, (2) saving, (3) reading the emitted JSON, (4) byte-mirroring the structure onto the target.

## b. Failure modes burned through in this project

| Round | Shape | Result |
|---|---|---|
| 1 | Pattern 1 alone at `labels[0]` with selector | fx dialog showed UI defaults (1 and 9999), not authored threshold |
| 2 | Pattern 2 at `labels[0]` (no selector) + Pattern 1 at `labels[1]` (with selector), `$schema 2.7.0` | User reported "for >1 and <9999" — renderer didn't engage even though structure was close |
| 3 | Measure-driven CF (`solid.color.expr.Measure` with helper DAX measure returning hex) at `labels[0]` | Helper measure greyed out as Color field in fx dialog. Field-value CF apparently isn't supported on card visuals; only Rules CF is. |
| 4 | Empty `{"properties": {}}` at `labels[0]` + Pattern 1 at `labels[1]` with selector | Mirrors what Desktop's "Remove CF" operation leaves behind. Renderer reads this as "no active CF". |
| 5 | Pattern 2 at `labels[0]` (no selector) + Pattern 1 at `labels[1]` (with selector), **`$schema 2.9.0`** | **WORKS.** Validated empirically. |

**Two key axes the renderer is sensitive to:** the active slot index per visual type, AND the schema version. Both must match Desktop's expectations.

## c. Anatomy reference

```
visual.objects.<container>[ACTIVE_SLOT].properties.<propName>.solid.color.expr.<expr-form>
```

- `<container>` — `labels` (card value), `values` (matrix/table cells), `dataPoint` (chart series), etc. Container name matches the Format pane section name.
- `ACTIVE_SLOT` — visual-type-dependent. Card: `[0]`. Matrix: `[1]`. Other types: reverse-engineer.
- `<propName>` — `color`, `backColor`, `fontColor`, `fill`, etc. See line 766 of the pbir-format skill's `references/schema-patterns/conditional-formatting.md` for the full list of CF-capable properties.
- `solid.color` is the wrapper for color-valued CF. Non-color CF (e.g., font size by measure) omits `solid.color` and goes directly to `expr`.
- `<expr-form>` — `Conditional` (rules) or `FillRule` (gradient).

## d. Enum reference

From `microsoft/json-schemas` semanticQuery 1.4.0 + the pbir-format skill's CF reference:

| Token | Value | Meaning |
|---|---|---|
| `ComparisonKind` | 0 | Equal |
|  | 1 | GreaterThan |
|  | 2 | GreaterThanOrEqual |
|  | 3 | LessThan ⚠ (data-goblin's skill says "LessThanOrEqual" but Desktop emits 3 for `<`; trust Desktop's emission) |
|  | 4 | LessThanOrEqual (per skill) / LessThan (per Desktop emission convention) |
| `matchingOption` | 0 | Match identities AND totals (default) |
|  | 1 | Match instances with identities only (most common) |
|  | 2 | Match totals only |
| `Aggregation.Function` | 0-8 | Sum, Avg, DistinctCount, Min, Max, Count, Median, StDev, Var |

Note: the skill's `references/schema-patterns/conditional-formatting.md` says `ComparisonKind 3` = `LessThanOrEqual` and `4` = `LessThan`. The `how-to/apply-advanced-conditional-formatting.md` in the same skill says `3` = `LessThanOrEqual` and `4` = `LessThan`. **Desktop's emitted CF in this project uses `3` for `<` (LessThan)**. When hand-authoring, match Desktop's convention.

## e. Literal value suffixes

JSON string values inside `Literal.Value` carry a type suffix:

- `"10D"` → double (use for thresholds in `Comparison.Right`; can also be `"10.0D"`)
- `"5L"` → int64 (used in `scopeId` filters)
- `"'#de425b'"` → string with internal single quotes. **Lowercase hex per Desktop convention.**
- `"true"` / `"false"` → boolean
- `"'Segoe UI'"` → string

## f. Field references

For a **measure**:
```json
"Left": {
  "Measure": {
    "Expression": { "SourceRef": { "Entity": "<table_name>" } },
    "Property": "<measure_name>"
  }
}
```

For a **column**:
```json
"Left": {
  "Column": {
    "Expression": { "SourceRef": { "Entity": "<table_name>" } },
    "Property": "<column_name>"
  }
}
```

For an **extension measure** (from `reportExtensions.json`):
```json
"Left": {
  "Measure": {
    "Expression": { "SourceRef": { "Schema": "extension", "Entity": "<entity_name>" } },
    "Property": "<measure_name>"
  }
}
```

Model measures: omit `Schema`. Extension measures: include `"Schema": "extension"`.

**Critical gotcha:** `pbir visuals cf --rules` always emits `Left.Measure` even for column-bound CF. Power BI rejects this on open with `Missing_References: (<table>) <column>`. Always check this when adapting CLI output.

## g. Authoring workflow

1. **Identify the CF need.** Visual + property + rule logic.
2. **Confirm Power BI Desktop is closed.** Close-edit-open protocol; PBIR writer doesn't aggressively normalize like TMDL but a save-while-open can overwrite an external edit.
3. **Read the target `visual.json`.** Note the `$schema` URL. If the visual has never had CF authored via Desktop UI, the schema may be < 2.9.0 — **bump it to 2.9.0**.
4. **Author the CF block** using §a's verified shape for the visual type. Default to Rules CF; field-value (measure-driven) CF is not reliable on card visuals.
5. **Validate** via `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 pbir validate pbip/Tonnelle_Risk.pbip`. Catches structural errors only.
6. **User opens PBIP** and confirms two things:
   - **CF rule appears in Format pane > property > fx dialog** with the exact threshold values authored (not UI default placeholders). This is the silent-failure checkpoint.
   - **CF actually colors the visual on canvas** when the rule fires.
7. **If fx dialog shows default placeholders**, the shape didn't engage. The most common causes (in order of likelihood):
   - Wrong active-slot index (matrix CF was put at `values[0]` instead of `values[1]`; card CF was put at `labels[1]` instead of `labels[0]`)
   - `$schema` version too old
   - Selector present on the active slot when it shouldn't be (card CF active slot has NO selector)
   - Used Pattern 1 (single bound) where Desktop expects Pattern 2 (And-bounded)
8. **Document the CF block** in the relevant phase doc. Format: visual name, property path, CF basis, rule logic.

## h. The reverse-engineering fallback

If a visual type's active-slot convention is unknown, the fastest path is:

1. Have the user author CF via Desktop UI fx on the target visual (or a clone of it)
2. Save and close the .pbip
3. Read the emitted `visual.json` byte-for-byte
4. Identify which `objects.<container>[N]` index Desktop wrote CF to, and whether it included a `selector`
5. That is the active-slot convention for that visual type on this Desktop build; byte-mirror the structure for future CF on similar visuals

This is how the card pattern in §a was nailed down. Phase 9's iteration history shows the same process for the PIMatrix pivotTable.

## i. Properties that support measure-based CF

Per the pbir-format skill's `references/schema-patterns/conditional-formatting.md` (line 766):

```
fill, borderColor, defaultColor, fontColor, color, backgroundColor, lineColor, markerColor, strokeColor, text, titleText, fontSize, strokeWidth, weight, transparency, radius, url, good, bad, neutral, target, icon
```

Properties NOT in this list accept only literal values or `ThemeDataColor`. They cannot be driven by measures.

**Practical caveat surfaced in this project:** even properties on this list may not accept measure-driven CF on every visual type. Card-visual `labels.color` is on the list but Desktop's fx dialog greys out helper measures as Color field choices — only Rules CF works on cards. The skill's recommendation to "default to measure-driven CF" applies cleanly to chart visuals (bar, column, line) but not necessarily cards.

## j. Failure modes in the project (full table)

| Failure | Cause | Resolution |
|---|---|---|
| `pbir visuals cf --rules` JSON loads but doesn't render | CLI emit shape doesn't engage Power BI's CF renderer | Hand-author using §a verified shape |
| `Missing_References: (Risk_Register) risk_level` | CLI emitted `Left.Measure` for a column reference | Manually swap to `Left.Column`, or use theme `dataColors` slot order for series |
| `RepeatedIndicesProjectionsOrGroupBy` | CF comparison on a column already projected as Series/Rows/Columns creates a duplicate in data shape | Use a helper measure, theme slot order, or separate dim table (Phase 9 PIMatrix solution: `dim_Probability`/`dim_Impact`) |
| Matrix CF backColor not firing on empty cells | Values measure returns BLANK for empty cells; CF on `values.backColor` doesn't engage on BLANK | Make Values measure return `0` instead: `COUNTROWS(<table>) + 0` (Phase 9 PIMatrix solution) |
| fx dialog shows default placeholders, not authored thresholds | Wrong active slot, old schema, or wrong selector presence (see §g step 7) | Reverse-engineer Desktop's emission via §h, byte-mirror |
| Helper color measure greyed out in fx dialog as Color field | Card visuals don't support field-value CF; only Rules CF works | Use Rules CF (Conditional/Cases/Comparison) with §a's verified shape |

## k. Related references

- `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/KPIHighRisks/visual.json` — verified working card CF (Pattern 2 at labels[0] + Pattern 1 at labels[1])
- `pbip/Tonnelle_Risk.Report/definition/pages/Overview/visuals/PIMatrix/visual.json` — verified working matrix CF (Conditional/Cases at values[1] with selector + multi-case for heatmap bands)
- `.claude/skills/pbir-format/references/schema-patterns/conditional-formatting.md` — data-goblin skill's CF reference (gradients, measure-driven for charts, full enum tables)
- `.claude/skills/pbir-format/references/how-to/apply-advanced-conditional-formatting.md` — data-goblin step-by-step guide (extension measures, label patterns, Scenario 7 Rules CF)
- `.claude/skills/pbir-format/examples/K201-MonthSlicer.Report/` — full example PBIR report with CF
