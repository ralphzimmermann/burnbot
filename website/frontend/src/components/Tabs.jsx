import React from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Tabs() {
  const { pathname } = useLocation()
  const isSearch = pathname === '/' || pathname.startsWith('/results')
  const isFavorites = pathname.startsWith('/favorites')
  const isWeek = pathname.startsWith('/week')

  return (
    <div className="tabs tabs-boxed w-full">
      <Link to="/" className={["tab", isSearch ? "tab-active" : ""].join(' ')}>
        Search
      </Link>
      <Link to="/favorites" className={["tab", isFavorites ? "tab-active" : ""].join(' ')}>
        Favorites
      </Link>
      <Link to="/week" className={["tab", isWeek ? "tab-active" : ""].join(' ')}>
        Week View
      </Link>
    </div>
  )
}


