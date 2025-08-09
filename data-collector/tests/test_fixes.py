#!/usr/bin/env python3
"""
Test the fixes for time parsing issues.
"""

from event_parser import convert_to_24_hour, parse_time_string
import requests
from event_parser import extract_event_data

def test_convert_fixes():
    """Test the improved convert_to_24_hour function."""
    
    test_cases = [
        "9 PM", "1 AM", "12 AM", "2 AM", "11 AM", "1 PM",
        "11:45 PM", "12:00 AM", "6:30 PM", "10:15 AM"
    ]
    
    print("=== Testing Improved convert_to_24_hour ===")
    
    for time_str in test_cases:
        result = convert_to_24_hour(time_str)
        print(f"'{time_str}' -> '{result}'")

def test_problematic_strings():
    """Test the original problematic strings."""
    
    test_cases = [
        "Monday, August 25th, 2025, 9 PM – 1 AM",
        "Sunday, August 24th, 2025, 12 AM – 2 AM", 
        "Tuesday, August 26th, 2025, 11 AM – 1 PM"
    ]
    
    print("\n=== Testing Original Problematic Strings ===")
    
    for time_str in test_cases:
        result = parse_time_string(time_str)
        print(f"'{time_str}' -> {result}")

def test_real_event_50893():
    """Test the real event that was failing."""
    
    print("\n=== Testing Real Event 50893 (Was Failing) ===")
    
    try:
        url = "https://playaevents.burningman.org/2025/playa_event/50893/"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        event_data = extract_event_data(response.text, "50893")
        
        print(f"Event times found: {len(event_data.get('times', []))}")
        for i, time_entry in enumerate(event_data.get('times', [])):
            print(f"  Time {i+1}: {time_entry}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_convert_fixes()
    test_problematic_strings() 
    test_real_event_50893()

