import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const FAVORITES_STORAGE_KEY = 'bm-eventguide.favorites.v1'

function readFavoritesFromStorage() {
  try {
    const raw = localStorage.getItem(FAVORITES_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
  } catch {
    return []
  }
}

function writeFavoritesToStorage(favoriteEvents) {
  try {
    localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favoriteEvents))
  } catch {
    // ignore write errors
  }
}

const FavoritesContext = createContext(null)

export function FavoritesProvider({ children }) {
  const [favoriteEvents, setFavoriteEvents] = useState(() => readFavoritesFromStorage())

  // Keep a quick lookup Set of IDs for fast checks
  const favoriteIdsSet = useMemo(() => {
    return new Set(favoriteEvents.map((ev) => ev.id))
  }, [favoriteEvents])

  // Persist to localStorage when favorites change
  useEffect(() => {
    writeFavoritesToStorage(favoriteEvents)
  }, [favoriteEvents])

  // Sync across tabs/windows
  useEffect(() => {
    function onStorage(e) {
      if (e.key === FAVORITES_STORAGE_KEY) {
        setFavoriteEvents(readFavoritesFromStorage())
      }
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  const addFavorite = useCallback((event) => {
    if (!event || !event.id) return
    setFavoriteEvents((prev) => {
      if (prev.some((ev) => ev.id === event.id)) return prev
      return [...prev, event]
    })
  }, [])

  const removeFavorite = useCallback((eventId) => {
    if (!eventId) return
    setFavoriteEvents((prev) => prev.filter((ev) => ev.id !== eventId))
  }, [])

  const toggleFavorite = useCallback((event) => {
    if (!event || !event.id) return
    setFavoriteEvents((prev) => {
      const exists = prev.some((ev) => ev.id === event.id)
      if (exists) return prev.filter((ev) => ev.id !== event.id)
      return [...prev, event]
    })
  }, [])

  const addManyFavorites = useCallback((events) => {
    if (!Array.isArray(events) || events.length === 0) return
    setFavoriteEvents((prev) => {
      const existingIds = new Set(prev.map((ev) => ev.id))
      const toAdd = events.filter((ev) => ev && ev.id && !existingIds.has(ev.id))
      if (toAdd.length === 0) return prev
      return [...prev, ...toAdd]
    })
  }, [])

  const value = useMemo(() => ({
    favorites: favoriteEvents,
    favoriteIdsSet,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    addManyFavorites,
  }), [favoriteEvents, favoriteIdsSet, addFavorite, removeFavorite, toggleFavorite, addManyFavorites])

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext)
  if (!ctx) throw new Error('useFavorites must be used within <FavoritesProvider>')
  return ctx
}


