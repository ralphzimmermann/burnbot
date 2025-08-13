import React, { useEffect, useMemo, useState } from 'react'
import Tabs from '../components/Tabs.jsx'
import { useFavorites } from '../services/favorites.jsx'

const WEEK_DAYS = [
  { label: 'Sun 8/24', dateStr: '08/24/2025' },
  { label: 'Mon 8/25', dateStr: '08/25/2025' },
  { label: 'Tue 8/26', dateStr: '08/26/2025' },
  { label: 'Wed 8/27', dateStr: '08/27/2025' },
  { label: 'Thu 8/28', dateStr: '08/28/2025' },
  { label: 'Fri 8/29', dateStr: '08/29/2025' },
  { label: 'Sat 8/30', dateStr: '08/30/2025' },
]

function timeToMinutes(t) {
  // Expecting HH:MM (24h). Fallback to 0 if missing/invalid.
  if (!t || typeof t !== 'string') return 0
  const parts = t.split(':')
  const hours = Number(parts[0] || 0)
  const minutes = Number(parts[1] || 0)
  if (Number.isNaN(hours) || Number.isNaN(minutes)) return 0
  return hours * 60 + minutes
}

export default function WeekView() {
  const { favorites, refreshFavorites } = useFavorites()
  const [expandedKeys, setExpandedKeys] = useState(() => new Set())

  // Ensure latest favorites when arriving on this tab
  useEffect(() => {
    refreshFavorites()
  }, [refreshFavorites])

  const byDate = useMemo(() => {
    const map = new Map(WEEK_DAYS.map((d) => [d.dateStr, []]))
    for (const ev of favorites) {
      if (!Array.isArray(ev?.times)) continue
      for (const t of ev.times) {
        if (!t?.date) continue
        if (!map.has(t.date)) continue // only this festival week
        map.get(t.date).push({
          key: `${ev.id}|${t.date}|${t.start_time}|${t.end_time}`,
          event: ev,
          time: t,
        })
      }
    }
    // Sort each day by start time
    for (const [dateStr, items] of map.entries()) {
      items.sort((a, b) => timeToMinutes(a.time?.start_time) - timeToMinutes(b.time?.start_time))
      map.set(dateStr, items)
    }
    return map
  }, [favorites])

  function toggle(key) {
    setExpandedKeys((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  return (
    <div className="space-y-6">
      <Tabs />
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Week View (Favorites)</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
        {WEEK_DAYS.map((day) => {
          const items = byDate.get(day.dateStr) || []
          return (
            <div key={day.dateStr} className="bg-base-100 border rounded">
              <div className="px-3 py-2 border-b font-medium">
                <button
                  type="button"
                  className="link link-hover"
                  onClick={() => {
                    const url = `/print/day/${encodeURIComponent(day.dateStr)}`
                    window.open(url, '_blank', 'noopener,noreferrer')
                  }}
                  title="Open printable day view"
                >
                  {day.label}
                </button>
              </div>
              <div className="p-2 space-y-2">
                {items.length === 0 && (
                  <div className="text-sm opacity-60">No favorites</div>
                )}
                {items.map(({ key, event, time }) => {
                  const isOpen = expandedKeys.has(key)
                  const hasCampLink = Boolean(event.campurl)
                  return (
                    <div key={key} className="card bg-base-100 card-border border-base-300">
                      <button
                        type="button"
                        onClick={() => toggle(key)}
                        className="text-left w-full p-3 hover:bg-base-200 transition-colors"
                      >
                        <div className="text-sm font-semibold line-clamp-2">{event.title || 'Untitled event'}</div>
                        <div className="mt-1 text-xs opacity-80">
                          {time?.start_time || '--:--'} – {time?.end_time || '--:--'}
                        </div>
                        <div className="mt-1 text-xs">
                          {hasCampLink ? (
                            <a href={event.campurl} target="_blank" rel="noreferrer" className="link link-primary">
                              {event.camp}
                            </a>
                          ) : (
                            <span className="opacity-80">{event.camp}</span>
                          )}
                        </div>
                      </button>
                      {isOpen && (
                        <div className="px-3 pb-3 text-sm leading-6">
                          {event.description}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}


