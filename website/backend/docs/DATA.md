# Backend Data Layout

- `data/events.json` → symlink to repository `data/events.json`
- `data/embeddings.npy` → NumPy array with shape `(num_events, dim)`

Embeddings are L2-normalized for cosine similarity and indexed with FAISS `IndexFlatIP`.

## API Shapes

- POST `/recommend`

  Request:

  - `query`: string
  - `max_results`: number (default 30)

  Response:

  - `events`: Array of `Event`
  - `query`: The original query string
  - `processing_time_ms`: server processing time in milliseconds
  - `rationale` (optional): 1–2 sentence explanation for why the results match the query (present when LLM reranking is enabled)

### Event shape

The `Event` model supports optional geographic coordinates:

- `latitude`: number | null
- `longitude`: number | null

These are read from `data/events.json` when present and are included in favorites responses for mobile map features.

