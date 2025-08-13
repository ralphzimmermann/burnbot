import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { addFavorite as apiAddFavorite, removeFavorite as apiRemoveFavorite, listFavorites as apiListFavorites, me as apiMe } from './api'

const FavoritesContext = createContext(null)

export function FavoritesProvider({ children }) {
  const [favoriteEvents, setFavoriteEvents] = useState([])
  const [isAuthed, setIsAuthed] = useState(false)

  // Keep a quick lookup Set of IDs for fast checks
  const favoriteIdsSet = useMemo(() => {
    return new Set(favoriteEvents.map((ev) => ev.id))
  }, [favoriteEvents])

  const refreshFavorites = useCallback(async () => {
    try {
      await apiMe()
      setIsAuthed(true)
    } catch {
      setIsAuthed(false)
      setFavoriteEvents([])
      return
    }
    try {
      const favs = await apiListFavorites()
      setFavoriteEvents(Array.isArray(favs) ? favs : [])
    } catch {
      // If fetching fails, keep current state rather than clearing
    }
  }, [])

  // On mount, check session and load favorites if logged in
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      if (cancelled) return
      await refreshFavorites()
    })()
    return () => {
      cancelled = true
    }
  }, [refreshFavorites])

  const addFavorite = useCallback(async (event) => {
    if (!event || !event.id) return
    try {
      await apiAddFavorite(event)
      setFavoriteEvents((prev) => {
        if (prev.some((ev) => ev.id === event.id)) return prev
        return [...prev, event]
      })
    } catch {
      // ignore
    }
  }, [])

  const removeFavorite = useCallback(async (eventId) => {
    if (!eventId) return
    try {
      await apiRemoveFavorite(eventId)
    } finally {
      setFavoriteEvents((prev) => prev.filter((ev) => ev.id !== eventId))
    }
  }, [])

  const toggleFavorite = useCallback(async (event) => {
    if (!event || !event.id) return
    const exists = favoriteIdsSet.has(event.id)
    try {
      if (exists) {
        await apiRemoveFavorite(event.id)
        setFavoriteEvents((prev) => prev.filter((ev) => ev.id !== event.id))
      } else {
        await apiAddFavorite(event)
        setFavoriteEvents((prev) => (prev.some((ev) => ev.id === event.id) ? prev : [...prev, event]))
      }
    } catch {
      // noop
    }
  }, [favoriteIdsSet])

  const addManyFavorites = useCallback(async (events) => {
    if (!Array.isArray(events) || events.length === 0) return
    // Filter out ones we already have locally to avoid redundant requests
    const toAdd = events.filter((ev) => ev && ev.id && !favoriteIdsSet.has(ev.id))
    if (toAdd.length === 0) return

    // Fire requests concurrently; tolerate duplicates or failures
    const results = await Promise.allSettled(toAdd.map((ev) => apiAddFavorite(ev)))

    // If any request failed due to auth, reflect that
    const hadAuthFailure = results.some((r) => r.status === 'rejected' && r.reason?.response?.status === 401)
    if (hadAuthFailure) {
      setIsAuthed(false)
      setFavoriteEvents([])
      return
    }

    // Merge successfully added ones into local state
    const successfulIds = new Set(
      results
        .map((r, idx) => (r.status === 'fulfilled' ? toAdd[idx].id : null))
        .filter(Boolean)
    )

    if (successfulIds.size === 0) return

    setFavoriteEvents((prev) => {
      const existingIds = new Set(prev.map((ev) => ev.id))
      const newlyAdded = toAdd.filter((ev) => successfulIds.has(ev.id) && !existingIds.has(ev.id))
      if (newlyAdded.length === 0) return prev
      return [...prev, ...newlyAdded]
    })
  }, [favoriteIdsSet])

  const value = useMemo(() => ({
    favorites: favoriteEvents,
    favoriteIdsSet,
    isAuthed,
    refreshFavorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    addManyFavorites,
  }), [favoriteEvents, favoriteIdsSet, isAuthed, refreshFavorites, addFavorite, removeFavorite, toggleFavorite, addManyFavorites])

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext)
  if (!ctx) throw new Error('useFavorites must be used within <FavoritesProvider>')
  return ctx
}


