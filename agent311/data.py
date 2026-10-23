"""Download and load the City of Toronto 311 open data.

Run once to download:   python -m agent311.data

Each row in the City's file is one service request. Columns we use:
    Creation Date, Status, First 3 Chars of Postal Code, Intersection Street 1,
    Intersection Street 2, Ward, Service Request Type, Division
The file has NO free-text description from the resident and NO closing date.
"""

import csv
import io
import urllib.request
import zipfile

from . import config

_cached_rows = None   # so the 75 MB file is only read once per program run


def download():
    """Download the year's zip from the City's open data portal and unzip the CSV."""
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {config.DATA_URL} ...")
    with urllib.request.urlopen(config.DATA_URL, timeout=600) as response:
        zip_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        z.extractall(config.RAW_DIR)
    print(f"Saved to {config.RAW_DIR}")


def clean_row(raw):
    """Turn one raw CSV row into a small, tidy dictionary."""
    fsa = raw["First 3 Chars of Postal Code"].strip().upper()
    if fsa == "INTERSECTION":
        fsa = ""
    street1 = raw["Intersection Street 1"].strip()
    street2 = raw["Intersection Street 2"].strip()
    intersection = f"{street1} & {street2}" if street1 and street2 else ""
    date = raw["Creation Date"][:10]          # "2025-01-01 00:01:05.0000000" -> "2025-01-01"
    return {
        "date": date,
        "month": date[:7],                    # "2025-01"
        "status": raw["Status"].strip(),
        "fsa": fsa,                           # e.g. "M6H", or "" if only an intersection was given
        "intersection": intersection,
        "ward": raw["Ward"].strip(),          # e.g. "Davenport (09)"
        "type": raw["Service Request Type"].strip(),
        "division": raw["Division"].strip(),
    }


def load_requests(path=None):
    """Return every request as a list of dicts. Cached after the first call."""
    global _cached_rows
    if path is None and _cached_rows is not None:
        return _cached_rows

    path = path or config.DATA_FILE
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run: python -m agent311.data")

    rows = []
    # utf-8-sig strips the invisible "byte order mark" some Windows CSVs start with
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        for raw in csv.DictReader(f):
            rows.append(clean_row(raw))

    if path == config.DATA_FILE:
        _cached_rows = rows
    return rows


def division_for_type(rows, request_type):
    """Which City division handles a request type (the most common one in the data)."""
    counts = {}
    for row in rows:
        if row["type"] == request_type:
            counts[row["division"]] = counts.get(row["division"], 0) + 1
    if not counts:
        return "Unknown"
    return max(counts, key=counts.get)


if __name__ == "__main__":
    if config.DATA_FILE.exists():
        print(f"{config.DATA_FILE} already exists, skipping download.")
    else:
        download()
    rows = load_requests()
    print(f"Loaded {len(rows):,} service requests from {config.DATA_YEAR}.")
