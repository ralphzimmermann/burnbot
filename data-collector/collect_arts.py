#!/usr/bin/env python3
"""
Burning Man Artwork Data Collector

This script scrapes the public Playa Info Artwork Directory to collect
art name, location, and description, saving the result to `arts.json` by default.

Usage:
    python collect_arts.py [--output arts.json] [--max-pages N]
"""

import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple

import requests

from art_parser import extract_art_links_from_index, extract_art_data
from geo import clock_and_distance_to_latlon


BASE_DIR_URL = "https://directory.burningman.org/artwork/?page={page}"
START_PAGE = 1
END_PAGE = 8

REQUEST_DELAY = 1.0
REQUEST_TIMEOUT = 30


class ArtCollector:
    def __init__(self, output_file: str = "arts.json", max_pages: int = None):
        self.output_file = output_file
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BurningMan-EventGuide-ArtCollector/1.0'
        })

    def collect_all_detail_links(self) -> List[str]:
        links: List[str] = []
        print("Collecting artwork links from index pages...")
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
                page_links = extract_art_links_from_index(response.text)
                print(f"    Found {len(page_links)} artwork links")
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

        print(f"\nTotal unique artwork links: {len(unique_links)}")
        return unique_links

    def collect_art_details(self, detail_links: List[str]) -> List[Dict]:
        arts: List[Dict] = []
        total = len(detail_links)
        print(f"\nCollecting details for {total} artworks...")

        for idx, link in enumerate(detail_links, 1):
            print(f"  Processing {idx}/{total}: {link}")
            try:
                response = self.session.get(link, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = extract_art_data(response.text, link)
                name = data.get("name", "")
                location = data.get("location", "")
                description = data.get("description", "")

                lat, lon = self._maybe_compute_latlon_from_location(location)
                art_entry: Dict[str, Optional[str]] = {
                    "name": name,
                    "location": location,
                    "description": description,
                }
                if lat is not None and lon is not None:
                    art_entry["latitude"] = lat
                    art_entry["longitude"] = lon

                arts.append(art_entry)
            except requests.RequestException as e:
                print(f"    Error fetching {link}: {e}")

            time.sleep(REQUEST_DELAY)

        print(f"\nSuccessfully collected {len(arts)} artworks")
        return arts

    @staticmethod
    def _maybe_compute_latlon_from_location(location: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Parse artwork location strings like "5:30 1710', Open Playa" and return lat/lon.

        Returns (None, None) if parsing fails.
        """
        import re
        if not location:
            return (None, None)
        # Pattern: <HH:MM> <feet>' optionally followed by comma and text
        m = re.match(r"^\s*([0-1]?\d:[0-5]\d)\s+([0-9]{2,5})'?\b", location)
        if not m:
            return (None, None)
        clock = m.group(1)
        feet_str = m.group(2)
        try:
            feet = float(feet_str)
        except ValueError:
            return (None, None)
        try:
            lat, lon = clock_and_distance_to_latlon(clock, feet)
            return (lat, lon)
        except Exception:
            return (None, None)

    def save(self, arts: List[Dict]) -> None:
        print(f"\nSaving {len(arts)} artworks to {self.output_file}...")
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(arts, f, indent=2, ensure_ascii=False)

            file_size = Path(self.output_file).stat().st_size
            print(f"✓ Data saved. File size: {file_size / (1024*1024):.2f} MB")
        except Exception as e:
            print(f"Error saving file: {e}")

    def run(self) -> None:
        print("=== Burning Man Artwork Data Collector ===")
        print(f"Output file: {self.output_file}")
        if self.max_pages:
            print(f"Max pages: {self.max_pages}")
        print()

        links = self.collect_all_detail_links()
        if not links:
            print("No artwork links found. Exiting.")
            return

        arts = self.collect_art_details(links)
        if not arts:
            print("No artwork details collected. Exiting.")
            return

        self.save(arts)
        print("\n=== Collection Complete ===")


def main():
    parser = argparse.ArgumentParser(
        description="Collect Burning Man artwork directory data and save to JSON file"
    )
    parser.add_argument(
        "--output",
        default="arts.json",
        help="Output JSON file name (default: arts.json)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Limit number of index pages to scan (for testing)",
    )

    args = parser.parse_args()

    collector = ArtCollector(output_file=args.output, max_pages=args.max_pages)
    try:
        collector.run()
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user.")
    except Exception as e:
        print(f"\nError during collection: {e}")
        raise


if __name__ == "__main__":
    main()



