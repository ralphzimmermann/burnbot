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

  // On mount, check session and load favorites if logged in
  useEffect(() => {
    let cancelled = false
    async function bootstrap() {
      try {
        await apiMe()
        if (cancelled) return
        setIsAuthed(true)
        const favs = await apiListFavorites()
        if (!cancelled) setFavoriteEvents(Array.isArray(favs) ? favs : [])
      } catch {
        if (!cancelled) {
          setIsAuthed(false)
          setFavoriteEvents([])
        }
      }
    }
    bootstrap()
    return () => { cancelled = true }
  }, [])

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
    isAuthed,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    addManyFavorites,
  }), [favoriteEvents, favoriteIdsSet, isAuthed, addFavorite, removeFavorite, toggleFavorite, addManyFavorites])

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext)
  if (!ctx) throw new Error('useFavorites must be used within <FavoritesProvider>')
  return ctx
}


