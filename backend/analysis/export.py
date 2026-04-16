from __future__ import annotations

import csv
import io
import json


def table_to_csv_string(rows: list[dict]) -> str:
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def json_export_string(payload: dict) -> str:
    return json.dumps(payload, indent=2)
