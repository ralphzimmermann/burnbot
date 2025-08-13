# Favorites (Frontend)

Users can mark events as favorites. Favorites are stored per user on the backend and loaded via the API using cookie-based sessions.

## Storage
- Backend SQLite via API, keyed by user session.

## API
- `website/frontend/src/services/favorites.jsx`
  - `<FavoritesProvider>`: Context provider wrapping the app.
  - `useFavorites()` returns:
    - `favorites`: array of favorite events
    - `favoriteIdsSet`: `Set<string>` for O(1) lookups
    - `isAuthed`: boolean
    - `refreshFavorites()`: re-fetch from server
    - `addFavorite(event)`, `removeFavorite(eventId)`, `toggleFavorite(event)`, `addManyFavorites(events)`
      - `addManyFavorites(events)` posts each new event concurrently to the backend using the same endpoint as single add. Already-favorited events are skipped client-side. Auth failures clear local favorites and mark `isAuthed=false`.

## UI integration
- Heart toggle on each `EventCard` top-right.
- "Add all to favorites" button in `Results` header when there are search results.
- Tabs: `Search`, `Favorites`, `Week View` (`website/frontend/src/components/Tabs.jsx`).
- `Favorites` page (`/favorites`) lists saved events.
- `Week View` (`/week`) organizes favorites by festival day/time.
  - Type filter: a dropdown to filter by event `type` with emoji labels.
    - Options: "All Events ✨" (default), "Arts & Crafts 🎨", "Beverages 🍹", "Class/Workshop 🧑‍🏫", "Food 🍽️", "Kids Activities 🎈", "Mature Audiences 🔞", "Music/Party 🪩", "Other ❓".
    - The emoji is shown before each event title in the list and in print.
  - Clicking a day label opens a printable view in a new tab. The current type filter is passed through.
  - Print route: `/print/day/:date` (date format `MM/DD/YYYY`). Optional query: `?type=<Type Name>`; omit or `All Events` to show all.
  - The print page lists all favorite events for that date, sorted by start time, honoring the `type` filter.

## Auto-refresh behavior
- To keep multiple browsers in sync, both `Favorites` and `Week View` call `refreshFavorites()` on mount. When switching tabs/routes to these pages, the latest server state is shown.

## Notes
- Event shape is stored as sent by the client; ensure `id` is stable.

