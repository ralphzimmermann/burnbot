### Temporal query filters (weekday and time-of-day)

The recommendation backend supports extracting temporal intent from free-text queries and filtering results accordingly. This allows queries like "What is going on on Thursday night for dancing?" to prioritize events occurring Thursday night.

Implementation scope:
- Weekday detection in query (no UI filters yet) and post-search filtering of candidates.
- Time-of-day buckets consistent across embedding text and filtering logic.

Weekday tokens recognized:
- Monday (mon), Tuesday (tue, tues), Wednesday (wed), Thursday (thu, thur, thurs), Friday (fri), Saturday (sat), Sunday (sun)

Time-of-day buckets:
- morning: 05:00–11:59
- afternoon: 12:00–16:59
- evening: 17:00–20:59
- night: 21:00–04:59 (wraps midnight)

Additional synonyms: "late night", "latenight", "tonight" map to night.

Filter behavior:
- If a weekday is present, at least one occurrence of an event must fall on that weekday.
- If a time-of-day is present, at least one occurrence must overlap that bucket.
- If both are present, a single occurrence must satisfy both.
- Progressive fallback: if no events match both, we try weekday-only, then time-of-day-only, finally return the original candidates.

Embedding text enrichment:
- Event embedding text now includes summarized weekday names (e.g., "Days: Thursday, Friday") and time buckets (e.g., "Times: evening, night").
- To leverage this in the vector search itself, regenerate embeddings (`embeddings.npy`). The system works without regeneration because filtering is applied after vector search, but quality may improve with updated embeddings.

Locations in code:
- Weekday/time buckets summarization for embeddings: `website/backend/app/services/embedding_service.py`
- Query parsing and candidate filtering: `website/backend/app/services/recommendation_service.py`


