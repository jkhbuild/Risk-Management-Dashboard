"""Run a DAX query against the published Tonnelle_Risk semantic model via fab api.

Usage:
  PYTHONUTF8=1 python scripts/run_dax.py "EVALUATE ROW(\"Active\", [Active Risks])"
  PYTHONUTF8=1 python scripts/run_dax.py --file query.dax
  echo 'EVALUATE ROW("X", [Total Risks])' | python scripts/run_dax.py -

Auth: requires `fab auth status` to show a logged-in account with workspace access.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

WORKSPACE_ID = "e3bf1016-3e76-48d3-aea9-bfe12b955abe"
DATASET_ID = "76460c68-be78-43aa-9b2e-7d195cc6e606"
ENDPOINT = f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/executeQueries"


def run_dax(query: str) -> dict:
    body = {
        "queries": [{"query": query}],
        "serializerSettings": {"includeNulls": True},
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(body, f)
        body_path = f.name
    try:
        result = subprocess.run(
            ["fab", "api", "-X", "post", "-A", "powerbi", ENDPOINT, "-i", body_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    finally:
        Path(body_path).unlink(missing_ok=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout)
        sys.exit(result.returncode)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(f"Non-JSON response:\n{result.stdout}\n")
        sys.exit(2)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("query", nargs="?", help="DAX query string")
    g.add_argument("--file", help="Path to file containing the DAX query")
    p.add_argument(
        "--raw",
        action="store_true",
        help="Print the full JSON response instead of just the rows",
    )
    args = p.parse_args()

    if args.file:
        query = Path(args.file).read_text(encoding="utf-8")
    elif args.query == "-":
        query = sys.stdin.read()
    else:
        query = args.query

    response = run_dax(query)
    if args.raw:
        json.dump(response, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    inner = response.get("text", response)
    if isinstance(inner, str):
        sys.stderr.write(f"Unexpected response body:\n{inner}\n")
        sys.exit(2)
    rows = inner.get("results", [{}])[0].get("tables", [{}])[0].get("rows", [])
    json.dump(rows, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
