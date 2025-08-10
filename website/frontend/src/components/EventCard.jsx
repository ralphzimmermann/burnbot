import React from 'react'
export default function EventCard({ event }) {
  return (
    <div className="card bg-base-100 shadow-sm border">
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


