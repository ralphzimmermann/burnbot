#!/usr/bin/env python3
"""
Test the fix for the unconverted time issue.
"""

from event_parser import convert_to_24_hour, parse_time_string

def test_convert_fix():
    """Test the improved convert function with problematic cases."""
    
    test_cases = [
        # Previously problematic cases
        "2:00PM",
        "4:30PM", 
        "4:30AM",
        "12PM",
        "12AM",
        # Cases that should still work
        "2:00 PM",
        "4:30 PM",
        "11:45 PM",
        "9 AM",
        # Already 24-hour format
        "14:00",
        "16:30"
    ]
    
    print("=== Testing Improved convert_to_24_hour ===")
    
    for time_str in test_cases:
        result = convert_to_24_hour(time_str)
        print(f"'{time_str}' -> '{result}'")

def test_edge_cases_fixed():
    """Test the edge cases that were failing before."""
    
    edge_cases = [
        "Tuesday, August 26th, 2025, 2:00PM – 4:30PM",     # no space before PM
        "Tuesday, August 26th, 2025, 14:00 – 4:30PM",      # mixed format, no space
        "Tuesday, August 26th, 2025, 2PM – 4:30PM",        # no minutes, no space
    ]
    
    print("\n=== Testing Previously Failing Edge Cases ===")
    
    for i, test_str in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: {repr(test_str)}")
        result = parse_time_string(test_str)
        print(f"Result: {result}")
        
        # Check for unconverted times
        for time_entry in result:
            start = time_entry.get('start_time', '')
            end = time_entry.get('end_time', '')
            if 'PM' in start or 'AM' in start or 'PM' in end or 'AM' in end:
                print(f"  ⚠️  STILL UNCONVERTED: start='{start}', end='{end}'")
            else:
                print(f"  ✅ PROPERLY CONVERTED: start='{start}', end='{end}'")

if __name__ == "__main__":
    test_convert_fix()
    test_edge_cases_fixed()

