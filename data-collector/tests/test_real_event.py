#!/usr/bin/env python3
"""
Test parsing with a real event that contains the problematic time formats.
"""

import requests
from event_parser import extract_event_data

def test_real_events_with_problematic_times():
    """Download and test real events that might have the problematic time formats."""
    
    # Test a few random events to see if we can find the problematic patterns
    test_event_ids = ["50893", "54757", "54484"]  # From our earlier sample
    
    print("=== Testing Real Events ===")
    
    for event_id in test_event_ids:
        print(f"\nTesting event {event_id}...")
        
        try:
            url = f"https://playaevents.burningman.org/2025/playa_event/{event_id}/"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            event_data = extract_event_data(response.text, event_id)
            
            print(f"Event ID: {event_id}")
            print(f"Type: {event_data.get('type', 'N/A')}")
            print(f"Camp: {event_data.get('camp', 'N/A')}")
            print(f"Times parsed: {len(event_data.get('times', []))}")
            
            for i, time_entry in enumerate(event_data.get('times', [])):
                print(f"  Time {i+1}: {time_entry}")
                
            # Look for empty times array which indicates parsing failure
            if not event_data.get('times'):
                print("⚠️  No times found - possible parsing issue!")
                
                # Let's examine the raw HTML to see the time format
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                event_display = soup.find('div', class_='event-display')
                if event_display:
                    rows = event_display.find_all('div', class_='row')
                    for row in rows:
                        cols = row.find_all('div')
                        if len(cols) >= 2:
                            label = cols[0].get_text(strip=True).lower()
                            if 'dates and times' in label:
                                raw_time = cols[1].get_text(strip=True)
                                print(f"  Raw time text: '{raw_time}'")
                                
                                # Test our parser on this raw text
                                from event_parser import parse_time_string
                                parsed = parse_time_string(raw_time)
                                print(f"  Parsed result: {parsed}")
                
        except Exception as e:
            print(f"Error testing event {event_id}: {e}")

if __name__ == "__main__":
    test_real_events_with_problematic_times()

