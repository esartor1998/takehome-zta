"""Date facts that depend on where the mail comes from, read from the mail itself.

A day and month with no year ('Jan 10', '3/18') means the year that puts it nearest the message, so
'by Jan 10' written in December is next January and is not already overdue. A slash date is month
first in the US and day first nearly everywhere else, and the export shows which: a date like 18/3 can
only be day first, and 3/18 only month first. The order is decided once at ingest, stored with the
database, and read back whenever a question is asked
"""
import re
from datetime import datetime

SLASH_RE = re.compile(r'\b(\d{1,2})/(\d{1,2})\b')
MIN_VOTES = 3             # evidence needed before leaving the US order
_state = {'order': 'mdy'}


def slash_order():
    return _state['order']


def set_slash_order(order):
    _state['order'] = order if order in ('mdy', 'dmy') else 'mdy'


def detect_slash_order(texts):
    """'dmy' when the export holds day-first dates the other order cannot explain, else 'mdy'. 24/7 is
    a phrase, not a date, and a single odd date is not a locale"""
    day_first = month_first = 0
    for text in texts:
        for a, b in SLASH_RE.findall(text):
            a, b = int(a), int(b)
            if {a, b} == {24, 7}:
                continue
            if a > 12 >= b >= 1 and a <= 31:
                day_first += 1
            elif b > 12 >= a >= 1 and b <= 31:
                month_first += 1
    return 'dmy' if day_first >= MIN_VOTES and day_first > month_first else 'mdy'


def month_day(first, second):
    """(month, day) for the two numbers of a slash date in this export's order, or None"""
    month, day = (first, second) if _state['order'] == 'mdy' else (second, first)
    return (month, day) if 1 <= month <= 12 and 1 <= day <= 31 else None


def nearest(base, month, day):
    """The date with this month and day, in the year that puts it closest to base. None for Feb 30"""
    best = None
    for year in (base.year - 1, base.year, base.year + 1):
        try:
            candidate = datetime(year, month, day)
        except ValueError:
            continue
        gap = abs((candidate - base.replace(tzinfo=None)).days)
        if best is None or gap < best[0]:
            best = (gap, candidate)
    return best[1] if best else None
