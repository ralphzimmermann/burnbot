# Favorites (Frontend)

This feature lets users mark events as favorites without authentication. Favorites are stored in `localStorage` and synchronized across tabs.

## Storage
- Key: `bm-eventguide.favorites.v1`
- Value: JSON array of event objects; deduplicated by `event.id`.

## API
- `src/services/favorites.jsx`
  - `<FavoritesProvider>`: Context provider wrapping the app.
  - `useFavorites()` returns:
    - `favorites`: array of favorite events
    - `favoriteIdsSet`: `Set<string>` for O(1) lookups
    - `addFavorite(event)`, `removeFavorite(eventId)`, `toggleFavorite(event)`, `addManyFavorites(events)`

## UI integration
- Heart toggle on each `EventCard` top-right: outline when not favorite, filled when favorite.
- "Add all to favorites" button in `Results` header when there are search results.
- Tabs beneath logo, above search: `Search` and `Favorites` (component `src/components/Tabs.jsx`).
- `Favorites` page at route `/favorites` lists saved events using `EventCard`.

## Files changed
- `src/services/favorites.js` (new)
- `src/components/EventCard.jsx` (heart toggle)
- `src/components/Tabs.jsx` (new)
- `src/pages/Home.jsx` (tabs added)
- `src/pages/Results.jsx` (tabs + add-all button)
- `src/pages/Favorites.jsx` (new)
- `src/main.jsx` (provider + route)

## Notes
- The provider persists on every change and listens to the `storage` event for cross-tab sync.
- Events are appended as-is; UI reads only fields it needs. If backend event shape changes, ensure `id` is stable.
- For future server sync, replace storage read/write with API calls inside the provider.

