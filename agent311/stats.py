"""Answer "what's happening in my area?" questions from the real 311 data.

An "area" is either a postal code prefix (FSA) like "M6H", or a ward like
"Davenport", "ward 9" or "9".

Important caveat (also in the governance docs): these are counts of REPORTS,
not counts of PROBLEMS. An area with few pothole reports might have few
potholes, or just residents who report less.
"""

import re
from collections import Counter

FSA_PATTERN = re.compile(r"^M\d[A-Z]$")   # every Toronto postal code starts with M


def find_ward(rows, text):
    """Match user text like 'ward 9', '09', or 'davenport' to a ward name in the data."""
    text = text.strip().lower()
    all_wards = sorted(set(row["ward"] for row in rows if row["ward"]))

    # A number: "ward 9", "9", "09"
    number_match = re.search(r"\d+", text)
    if number_match:
        number = int(number_match.group())
        for ward in all_wards:
            ward_number = re.search(r"\((\d+)\)", ward)    # "Davenport (09)" -> "09"
            if ward_number and int(ward_number.group(1)) == number:
                return ward

    # A name: "davenport", "toronto-danforth"
    for ward in all_wards:
        if text and text in ward.lower():
            return ward
    return None


def filter_area(rows, area):
    """Return (label, matching rows) for an area, or (None, []) if not recognised."""
    area_clean = area.strip().upper()
    if FSA_PATTERN.match(area_clean):
        matching = [row for row in rows if row["fsa"] == area_clean]
        return f"postal area {area_clean}", matching

    ward = find_ward(rows, area)
    if ward:
        matching = [row for row in rows if row["ward"] == ward]
        return f"ward {ward}", matching

    return None, []


def area_summary(rows, area, request_type=None, top_n=5):
    """Summary of 311 requests for one area. Returns a plain dict."""
    label, area_rows = filter_area(rows, area)
    if label is None:
        return {"error": f"Could not recognise area '{area}'. Use a postal code prefix "
                         f"like M6H, or a ward name/number."}
    if not area_rows:
        return {"error": f"No 311 requests found for {label}."}

    type_counts = Counter(row["type"] for row in area_rows)
    summary = {
        "area": label,
        "total_requests": len(area_rows),
        "top_request_types": type_counts.most_common(top_n),
    }

    if request_type:
        summary["request_type"] = request_type
        summary["count_of_this_type"] = type_counts.get(request_type, 0)
        summary["rank_in_area"] = rank_of(type_counts, request_type)
        type_rows = [row for row in area_rows if row["type"] == request_type]
        summary["status_breakdown"] = dict(Counter(row["status"] for row in type_rows))
        summary["busiest_months"] = Counter(row["month"] for row in type_rows).most_common(3)

    return summary


def rank_of(counter, key):
    """1 = most common. None if the key never appears."""
    for position, (name, _count) in enumerate(counter.most_common(), start=1):
        if name == key:
            return position
    return None


def city_totals(rows, top_n=10):
    """City-wide view, used by the README and the workshop deck."""
    return {
        "total_requests": len(rows),
        "top_request_types": Counter(row["type"] for row in rows).most_common(top_n),
        "by_division": Counter(row["division"] for row in rows).most_common(),
    }
