## Auth and Favorites (Phase 1.1)

Minimal username/password auth with cookie sessions. Favorites are stored per user in SQLite.

### Backend

- Session cookies via FastAPI `SessionMiddleware` (set `SECRET_KEY`).
- SQLite using SQLAlchemy. Default path: `website/backend/data/app.db`. In Docker it's `/data/app.db` mounted on a named volume.
- Endpoints:
  - `POST /auth/register { username, password }` → creates user, logs in
  - `POST /auth/login { username, password }` → logs in
  - `POST /auth/logout`
  - `GET /auth/me` → current user
  - `GET /favorites` → list favorites
  - `POST /favorites` → add favorite (send full event JSON)
  - `DELETE /favorites/{event_id}` → remove favorite

### Frontend

- `AuthProvider` manages session (`/auth/me`, login/register/logout) and exposes `user`.
- `FavoritesProvider` loads and persists favorites on the server for the current session.
- `AuthWidget` in the header provides simple login/register/logout.

### Docker

- `docker-compose.yml` defines a named volume `eventguide-db` mounted at `/data` with `SQLITE_DB_PATH=/data/app.db`.

### Env vars

- `SECRET_KEY` (session signing). In Docker, defaults to a dev value if not provided.
- `SQLITE_DB_PATH` (optional) to override database path.


