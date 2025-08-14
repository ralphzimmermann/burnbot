#!/usr/bin/env python3
"""
Burning Man Events Data Collector

This script collects event data from the Burning Man Playa Events website
and saves it to a structured JSON file.

Usage:
    python collect_events.py [--output events.json] [--max-events N]
"""

import argparse
import json
import re
import requests
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from event_parser import extract_event_ids_from_index, extract_event_data

# Configuration
BASE_URL = "https://playaevents.burningman.org/2025"
INDEX_URLS = [
    f"{BASE_URL}/playa_events/01",
    f"{BASE_URL}/playa_events/02", 
    f"{BASE_URL}/playa_events/03",
    f"{BASE_URL}/playa_events/04",
    f"{BASE_URL}/playa_events/05",
    f"{BASE_URL}/playa_events/06",
    f"{BASE_URL}/playa_events/07",
    f"{BASE_URL}/playa_events/08",
]

REQUEST_DELAY = 1.0  # Delay between requests to be respectful
REQUEST_TIMEOUT = 30  # Request timeout in seconds


def _normalize_camp_name(name: str) -> str:
    """Normalize camp names for robust matching.

    - lowercase
    - collapse whitespace
    - remove non-alphanumeric except '&'
    - normalize 'and' to '&' and vice versa for a unified key
    """
    if not name:
        return ""
    s = name.lower().strip()
    s = re.sub(r"\s+", " ", s)
    # normalize textual ' and ' to ' & '
    s = re.sub(r"\band\b", "&", s)
    # keep letters, numbers, spaces, and '&'
    s = re.sub(r"[^a-z0-9 &]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _load_camps_map(camps_file: Optional[str]) -> Dict[str, Dict]:
    """Load camps.json and return a lookup by normalized camp name.

    The value dict includes keys: name, normalized_location, latitude, longitude, location.
    """
    if not camps_file:
        return {}
    path = Path(camps_file)
    if not path.exists():
        print(f"Warning: camps file not found at {camps_file}; events will not be enriched.")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            camps = json.load(f)
        lookup: Dict[str, Dict] = {}
        for c in camps:
            name = c.get("name", "")
            key = _normalize_camp_name(name)
            if not key:
                continue
            lookup[key] = c
        print(f"Loaded {len(lookup)} camps from {camps_file}")
        return lookup
    except Exception as e:
        print(f"Warning: failed to read camps file {camps_file}: {e}")
        return {}


class EventCollector:
    """Main event collector class."""
    
    def __init__(self, output_file: str = "events.json", max_events: int = None, camps_file: Optional[str] = None):
        self.output_file = output_file
        self.max_events = max_events
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BurningMan-EventGuide-DataCollector/1.0'
        })
        self.camps_file = camps_file
        self.camps_by_name: Dict[str, Dict] = _load_camps_map(camps_file)
        
    def collect_all_event_ids(self) -> Set[str]:
        """
        Collect all event IDs from index pages.
        
        Returns:
            Set of unique event IDs
        """
        all_event_ids = set()
        
        print("Collecting event IDs from index pages...")
        
        for i, url in enumerate(INDEX_URLS, 1):
            print(f"  Processing index {i}/{len(INDEX_URLS)}: {url}")
            
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                event_ids = extract_event_ids_from_index(response.text)
                all_event_ids.update(event_ids)
                
                print(f"    Found {len(event_ids)} events (total unique: {len(all_event_ids)})")
                
            except requests.RequestException as e:
                print(f"    Error fetching {url}: {e}")
                continue
            
            # Be respectful with delays
            if i < len(INDEX_URLS):
                time.sleep(REQUEST_DELAY)
        
        print(f"\nTotal unique events found: {len(all_event_ids)}")
        return all_event_ids
    
    def collect_event_data(self, event_ids: List[str]) -> List[Dict]:
        """
        Collect detailed data for each event.
        
        Args:
            event_ids: List of event IDs to collect
            
        Returns:
            List of event data dictionaries
        """
        events_data = []
        total_events = len(event_ids)
        
        print(f"\nCollecting detailed data for {total_events} events...")
        
        for i, event_id in enumerate(event_ids, 1):
            if self.max_events and i > self.max_events:
                print(f"\nReached maximum events limit ({self.max_events})")
                break
                
            print(f"  Processing event {i}/{total_events}: {event_id}")
            
            try:
                event_url = f"{BASE_URL}/playa_event/{event_id}/"
                response = self.session.get(event_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                event_data = extract_event_data(response.text, event_id)
                # Enrich with camp location and coordinates, if available
                camp_name = event_data.get("camp", "")
                enriched = self._enrich_with_camp_location(event_data, camp_name)
                events_data.append(enriched)
                
                # Show progress every 50 events
                if i % 50 == 0:
                    print(f"    Progress: {i}/{total_events} events processed")
                
            except requests.RequestException as e:
                print(f"    Error fetching event {event_id}: {e}")
                continue
            
            # Be respectful with delays
            time.sleep(REQUEST_DELAY)
        
        print(f"\nSuccessfully collected data for {len(events_data)} events")
        return events_data

    def _enrich_with_camp_location(self, event: Dict, camp_name: str) -> Dict:
        """Return a copy of event with location/lat/lon enriched from camps map.

        If no match or no normalized_location is available, set location to "n/a".
        """
        # Work on a copy to avoid side-effects
        e = dict(event)
        # If we don't have camps, mark for manual review
        if not self.camps_by_name:
            if not e.get("location"):
                e["location"] = "n/a"
            return e

        key = _normalize_camp_name(camp_name)
        camp = self.camps_by_name.get(key)
        if not camp:
            # Attempt a looser match by stripping spaces
            loose_key = re.sub(r"\s+", "", key)
            for k, v in self.camps_by_name.items():
                if re.sub(r"\s+", "", k) == loose_key:
                    camp = v
                    break

        if camp:
            norm_loc = camp.get("normalized_location") or ""
            if norm_loc:
                e["location"] = norm_loc
                if "latitude" in camp and "longitude" in camp and camp["latitude"] and camp["longitude"]:
                    e["latitude"] = camp["latitude"]
                    e["longitude"] = camp["longitude"]
                return e

        # No usable camp location; set to n/a for manual review
        e["location"] = "n/a"
        # Do not set latitude/longitude when unresolved
        return e
    
    def save_events_data(self, events_data: List[Dict]) -> None:
        """
        Save events data to JSON file.
        
        Args:
            events_data: List of event data dictionaries
        """
        print(f"\nSaving {len(events_data)} events to {self.output_file}...")
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
            
            # Calculate file size
            file_size = Path(self.output_file).stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"✓ Data saved successfully!")
            print(f"  File: {self.output_file}")
            print(f"  Size: {file_size_mb:.2f} MB")
            print(f"  Events: {len(events_data)}")
            
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def run(self) -> None:
        """Run the complete data collection process."""
        print("=== Burning Man Events Data Collector ===")
        print(f"Output file: {self.output_file}")
        if self.max_events:
            print(f"Maximum events: {self.max_events}")
        print()
        
        # Step 1: Collect all event IDs
        event_ids = self.collect_all_event_ids()
        
        if not event_ids:
            print("No event IDs found. Exiting.")
            return
        
        # Convert to sorted list for consistent processing
        event_ids_list = sorted(list(event_ids))
        
        # Step 2: Collect detailed event data
        events_data = self.collect_event_data(event_ids_list)
        
        if not events_data:
            print("No event data collected. Exiting.")
            return
        
        # Step 3: Save to file
        self.save_events_data(events_data)
        
        print("\n=== Collection Complete ===")


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Collect Burning Man event data and save to JSON file"
    )
    parser.add_argument(
        "--output", 
        default="events.json",
        help="Output JSON file name (default: events.json)"
    )
    parser.add_argument(
        "--max-events",
        type=int,
        help="Maximum number of events to collect (for testing)"
    )
    parser.add_argument(
        "--camps",
        dest="camps_file",
        default=None,
        help="Path to camps.json for enriching locations (collect camps first)"
    )
    
    args = parser.parse_args()
    
    collector = EventCollector(
        output_file=args.output,
        max_events=args.max_events,
        camps_file=args.camps_file,
    )
    
    try:
        collector.run()
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user.")
    except Exception as e:
        print(f"\nError during collection: {e}")
        raise


if __name__ == "__main__":
    main()
