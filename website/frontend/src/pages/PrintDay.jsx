import React, { useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useFavorites } from '../services/favorites.jsx'

function timeToMinutes(t) {
  if (!t || typeof t !== 'string') return 0
  const parts = t.split(':')
  const hours = Number(parts[0] || 0)
  const minutes = Number(parts[1] || 0)
  if (Number.isNaN(hours) || Number.isNaN(minutes)) return 0
  return hours * 60 + minutes
}

export default function PrintDay() {
  const { date } = useParams()
  const { favorites, refreshFavorites } = useFavorites()

  // Ensure favorites are loaded when this page opens in a new tab
  useEffect(() => {
    refreshFavorites()
  }, [refreshFavorites])

  const items = useMemo(() => {
    const results = []
    for (const ev of favorites) {
      if (!Array.isArray(ev?.times)) continue
      for (const t of ev.times) {
        if (t?.date === date) {
          results.push({ key: `${ev.id}|${t.date}|${t.start_time}|${t.end_time}`, event: ev, time: t })
        }
      }
    }
    results.sort((a, b) => timeToMinutes(a.time?.start_time) - timeToMinutes(b.time?.start_time))
    return results
  }, [favorites, date])

  const displayDate = useMemo(() => {
    if (!date || typeof date !== 'string') return String(date || '')
    // Expect MM/DD/YYYY
    const [mm, dd, yyyy] = date.split('/')
    const month = Number(mm)
    const day = Number(dd)
    const year = Number(yyyy)
    if (!month || !day || !year) return date
    const d = new Date(Date.UTC(year, month - 1, day))
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    const w = weekdays[d.getUTCDay()]
    return `${w} ${month}/${day}/${year}`
  }, [date])

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      {/* Screen-only controls */}
      <div className="flex items-center justify-between gap-2 mb-6 print:hidden">
        <h1 className="text-xl font-semibold">Print view for {displayDate}</h1>
        <div className="flex items-center gap-2">
          <button className="btn btn-sm" onClick={() => window.print()}>Print</button>
          <Link to="/week" className="btn btn-sm btn-outline">Back to week</Link>
        </div>
      </div>

      {/* Printable content */}
      <div className="space-y-5">
        <div className="print:mb-6">
          <h1 className="text-2xl font-semibold mb-2">{displayDate}</h1>
          <p className="text-sm opacity-70">Favorites scheduled for this day</p>
        </div>

        {items.length === 0 && (
          <div className="text-sm opacity-80">No favorites on this day.</div>
        )}

        {items.map(({ key, event, time }) => (
          <article key={key} className="break-inside-avoid">
            <h2 className="text-lg font-semibold">{event.title || 'Untitled event'}</h2>
            <div className="mt-1 text-sm opacity-80">
              {time?.start_time || '--:--'} – {time?.end_time || '--:--'}
            </div>
            <div className="mt-1 text-sm">
              <span className="opacity-90">{event.location}</span>
            </div>
            <div className="mt-1 text-sm">
              {event.campurl ? (
                <a href={event.campurl} target="_blank" rel="noreferrer" className="link link-primary">
                  {event.camp}
                </a>
              ) : (
                <span className="opacity-80">{event.camp}</span>
              )}
            </div>
            <div className="mt-3 text-sm leading-6 whitespace-pre-line">
              {event.description}
            </div>
          </article>
        ))}
      </div>

      <style>{`
        @media print {
          /* Use tighter margins in print */
          @page { margin: 12mm; }
          /* Avoid page breaks inside items */
          article { page-break-inside: avoid; }
          /* Make links appear as plain text */
          a { color: inherit; text-decoration: none; }
        }
      `}</style>
    </div>
  )
}


