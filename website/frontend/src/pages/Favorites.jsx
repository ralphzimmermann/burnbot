import React from 'react'
import { Link } from 'react-router-dom'
import { useFavorites } from '../services/favorites.jsx'
import EventCard from '../components/EventCard.jsx'
import Tabs from '../components/Tabs.jsx'

export default function Favorites() {
  const { favorites } = useFavorites()

  return (
    <div className="space-y-6">
      <Tabs />
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Your favorites</h2>
        <Link to="/" className="btn btn-sm btn-outline">New search</Link>
      </div>
      {favorites.length === 0 ? (
        <div className="text-sm opacity-80">No favorites yet. Browse events and tap the heart to add some.</div>
      ) : (
        <div className="grid gap-4">
          {favorites.map((ev) => (
            <EventCard key={ev.id} event={ev} />
          ))}
        </div>
      )}
    </div>
  )
}


