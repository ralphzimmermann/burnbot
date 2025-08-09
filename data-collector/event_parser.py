#!/usr/bin/env python3
"""
Event parser module for extracting event data from Burning Man event pages.
"""

import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


def extract_event_ids_from_index(html_content: str) -> List[str]:
    """
    Extract event IDs from an index page.
    
    Args:
        html_content: HTML content of the index page
        
    Returns:
        List of event IDs as strings
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all links to event pages
    event_links = soup.find_all('a', href=re.compile(r'/2025/playa_event/\d+/'))
    
    event_ids = []
    for link in event_links:
        href = link.get('href')
        match = re.search(r'/playa_event/(\d+)/', href)
        if match:
            event_ids.append(match.group(1))
    
    return event_ids


def parse_time_string(time_str: str) -> List[Dict[str, str]]:
    """
    Parse time strings like "Sunday, August 24th, 2025, 12 AM – 12 AM"
    
    Args:
        time_str: Raw time string from the website
        
    Returns:
        List of time dictionaries with date, start_time, end_time
    """
    times = []
    
    # Split by day names to handle multiple dates
    day_pattern = r'(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)'
    day_matches = re.split(day_pattern, time_str)
    
    # Rejoin each day with its data
    for i in range(1, len(day_matches), 2):
        if i + 1 < len(day_matches):
            day_name = day_matches[i]
            day_data = day_matches[i + 1]
            full_day_str = day_name + day_data
            
            # Parse individual day: "Sunday, August 24th, 2025, 12 AM – 12 AM"
            # Handle different dash types: – (en dash), — (em dash), - (hyphen)
            match = re.search(
                r'(\w+),\s*(\w+)\s+(\d+)\w*,\s*(\d{4}),\s*(.+?)\s*[–—-]\s*(.+?)(?=\w+day|$)',
                full_day_str
            )
            
            if match:
                day, month, date, year, start_time, end_time = match.groups()
                
                # Convert to MM/DD/YYYY format
                try:
                    date_obj = datetime.strptime(f"{month} {date} {year}", "%B %d %Y")
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                    
                    # Clean and format times
                    start_time = start_time.strip()
                    end_time = end_time.strip()
                    
                    # Convert to 24-hour format
                    start_24 = convert_to_24_hour(start_time)
                    end_24 = convert_to_24_hour(end_time)
                    
                    times.append({
                        "date": formatted_date,
                        "start_time": start_24,
                        "end_time": end_24
                    })
                except ValueError:
                    # Skip if date parsing fails
                    continue
    
    return times


def convert_to_24_hour(time_str: str) -> str:
    """Convert 12-hour time format to 24-hour format."""
    try:
        # Handle various time formats
        time_str = time_str.strip()
        
        # Handle formats like "11:45 PM", "9 PM", "12 AM", "11:45PM", "9PM"
        if 'AM' in time_str or 'PM' in time_str or 'am' in time_str or 'pm' in time_str:
            # Normalize by adding space before AM/PM if missing
            time_str = re.sub(r'(\d)(AM|PM|am|pm)', r'\1 \2', time_str)
            
            # Try various formats
            formats_to_try = [
                "%I:%M %p",  # "2:30 PM"
                "%I %p",     # "2 PM" 
                "%I:%M%p",   # "2:30PM" (fallback)
                "%I%p"       # "2PM" (fallback)
            ]
            
            for fmt in formats_to_try:
                try:
                    time_obj = datetime.strptime(time_str.upper(), fmt)
                    return time_obj.strftime("%H:%M")
                except ValueError:
                    continue
            
            # If still not parsed, try lowercase versions
            for fmt in formats_to_try:
                try:
                    time_obj = datetime.strptime(time_str.lower(), fmt.lower())
                    return time_obj.strftime("%H:%M")
                except ValueError:
                    continue
        
        # If no AM/PM, assume it's already in 24-hour format
        return time_str
        
    except ValueError:
        # Return original if parsing fails
        return time_str


def extract_event_data(html_content: str, event_id: str) -> Dict:
    """
    Extract event data from an event page.
    
    Args:
        html_content: HTML content of the event page
        event_id: Event ID for reference
        
    Returns:
        Dictionary with event data matching the required structure
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    event_data = {
        "id": event_id,
        "title": "",
        "times": [],
        "type": "",
        "camp": "",
        "campurl": "",
        "location": "",
        "description": ""
    }
    
    # Find the event display container
    event_display = soup.find('div', class_='event-display')
    if not event_display:
        return event_data
    
    # Title: try common headings inside the event display, then page title
    title_tag = event_display.find(['h1', 'h2']) or soup.find('h1') or soup.find('h2')
    if title_tag:
        event_data["title"] = title_tag.get_text(strip=True)
    else:
        # Fallback to <title> element, removing site branding if present
        page_title = soup.find('title').get_text(strip=True) if soup.find('title') else ""
        # Heuristic cleanup
        for sep in ["|", "-", "—"]:
            if sep in page_title:
                page_title = page_title.split(sep)[0].strip()
                break
        event_data["title"] = page_title

    # Find all data rows
    rows = event_display.find_all('div', class_='row')
    
    for row in rows:
        cols = row.find_all('div')
        if len(cols) >= 2:
            label = cols[0].get_text(strip=True).lower()
            value_element = cols[1]
            
            if 'dates and times' in label or 'date and time' in label:
                # Extract times
                time_text = value_element.get_text(strip=True)
                event_data["times"] = parse_time_string(time_text)
                
            elif 'type' in label:
                # Extract type
                event_data["type"] = value_element.get_text(strip=True)
                
            elif 'located at camp' in label:
                # Extract camp name and URL
                camp_link = value_element.find('a')
                if camp_link:
                    event_data["camp"] = camp_link.get_text(strip=True)
                    event_data["campurl"] = camp_link.get('href', '')
                else:
                    event_data["camp"] = value_element.get_text(strip=True)
                    
            elif 'location' in label and 'camp' not in label:
                # Extract location (but not "Located at Camp")
                event_data["location"] = value_element.get_text(strip=True)
                
            elif 'description' in label:
                # Extract description
                event_data["description"] = value_element.get_text(strip=True)
    
    return event_data


if __name__ == "__main__":
    # Test with sample files
    print("Testing parser with sample files...")
    
    # Test index parsing
    with open("samples/sample_index.html", "r", encoding="utf-8") as f:
        index_content = f.read()
    
    event_ids = extract_event_ids_from_index(index_content)
    print(f"Extracted {len(event_ids)} event IDs")
    print(f"First 5 IDs: {event_ids[:5]}")
    
    # Test event parsing
    with open("samples/sample_event.html", "r", encoding="utf-8") as f:
        event_content = f.read()
    
    event_data = extract_event_data(event_content, "51620")
    print(f"\nExtracted event data:")
    import json
    print(json.dumps(event_data, indent=2))
