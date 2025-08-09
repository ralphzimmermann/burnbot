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
import requests
import time
from pathlib import Path
from typing import List, Dict, Set
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


class EventCollector:
    """Main event collector class."""
    
    def __init__(self, output_file: str = "events.json", max_events: int = None):
        self.output_file = output_file
        self.max_events = max_events
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BurningMan-EventGuide-DataCollector/1.0'
        })
        
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
                events_data.append(event_data)
                
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
    
    args = parser.parse_args()
    
    collector = EventCollector(
        output_file=args.output,
        max_events=args.max_events
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
