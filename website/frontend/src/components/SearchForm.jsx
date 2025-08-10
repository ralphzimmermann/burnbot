import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const EXAMPLES = [
  'I love electronic music and want to dance all night',
  'Looking for creative workshops where I can make something',
  'Want to try unique food experiences and meet people',
  'Interested in spiritual or wellness activities',
  'Comedy shows or entertaining performances',
]

export default function SearchForm({ initialQuery = '', initialMaxResults = 5, showExamples = true }) {
  const [query, setQuery] = useState(initialQuery)
  const [maxResults, setMaxResults] = useState(initialMaxResults)
  const navigate = useNavigate()

  const onSubmit = (e) => {
    e.preventDefault()
    if (!query.trim()) return
    const clamped = Math.min(Math.max(1, Number(maxResults) || Number(initialMaxResults) || 5), 50)
    const params = new URLSearchParams({ q: query, k: String(clamped) })
    navigate(`/results?${params.toString()}`)
  }

  return (
    <div className="space-y-4">
      <form noValidate onSubmit={onSubmit} className="space-y-3">
        <textarea
          className="textarea textarea-bordered textarea-lg w-full"
          rows={3}
          placeholder="Describe what you're looking for..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="flex items-center gap-3">
          <label className="text-sm opacity-70">Max results</label>
          <input
            type="number"
            min={1}
            max={50}
            step={1}
            value={maxResults}
            onChange={(e) => setMaxResults(Number(e.target.value))}
            className="input input-bordered input-md w-24"
          />
          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </div>
      </form>
      {showExamples && (
        <div>
          <div className="mb-2 text-sm font-medium">Try examples:</div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => setQuery(ex)}
                className="badge badge-outline whitespace-normal normal-case"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}


