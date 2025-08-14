# Burning Man Events Data Collector

A simple Python script to collect event data from the Burning Man Playa Events website.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Collect All Events
```bash
python collect_events.py
```

### Test with Limited Events
```bash
python collect_events.py --max-events 10 --output test_events.json
```

### Options
- `--output FILENAME`: Specify output JSON file (default: events.json)
- `--max-events N`: Limit collection to N events (useful for testing)

## Output Format

The script generates a JSON file with events in this format:

```json
[
  {
    "id": "51620",
    "times": [
      {
        "date": "08/24/2025",
        "start_time": "00:00", 
        "end_time": "00:00"
      }
    ],
    "type": "Other",
    "camp": "Camp BUI",
    "campurl": "https://www.campbui.org",
    "location": "Camp BUI", 
    "description": "Stop by and get yourself a tattoo stamp."
  }
]
```

## Files

- `collect_events.py`: Main data collection script
- `event_parser.py`: HTML parsing utilities
- `requirements.txt`: Python dependencies
- `samples/`: Sample HTML files for development
- `sample_downloader.py`: Utility to download sample files
- `analyze_structure.py`: Utility to analyze HTML structure

## Notes

- The script includes request delays to be respectful to the server
- Progress is shown every 50 events during collection
- Failed requests are logged but don't stop the collection process
- All data is collected locally - no server or Docker required

## Camps Collector

### Collect All Camps
```bash
python collect_camps.py
```

### Test Camps With Limited Pages
```bash
python collect_camps.py --max-pages 2 --output test_camps.json
```

### Options (Camps)
- `--output FILENAME`: Specify output JSON file (default: camps.json)
- `--max-pages N`: Limit to the first N index pages (1–30)

### Output Format (Camps)
The camps script generates a JSON file with this format:

```json
[
  {
    "name": "Zendo Project 9:00",
    "website": "https://zendoproject.org/",
    "location": "9:00 & C",
    "description": "The Zendo Project - Psychedelic Care & Emotional Support …"
  }
]
```

### Files Added
- `collect_camps.py`: Camps data collection script
- `camp_parser.py`: Camp directory parsing utilities
 
### Normalize Camp Locations
Add a `normalized_location` field to each camp entry with canonical format `<Ring> & <Clock>`.

```bash
python normalize_camps_locations.py --input camps.json --output camps_normalized.json
```

Rules:
- "Esplanade" is distinct from the ring letter "E"
- Letters A..K represent street rings
- Clock is the H:MM position (e.g., 7:25, 9:00)
- Examples: "Gobsmack & 7:25" -> "G & 7:25"; "Esplanade & 7:45" -> "Esplanade & 7:45"; "9:00 & J" -> "J & 9:00"

## Art Collector

### Collect All Artworks
```bash
python collect_arts.py
```

### Test Art With Limited Pages
```bash
python collect_arts.py --max-pages 2 --output test_arts.json
```

### Options (Art)
- `--output FILENAME`: Specify output JSON file (default: arts.json)
- `--max-pages N`: Limit to the first N index pages (1–8)

### Output Format (Art)
The art script generates a JSON file with this format:

```json
[
  {
    "name": "A Basic Bench",
    "location": "10:52 1800', Open Playa",
    "description": "A Basic Bench is constructed out of 4\" curved steel …"
  }
]
```

### Files Added
- `collect_arts.py`: Artwork data collection script
- `art_parser.py`: Artwork directory parsing utilities
