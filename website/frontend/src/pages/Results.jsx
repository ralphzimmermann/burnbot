import React, { useEffect, useMemo, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { recommend } from '../services/api.js'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import EventCard from '../components/EventCard.jsx'
import SearchForm from '../components/SearchForm.jsx'

export default function Results() {
  const { search } = useLocation()
  const params = useMemo(() => new URLSearchParams(search), [search])
  const q = params.get('q') || ''
  const k = Number(params.get('k') || 5)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function run() {
      if (!q.trim()) return
      setLoading(true)
      setError('')
      try {
        const res = await recommend(q, k)
        if (!cancelled) setData(res)
      } catch (e) {
        if (!cancelled) setError('Search failed. Please try again.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    run()
    return () => { cancelled = true }
  }, [q, k])

  return (
    <div className="space-y-6">
      <SearchForm initialQuery={q} initialMaxResults={k} showExamples={false} />
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Results</h2>
        <Link to="/" className="text-sm text-blue-600 hover:underline">New search</Link>
      </div>
      {loading && <LoadingSpinner />}
      {error && <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      {!loading && !error && data && data.events?.length === 0 && (
        <div className="text-sm text-gray-700">No results. Try another query.</div>
      )}
      {!loading && !error && data && data.events?.length > 0 && (
        <div className="grid gap-4">
          {data.events.map((ev) => (
            <EventCard key={ev.id} event={ev} />
          ))}
        </div>
      )}
    </div>
  )
}


