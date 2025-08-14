#!/usr/bin/env python3
"""
Burning Man Camps Data Collector

This script scrapes the public Playa Info Camp Directory to collect
camp name, website, location, and description, saving the result to
`camps.json` by default.

Usage:
    python collect_camps.py [--output camps.json] [--max-pages N]
"""

import argparse
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Set, Optional

import requests

from camp_parser import extract_camp_links_from_index, extract_camp_data
from geo import normalized_location_to_latlon


BASE_DIR_URL = "https://directory.burningman.org/camps/?page={page}"
START_PAGE = 1
END_PAGE = 30

REQUEST_DELAY = 1.0
REQUEST_TIMEOUT = 30


TIME_PATTERN = re.compile(r"\b((?:[0-1]?\d|2[0-3]):[0-5]\d)\b")


def _extract_clock(text: str) -> Optional[str]:
    if not text:
        return None
    matches = TIME_PATTERN.findall(text)
    if matches:
        return matches[-1]
    return None


def _extract_ring(text: str) -> Optional[str]:
    if not text:
        return None
    s = text.strip()
    if re.search(r"\bEsplanade\b", s, flags=re.IGNORECASE):
        return "Esplanade"
    m = re.search(r"\b([A-Ka-k])\b", s)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b([A-Ka-k])\s*(?:Plaza|Plz)\b", s, flags=re.IGNORECASE)
    if m:
        return m.group(1).upper()
    for word in re.findall(r"\b([A-Za-z][A-Za-z\-']*)\b", s):
        if word.lower() == 'esplanade':
            return 'Esplanade'
        first = word[0].upper()
        if first in "ABCDEFGHIJK":
            return first
    return None


def normalize_location(raw_location: str) -> str:
    if not raw_location:
        return ""
    s = re.sub(r"\s*\([^)]*\)", "", raw_location)
    s = re.sub(r",.*$", "", s)
    s = s.replace('@', '&')
    s = re.sub(r"\s*&\s*", " & ", s)
    s = re.sub(r"\s+", " ", s).strip()
    ring = _extract_ring(s)
    clock = _extract_clock(s)
    if ring and clock:
        return f"{ring} & {clock}"
    if '&' in s:
        left, right = [part.strip() for part in s.split('&', 1)]
        left_ring = _extract_ring(left)
        right_ring = _extract_ring(right)
        left_clock = _extract_clock(left)
        right_clock = _extract_clock(right)
        ring2 = left_ring or right_ring
        clock2 = right_clock or left_clock
        if ring2 and clock2:
            return f"{ring2} & {clock2}"
    return s


class CampCollector:
    def __init__(self, output_file: str = "camps.json", max_pages: int = None):
        self.output_file = output_file
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BurningMan-EventGuide-CampCollector/1.0'
        })

    def collect_all_detail_links(self) -> List[str]:
        links: List[str] = []
        print("Collecting camp links from index pages...")
        total_pages = END_PAGE - START_PAGE + 1

        for i, page in enumerate(range(START_PAGE, END_PAGE + 1), 1):
            if self.max_pages and i > self.max_pages:
                print(f"Reached max pages limit ({self.max_pages})")
                break

            url = BASE_DIR_URL.format(page=page)
            print(f"  Processing index {i}/{total_pages}: {url}")
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                page_links = extract_camp_links_from_index(response.text)
                print(f"    Found {len(page_links)} camp links")
                links.extend(page_links)
            except requests.RequestException as e:
                print(f"    Error fetching {url}: {e}")

            if i < total_pages:
                time.sleep(REQUEST_DELAY)

        # De-duplicate while preserving order
        seen: Set[str] = set()
        unique_links: List[str] = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        print(f"\nTotal unique camp links: {len(unique_links)}")
        return unique_links

    def collect_camp_details(self, detail_links: List[str]) -> List[Dict]:
        camps: List[Dict] = []
        total = len(detail_links)
        print(f"\nCollecting details for {total} camps...")

        for idx, link in enumerate(detail_links, 1):
            print(f"  Processing {idx}/{total}: {link}")
            try:
                response = self.session.get(link, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = extract_camp_data(response.text, link)
                # Add normalized location
                data["normalized_location"] = normalize_location(data.get("location", ""))
                # Add approximate coordinates if normalization succeeded
                try:
                    if data["normalized_location"] and "&" in data["normalized_location"]:
                        lat, lon = normalized_location_to_latlon(data["normalized_location"])
                        data["latitude"] = lat
                        data["longitude"] = lon
                except Exception:
                    # Skip coordinate assignment on parsing errors
                    pass
                camps.append(data)
            except requests.RequestException as e:
                print(f"    Error fetching {link}: {e}")

            time.sleep(REQUEST_DELAY)

        print(f"\nSuccessfully collected {len(camps)} camps")
        return camps

    def save(self, camps: List[Dict]) -> None:
        print(f"\nSaving {len(camps)} camps to {self.output_file}...")
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(camps, f, indent=2, ensure_ascii=False)

            file_size = Path(self.output_file).stat().st_size
            print(f"✓ Data saved. File size: {file_size / (1024*1024):.2f} MB")
        except Exception as e:
            print(f"Error saving file: {e}")

    def run(self) -> None:
        print("=== Burning Man Camps Data Collector ===")
        print(f"Output file: {self.output_file}")
        if self.max_pages:
            print(f"Max pages: {self.max_pages}")
        print()

        links = self.collect_all_detail_links()
        if not links:
            print("No camp links found. Exiting.")
            return

        camps = self.collect_camp_details(links)
        if not camps:
            print("No camp details collected. Exiting.")
            return

        self.save(camps)
        print("\n=== Collection Complete ===")


def main():
    parser = argparse.ArgumentParser(
        description="Collect Burning Man camp directory data and save to JSON file"
    )
    parser.add_argument(
        "--output",
        default="camps.json",
        help="Output JSON file name (default: camps.json)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Limit number of index pages to scan (for testing)",
    )

    args = parser.parse_args()

    collector = CampCollector(output_file=args.output, max_pages=args.max_pages)
    try:
        collector.run()
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user.")
    except Exception as e:
        print(f"\nError during collection: {e}")
        raise


if __name__ == "__main__":
    main()


