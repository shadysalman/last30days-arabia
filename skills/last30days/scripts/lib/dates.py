"""Date utilities for last30days skill."""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


def parse_as_of_date(as_of_date: Optional[str]) -> Optional[str]:
    """Validate and normalize an --as-of date.

    Args:
        as_of_date: Date string in YYYY-MM-DD format.

    Returns:
        Normalized YYYY-MM-DD string, or None when no date was provided.

    Raises:
        ValueError: If the date is not in YYYY-MM-DD format.
    """
    if as_of_date is None:
        return None

    if not as_of_date.strip():
        raise ValueError("--as-of must be in YYYY-MM-DD format.")

    try:
        parsed = datetime.strptime(as_of_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(
            f"Invalid --as-of date: {as_of_date}. Expected YYYY-MM-DD."
        ) from exc

    return parsed.isoformat()


def get_date_range(days: int = 30, as_of_date: Optional[str] = None) -> Tuple[str, str]:
    """Get the date range for the last N days.

    When as_of_date is provided, the range ends at that date instead of today.

    Args:
        days: Number of days to look back.
        as_of_date: Optional end date in YYYY-MM-DD format.

    Returns:
        Tuple of (from_date, to_date) as YYYY-MM-DD strings.
    """
    normalized_as_of = parse_as_of_date(as_of_date)

    if normalized_as_of:
        to_date = datetime.strptime(normalized_as_of, "%Y-%m-%d").date()
    else:
        to_date = datetime.now(timezone.utc).date()

    from_date = to_date - timedelta(days=days)
    return from_date.isoformat(), to_date.isoformat()


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a date string in various formats.

    Supports: YYYY-MM-DD, ISO 8601, Unix timestamp
    """
    if not date_str:
        return None

    # Try Unix timestamp (from Reddit)
    try:
        ts = float(date_str)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (ValueError, TypeError):
        pass

    # Try ISO formats
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is not None:
                return dt.astimezone(timezone.utc)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def timestamp_to_date(ts: Optional[float]) -> Optional[str]:
    """Convert Unix timestamp to YYYY-MM-DD string."""
    if ts is None:
        return None
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.date().isoformat()
    except (ValueError, TypeError, OSError):
        return None


def get_date_confidence(date_str: Optional[str], from_date: str, to_date: str) -> str:
    """Determine confidence level for a date.

    Args:
        date_str: The date to check (YYYY-MM-DD or None)
        from_date: Start of valid range (YYYY-MM-DD)
        to_date: End of valid range (YYYY-MM-DD)

    Returns:
        'high', 'med', or 'low'
    """
    if not date_str:
        return 'low'

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        start = datetime.strptime(from_date, "%Y-%m-%d").date()
        end = datetime.strptime(to_date, "%Y-%m-%d").date()

        return 'high' if start <= dt <= end else 'low'
    except ValueError:
        return 'low'


def days_ago(date_str: Optional[str], reference_date: Optional[str] = None) -> Optional[int]:
    """Calculate how many days before the reference date a date is.

    If reference_date is None, use real today for backward compatibility.
    Returns None if date is invalid or missing.
    """
    if not date_str:
        return None

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        if reference_date:
            today = datetime.strptime(reference_date, "%Y-%m-%d").date()
        else:
            today = datetime.now(timezone.utc).date()
        delta = today - dt
        return delta.days
    except ValueError:
        return None


def recency_score(
    date_str: Optional[str],
    max_days: int = 30,
    reference_date: Optional[str] = None,
) -> int:
    """Calculate recency score (0-100).

    0 days before reference_date = 100, max_days before reference_date = 0.
    If reference_date is None, use real today for backward compatibility.
    """
    age = days_ago(date_str, reference_date=reference_date)
    if age is None:
        return 0

    if age < 0:
        return 100
    if age >= max_days:
        return 0

    return int(100 * (1 - age / max_days))


# Named windows accepted by --period, in English and Arabic.
_PERIOD_WORDS = {
    "today": 1, "day": 1, "24h": 1, "يوم": 1, "اليوم": 1,
    "week": 7, "weekly": 7, "أسبوع": 7, "اسبوع": 7, "الأسبوع": 7, "الاسبوع": 7,
    "fortnight": 14, "أسبوعين": 14, "اسبوعين": 14,
    "month": 30, "monthly": 30, "شهر": 30, "الشهر": 30,
    "quarter": 90, "quarterly": 90, "ربع": 90, "ثلاثة أشهر": 90, "3 أشهر": 90,
    "half": 180, "half-year": 180, "ستة أشهر": 180, "6 أشهر": 180,
    "year": 365, "yearly": 365, "annual": 365, "سنة": 365, "السنة": 365, "عام": 365,
}
_PERIOD_UNITS = {
    "h": 1 / 24, "hour": 1 / 24, "hours": 1 / 24,
    "d": 1, "day": 1, "days": 1,
    "w": 7, "week": 7, "weeks": 7,
    "m": 30, "mo": 30, "month": 30, "months": 30,
    "q": 90, "quarter": 90, "quarters": 90,
    "y": 365, "yr": 365, "year": 365, "years": 365,
}
_PERIOD_RE = re.compile(r"^(\d+)\s*([a-z]*)$")
# Most sources only index a few years back; beyond that results are empty.
MAX_PERIOD_DAYS = 3650


def parse_period(value: str) -> int:
    """Convert a --period value into a whole number of lookback days.

    Accepts a bare number of days ("45"), a number with a unit ("7d", "2w",
    "3m", "1y", "6 months", "24h"), or a named window ("week", "month",
    "quarter", "year", or the Arabic "أسبوع", "شهر", "سنة"). Months count as
    30 days and years as 365.

    Raises:
        ValueError: when the value is empty, zero, negative or unrecognized.
    """
    text = (value or "").strip().lower()
    if not text:
        raise ValueError("--period needs a value such as 7d, 2w, 3m or 1y.")
    if text in _PERIOD_WORDS:
        return _PERIOD_WORDS[text]
    match = _PERIOD_RE.match(text)
    if match:
        amount, unit = int(match.group(1)), match.group(2) or "d"
        if unit in _PERIOD_UNITS and amount > 0:
            days = max(1, round(amount * _PERIOD_UNITS[unit]))
            if days > MAX_PERIOD_DAYS:
                raise ValueError(f"--period is capped at {MAX_PERIOD_DAYS} days.")
            return days
    raise ValueError(
        f"Unrecognized --period {value!r}. Use e.g. 7d, 2w, 3m, 1y, week, month, quarter or year."
    )


def days_between(from_date: str, to_date: str) -> int:
    """Return the lookback length for an explicit YYYY-MM-DD..YYYY-MM-DD window."""
    start = datetime.strptime(from_date, "%Y-%m-%d").date()
    end = datetime.strptime(to_date, "%Y-%m-%d").date()
    if start >= end:
        raise ValueError(f"--from {from_date} must be before the end date {to_date}.")
    return (end - start).days
