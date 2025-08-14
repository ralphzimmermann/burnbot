#!/usr/bin/env python3
"""
Normalize camp location strings in camps.json and write back with a new
"normalized_location" field for each camp entry.

Rules:
- Put the location ring first and the clock position second: "<Ring> & <Clock>"
- Ring is either the literal "Esplanade" or a single letter A..K (uppercase)
- If the ring is a named street (e.g., "Gobsmack"), map to its letter by
  the initial character (e.g., "Gobsmack" -> "G"). "Esplanade" stays distinct
  from "E".
- The clock position is of the form H:MM (e.g., 7:25, 9:00)

Examples:
  "Gobsmack & 7:25"   -> "G & 7:25"
  "Esplanade & 7:45"  -> "Esplanade & 7:45"
  "9:00 & J"          -> "J & 9:00"
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


TIME_PATTERN = re.compile(r"\b((?:[0-1]?\d|2[0-3]):[0-5]\d)\b")


def extract_clock(text: str) -> Optional[str]:
    """Return the last clock-position time (H:MM) found in the text, if any."""
    if not text:
        return None
    matches = TIME_PATTERN.findall(text)
    if matches:
        return matches[-1]
    return None


def extract_ring(text: str) -> Optional[str]:
    """Extract the ring identifier: 'Esplanade' or a single letter A..K."""
    if not text:
        return None

    s = text.strip()

    # Special case: Esplanade (distinct from letter E)
    if re.search(r"\bEsplanade\b", s, flags=re.IGNORECASE):
        return "Esplanade"

    # Single letter ring token A..K
    m = re.search(r"\b([A-Ka-k])\b", s)
    if m:
        return m.group(1).upper()

    # Patterns like "G Plaza" / "G Plz"
    m = re.search(r"\b([A-Ka-k])\s*(?:Plaza|Plz)\b", s, flags=re.IGNORECASE)
    if m:
        return m.group(1).upper()

    # Named street: use initial letter if within A..K
    for word in re.findall(r"\b([A-Za-z][A-Za-z\-']*)\b", s):
        if word.lower() == 'esplanade':
            return 'Esplanade'
        first = word[0].upper()
        if first in "ABCDEFGHIJK":
            return first

    return None


def normalize_location(raw_location: str) -> str:
    """Normalize a raw location value to "<Ring> & <Clock>" when possible."""
    if not raw_location:
        return ""

    # Remove parenthetical notes and trailing comma sections (e.g., ", Man side")
    s = re.sub(r"\s*\([^)]*\)", "", raw_location)
    s = re.sub(r",.*$", "", s)

    # Normalize separators
    s = s.replace('@', '&')
    s = re.sub(r"\s*&\s*", " & ", s)
    s = re.sub(r"\s+", " ", s).strip()

    ring = extract_ring(s)
    clock = extract_clock(s)

    if ring and clock:
        return f"{ring} & {clock}"

    # If order is reversed like "9:00 & J" and the above didn't catch it,
    # try swapping parts around '&'
    if '&' in s:
        left, right = [part.strip() for part in s.split('&', 1)]
        left_ring = extract_ring(left)
        right_ring = extract_ring(right)
        left_clock = extract_clock(left)
        right_clock = extract_clock(right)
        ring2 = left_ring or right_ring
        clock2 = right_clock or left_clock
        if ring2 and clock2:
            return f"{ring2} & {clock2}"

    # As a fallback, return the original cleansed string
    return s


def process_file(input_path: Path, output_path: Optional[Path] = None) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        data: List[Dict[str, Any]] = json.load(f)

    for entry in data:
        raw_loc = entry.get('location', '') or ''
        entry['normalized_location'] = normalize_location(raw_loc)

    out_path = output_path or input_path
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Normalize camp locations in camps.json')
    parser.add_argument('--input', default='camps.json', help='Input camps JSON file')
    parser.add_argument('--output', help='Output JSON file (defaults to in-place update)')
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    process_file(input_path, output_path)


if __name__ == '__main__':
    main()


