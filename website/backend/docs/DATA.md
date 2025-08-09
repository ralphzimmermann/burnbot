# Backend Data Layout

- `data/events.json` → symlink to repository `data/events.json`
- `data/embeddings.npy` → NumPy array with shape `(num_events, dim)`

Embeddings are L2-normalized for cosine similarity and indexed with FAISS `IndexFlatIP`.

