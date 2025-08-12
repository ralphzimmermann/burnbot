import React from 'react'
import { useFavorites } from '../services/favorites.jsx'

export default function EventCard({ event }) {
  const { favoriteIdsSet, toggleFavorite } = useFavorites()
  const isFavorite = favoriteIdsSet.has(event.id)
  return (
    <div className="card bg-base-100 shadow-sm border relative">
      <button
        type="button"
        aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        aria-pressed={isFavorite}
        onClick={() => toggleFavorite(event)}
        className="btn btn-ghost btn-xs absolute right-2 top-2"
      >
        {isFavorite ? (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-red-500">
            <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.24 14.584 2.25 11.903 2.25 8.904 2.25 6.366 4.204 4.5 6.75 4.5c1.652 0 3.134.937 3.855 2.299.721-1.362 2.203-2.299 3.855-2.299 2.546 0 4.5 1.867 4.5 4.404 0 2.999-1.99 5.68-4.739 8.603a25.18 25.18 0 01-4.244 3.17 15.247 15.247 0 01-.383.218l-.022.012-.007.003-.003.002a.75.75 0 01-.69 0l-.003-.002z" />
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 opacity-70">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.086-4.5-4.66-4.5-1.528 0-2.986.757-3.84 1.986-.854-1.229-2.312-1.986-3.84-1.986C5.086 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
        )}
      </button>
      <div className="card-body p-4">
        <h3 className="card-title text-base">{event.title || 'Untitled event'}</h3>
        <div className="mb-2 flex items-center justify-between">
          <span className="badge badge-primary badge-outline">
            {event.type}
          </span>
          {event.campurl ? (
            <a
              href={event.campurl}
              target="_blank"
              rel="noreferrer"
              className="link link-primary"
            >
              {event.camp}
            </a>
          ) : (
            <span className="opacity-80">{event.camp}</span>
          )}
        </div>
        <div className="mb-2 text-sm opacity-70">{event.location}</div>
        <div className="mb-3 space-y-0.5 text-sm">
          {event.times?.map((t, idx) => (
            <div key={idx} className="opacity-90">
              {t.date} · {t.start_time} – {t.end_time}
            </div>
          ))}
        </div>
        <p className="text-sm leading-6">{event.description}</p>
      </div>
    </div>
  )
}


