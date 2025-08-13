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

const TYPE_TO_EMOJI = {
  'All Events': '✨',
  'Arts & Crafts': '🎨',
  'Beverages': '🍹',
  'Class/Workshop': '🧑‍🏫',
  'Food': '🍽️',
  'Kids Activities': '🎈',
  'Mature Audiences': '🔞',
  'Music/Party': '🪩',
  'Other': '❓',
}

const TYPE_OPTIONS = [
  'All Events',
  'Arts & Crafts',
  'Beverages',
  'Class/Workshop',
  'Food',
  'Kids Activities',
  'Mature Audiences',
  'Music/Party',
  'Other',
]

function getTypeEmoji(type) {
  if (!type) return TYPE_TO_EMOJI['Other']
  return TYPE_TO_EMOJI[type] || TYPE_TO_EMOJI['Other']
}

function timeToMinutes(t) {
  // Expecting HH:MM (24h). Fallback to 0 if missing/invalid.
  if (!t || typeof t !== 'string') return 0
  const parts = t.split(':')
  const hours = Number(parts[0] || 0)
  const minutes = Number(parts[1] || 0)
  if (Number.isNaN(hours) || Number.isNaN(minutes)) return 0
  return hours * 60 + minutes
}

function getTimeBucketLabelFromMinutes(m) {
  const FOUR_AM = 4 * 60
  const EIGHT_AM = 8 * 60
  const ELEVEN_THIRTY = 11 * 60 + 30
  const THREE_PM = 15 * 60
  const SIX_PM = 18 * 60
  const NINE_PM = 21 * 60
  if (m < FOUR_AM) return 'Night'
  if (m < EIGHT_AM) return 'Early morning'
  if (m < ELEVEN_THIRTY) return 'Morning'
  if (m < THREE_PM) return 'Lunch'
  if (m < SIX_PM) return 'Afternoon'
  if (m < NINE_PM) return 'Evening'
  return 'Night'
}

export default function WeekView() {
  const { favorites, refreshFavorites } = useFavorites()
  const [expandedKeys, setExpandedKeys] = useState(() => new Set())
  const [typeFilter, setTypeFilter] = useState('All Events')

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
        // Filter by type if needed
        if (typeFilter !== 'All Events' && ev.type !== typeFilter) continue
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
  }, [favorites, typeFilter])

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
        <div className="flex items-center gap-2">
          <label className="text-sm opacity-70" htmlFor="typeFilter">Event type</label>
          <select
            id="typeFilter"
            className="select select-sm select-bordered"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {getTypeEmoji(opt)} {opt}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="overflow-x-auto">
        <div className="grid grid-flow-col auto-cols-[minmax(18rem,1fr)] md:auto-cols-[minmax(20rem,1fr)] gap-4">
          {WEEK_DAYS.map((day) => {
            const items = byDate.get(day.dateStr) || []
            return (
              <div key={day.dateStr} className="bg-base-100 border rounded">
              <div className="px-3 py-2 border-b font-medium">
                <button
                  type="button"
                  className="link link-hover"
                  onClick={() => {
                    const params = new URLSearchParams()
                    if (typeFilter && typeFilter !== 'All Events') params.set('type', typeFilter)
                    const qs = params.toString()
                    const url = `/print/day/${encodeURIComponent(day.dateStr)}${qs ? `?${qs}` : ''}`
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
                  {items.length > 0 && (() => {
                    const content = []
                    let lastLabel = null
                    let groupIdx = 0
                    for (const { key, event, time } of items) {
                      const startMinutes = timeToMinutes(time?.start_time)
                      const label = getTimeBucketLabelFromMinutes(startMinutes)
                      if (label !== lastLabel) {
                        content.push(
                          <div key={`div-${groupIdx++}-${label}`} className="divider text-xs uppercase font-bold opacity-70">
                            {label}
                          </div>
                        )
                        lastLabel = label
                      }
                      const isOpen = expandedKeys.has(key)
                      const hasCampLink = Boolean(event.campurl)
                      const emoji = getTypeEmoji(event.type)
                      content.push(
                        <div key={key} className="card bg-base-100 card-border border-base-300">
                          <button
                            type="button"
                            onClick={() => toggle(key)}
                            className="text-left w-full p-3 hover:bg-base-200 transition-colors"
                          >
                            <div className="text-sm font-semibold line-clamp-2">{emoji} {event.title || 'Untitled event'}</div>
                            <div className="mt-1 text-xs opacity-80">
                              {time?.start_time || '--:--'} – {time?.end_time || '--:--'}{Array.isArray(event?.times) && event.times.length > 1 ? <span className="ml-1" title="This event has multiple time slots">🔁</span> : null}
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
                    }
                    return content
                  })()}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}


