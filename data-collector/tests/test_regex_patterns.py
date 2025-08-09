#!/usr/bin/env python3
"""
Test the regex pattern with various time formats to find edge cases.
"""

import re
from event_parser import parse_time_string

def test_problematic_patterns():
    """Test patterns that might cause the 4:30 PM issue."""
    
    test_cases = [
        # Various formats that might cause issues
        "Tuesday, August 26th, 2025, 2:00 PM – 4:30 PM",
        "Tuesday, August 26th, 2025, 14:00 – 4:30 PM", 
        "Tuesday, August 26th, 2025, 2 PM – 4:30 PM",
        "Tuesday, August 26th, 2025, 14:00 – 16:30",
        # Multi-day cases
        "Tuesday, August 26th, 2025, 2:00 PM – 4:30 PMWednesday, August 27th, 2025, 2:00 PM – 4:30 PM",
        # Mixed formats
        "Monday, August 25th, 2025, 14:00 – 4:30 PM",
    ]
    
    print("=== Testing Regex Patterns ===")
    
    for i, test_str in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_str}'")
        result = parse_time_string(test_str)
        print(f"Result: {result}")
        
        # Check for unconverted times
        for time_entry in result:
            start = time_entry.get('start_time', '')
            end = time_entry.get('end_time', '')
            if 'PM' in start or 'AM' in start or 'PM' in end or 'AM' in end:
                print(f"  ⚠️  UNCONVERTED: start='{start}', end='{end}'")

def debug_regex_extraction():
    """Debug the regex extraction step by step."""
    
    test_str = "Tuesday, August 26th, 2025, 14:00 – 4:30 PM"
    
    print("\n=== Debugging Regex Extraction ===")
    print(f"Input: '{test_str}'")
    
    # Test the main regex pattern
    pattern = r'(\w+),\s*(\w+)\s+(\d+)\w*,\s*(\d{4}),\s*(.+?)\s*–\s*(.+?)(?=\w+day|$)'
    match = re.search(pattern, test_str)
    
    if match:
        day, month, date, year, start_time, end_time = match.groups()
        print(f"Extracted:")
        print(f"  Day: '{day}'")
        print(f"  Month: '{month}'") 
        print(f"  Date: '{date}'")
        print(f"  Year: '{year}'")
        print(f"  Start time: '{start_time}' (repr: {repr(start_time)})")
        print(f"  End time: '{end_time}' (repr: {repr(end_time)})")
        
        # Test conversion
        from event_parser import convert_to_24_hour
        start_converted = convert_to_24_hour(start_time.strip())
        end_converted = convert_to_24_hour(end_time.strip())
        
        print(f"  Start converted: '{start_converted}'")
        print(f"  End converted: '{end_converted}'")
    else:
        print("No match found!")

if __name__ == "__main__":
    test_problematic_patterns()
    debug_regex_extraction()

