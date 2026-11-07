import re

# A bracketed citation group, e.g. "[HDFC FY26 p.248]", "[HDFC FY26 p.45, 247]",
# "[HDFC FY26 p.248, p.400]" or "[HDFC FY25 p.228, HDFC FY26 p.248]".
_GROUP = re.compile(r"\[([^\]]*HDFC FY\d{2}[^\]]*)\]")
_PART = re.compile(r"(HDFC FY\d{2})\s+p\.\s*(\d+)|(?:p\.\s*)?(\d+)")


def parse_citations(text):
    """Return the sorted unique (source, page) pairs cited in text."""
    found = set()
    for group in _GROUP.findall(text):
        source = None
        for m in _PART.finditer(group):
            if m.group(1):
                source = m.group(1)
                found.add((source, int(m.group(2))))
            elif source and m.group(3):
                found.add((source, int(m.group(3))))
    return sorted(found)
