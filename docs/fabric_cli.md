# Fabric CLI workflow

`ms-fabric-cli` is the resolved path for verifying DAX measures against the published Power BI Service model without the Desktop publish-debug-republish loop.

## Identifiers (My Workspace; personal capacity, Fabric trial)

| Item | Value |
|---|---|
| Account | `JustinHwang@jhprojectcontrols.onmicrosoft.com` |
| Tenant ID | `1b44f439-b503-4651-aeab-0c577eb13370` |
| Workspace name | `My workspace.Personal` |
| Workspace ID | `e3bf1016-3e76-48d3-aea9-bfe12b955abe` |
| Dataset (semantic model) ID | `76460c68-be78-43aa-9b2e-7d195cc6e606` |
| Report ID | `5c91b779-a387-41bd-8816-f67c28654c30` |

The original CLAUDE.md 2026-05-25 status note referenced `jkh.build@gmail.com` for sign-in. That account has no Fabric tenant; the actual Fabric license lives on `JustinHwang@jhprojectcontrols.onmicrosoft.com` (own-tenant developer account).

## Install + PATH

CLI installed at `C:\Users\jkhbu\AppData\Local\Python\pythoncore-3.14-64\Scripts\fab.exe` (`ms-fabric-cli` 0.1.10). On 2026-05-25 the Scripts directory was appended to the user `Path` env var via `[Environment]::SetEnvironmentVariable("Path", ..., "User")`. A bare `fab` now resolves in a fresh PowerShell session.

A current PowerShell session opened before that change must refresh manually:
```powershell
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ';' + [Environment]::GetEnvironmentVariable("Path", "User")
```

## Auth

`fab auth login` is interactive and **requires a real console**. The Claude Code PowerShell tool runs without a TTY; the command fails with `No Windows console found. Are you running cmd.exe?`. Run it from a regular PowerShell window or use the Start-Process workaround. Once authenticated, the token persists across shells; subsequent `fab` invocations from the PowerShell tool work fine.

Verify with:
```powershell
fab auth status
```
The CLI prints a `✓` (U+2713). PowerShell's default cp1252 console breaks on it; set UTF-8 first or run via a wrapper that does:
```powershell
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Running DAX queries

Helper: `scripts/run_dax.py` wraps the executeQueries call.

```powershell
python scripts/run_dax.py 'EVALUATE ROW(\"Active\", [Active Risks], \"Total\", [Total Risks])'
python scripts/run_dax.py --file path/to/query.dax
python scripts/run_dax.py --raw 'EVALUATE TOPN(5, Risk_Register, [risk_score_overall], DESC)'
```

The helper hides three gotchas:
1. The Power BI REST body must be **BOM-less UTF-8**. PowerShell 5.1's `Set-Content -Encoding utf8` writes a BOM; the executeQueries endpoint rejects it (`InvalidJson: Unexpected UTF-8 BOM`). Python's `tempfile` + `encoding="utf-8"` produces clean BOM-less.
2. `fab api -A powerbi` **prepends** `https://api.powerbi.com/v1.0/myorg/` to the endpoint. Pass the relative path only (`groups/<ws>/datasets/<ds>/executeQueries`). The full URL form (`v1.0/myorg/groups/...`) double-prefixes and returns 404.
3. `fab api` wraps the upstream response under `text` (with `status_code` as a sibling). The script unwraps before extracting `results[0].tables[0].rows`.

## Ad-hoc REST calls

For non-DAX endpoints (refresh schedules, dataset metadata, reports list) call `fab api` directly:

```powershell
# List workspaces
fab api workspaces

# Get current dataset metadata
fab api "groups/e3bf1016-3e76-48d3-aea9-bfe12b955abe/datasets/76460c68-be78-43aa-9b2e-7d195cc6e606" -A powerbi

# Trigger a refresh
fab api -X post "groups/e3bf1016-3e76-48d3-aea9-bfe12b955abe/datasets/76460c68-be78-43aa-9b2e-7d195cc6e606/refreshes" -A powerbi
```

Default audience is `fabric` (Fabric REST API base `https://api.fabric.microsoft.com/v1/`). Use `-A powerbi` for the Power BI REST surface (where executeQueries lives).

## Smoke test (2026-05-25)

```
EVALUATE ROW(
  "Active",   [Active Risks],
  "Realized", [Realized Risks],
  "Closed",   [Closed Risks],
  "Total",    [Total Risks]
)
```
Result: `Active=32, Realized=2, Closed=3, Total=37`. Sum reconciles to the Risk_Register row count.

## Scope

Fabric CLI is in scope for the remaining iterations of this project. PBIP remains the canonical authoring artifact; the CLI is a verification channel. Publishing still happens via Power BI Desktop File → Publish; no CI/CD pipeline is set up against the dataset.
