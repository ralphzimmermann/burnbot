import axios from 'axios'

// Default to same-origin in production; override via VITE_API_BASE_URL for dev
const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function recommend(query, maxResults = 30) {
  const { data } = await axios.post(`${BASE_URL}/recommend`, {
    query,
    max_results: maxResults,
  })
  return data
}

export async function getEvent(eventId) {
  const { data } = await axios.get(`${BASE_URL}/events/${eventId}`)
  return data
}


