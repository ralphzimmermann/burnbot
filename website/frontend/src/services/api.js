import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export async function recommend(query, maxResults = 5) {
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


