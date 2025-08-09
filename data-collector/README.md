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
