from search import search

YEAR_TERMS = {"FY25": "March 31, 2025", "FY26": "March 31, 2026"}


def _format(hits, max_chars=1500):
    return "\n\n".join(
        f"[{h['source']} p.{h['page']}]\n{h['text'][:max_chars]}" for h in hits
    )


def search_reports(query: str, year: str = "") -> str:
    """Search HDFC Bank's annual reports and return the most relevant excerpts,
    each labelled with its source and page number like [HDFC FY26 p.248].
    Use this to find any figure or fact. Optionally set year to FY25 or FY26
    to restrict the search to one report."""
    print(f"  [TOOL] search_reports(query={query!r}, year={year!r})")
    hits = search(query, k=60, pool=120)
    key = year.upper().replace(" ", "")
    if key in YEAR_TERMS:
        hits = [h for h in hits if key in h["source"].upper().replace(" ", "")]
    return _format(hits[:8]) or "No results found."


def compare_years(topic: str) -> str:
    """Look up the same topic in both the FY25 and FY26 reports and return the
    excerpts for each year side by side. Use this when a question compares
    two years or asks how something changed, for example 'gross NPA' or
    'net interest margin'."""
    print(f"  [TOOL] compare_years(topic={topic!r})")
    parts = []
    for fy, period in YEAR_TERMS.items():
        hits = [h for h in search(f"{topic} {period}", k=60, pool=120)
                if fy in h["source"].upper().replace(" ", "")]
        parts.append(f"===== {fy} =====\n{_format(hits[:4]) or 'No results found.'}")
    return "\n\n".join(parts)


def percent_change(old_value: float, new_value: float) -> float:
    """Percentage change from old_value to new_value. Always use this for
    percentage change instead of calculating it yourself.
    Example: percent_change(1.33, 1.15) returns -13.53."""
    print(f"  [TOOL] percent_change({old_value}, {new_value})")
    if old_value == 0:
        return float("nan")
    return round((new_value - old_value) / old_value * 100, 2)


def difference(a: float, b: float) -> float:
    """Returns a minus b. Use this for changes measured in percentage points,
    for example difference(1.15, 1.33) returns -0.18."""
    print(f"  [TOOL] difference({a}, {b})")
    return round(a - b, 4)


def thousands_to_crore(value_in_thousands: float) -> float:
    """Convert a rupee amount given in thousands (the unit of the balance sheet
    tables, written as ` in '000) into crore. 1 crore = 10,000 thousand.
    Example: thousands_to_crore(31052504740) returns 3105250.47.
    Always use this instead of converting by hand."""
    print(f"  [TOOL] thousands_to_crore({value_in_thousands})")
    return round(value_in_thousands / 10000, 2)


if __name__ == "__main__":
    print(percent_change(1.33, 1.15))
    print(difference(1.15, 1.33))
    print(thousands_to_crore(31052504740))
    print(compare_years("total advances")[:1500])
