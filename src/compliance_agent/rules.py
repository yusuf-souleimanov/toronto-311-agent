"""The compliance rule, kept deterministic on purpose.

The LLM extracts facts; plain code decides compliance. That split is easy to
audit and easy to explain to a compliance manager.
"""

from datetime import date


def years_between(start: date, end: date) -> float:
    return (end - start).days / 365.25


def is_compliant(issue_date: date | None, as_of: date, max_age_years: int) -> bool | None:
    """True if the document is recent enough, False if too old, None if undated.

    None means "can't decide" and should go to human review, never be read as compliant.
    """
    if issue_date is None:
        return None
    if issue_date > as_of:
        return None  # future-dated: probably an extraction error
    return years_between(issue_date, as_of) <= max_age_years
