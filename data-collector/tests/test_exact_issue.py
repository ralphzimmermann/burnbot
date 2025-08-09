#!/usr/bin/env python3
"""
Test the exact time string that's failing.
"""

from event_parser import parse_time_string

def test_exact_failing_string():
    """Test the exact time string from the failing event."""
    
    # The exact string from the failing event
    time_str = """Sunday, August 24th, 2025, 12 AM –
             2 AM"""
    
    print("=== Testing Exact Failing String ===")
    print(f"Input: {repr(time_str)}")
    print(f"Input formatted:\n'{time_str}'")
    
    result = parse_time_string(time_str)
    print(f"Result: {result}")
    
    # Let's also test a cleaned version
    cleaned = " ".join(time_str.split())
    print(f"\nCleaned: {repr(cleaned)}")
    result_cleaned = parse_time_string(cleaned)
    print(f"Result cleaned: {result_cleaned}")

if __name__ == "__main__":
    test_exact_failing_string()

