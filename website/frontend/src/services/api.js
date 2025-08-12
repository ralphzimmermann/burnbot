import axios from 'axios'

// In dev, use Vite proxy at /api to avoid cross-site cookies. In prod, same-origin.
// Force same-origin in production; use /api proxy only in dev
let BASE_URL = import.meta.env.DEV ? '/api' : ''
// Safety: if a stale build ever inlines localhost while deployed on a remote host, ignore it
if (!import.meta.env.DEV && typeof window !== 'undefined') {
  const origin = window.location.origin
  if (origin && !origin.includes('localhost') && (import.meta.env.VITE_API_BASE_URL?.includes('localhost') || import.meta.env.VITE_API_BASE_URL?.includes('127.0.0.1'))) {
    BASE_URL = ''
  }
}

// Send cookies for session auth
const http = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
})

export async function recommend(query, maxResults = 30) {
  const { data } = await http.post(`/recommend`, {
    query,
    max_results: maxResults,
  })
  return data
}

export async function getEvent(eventId) {
  const { data } = await http.get(`/events/${eventId}`)
  return data
}

// Auth
export async function register(username, password) {
  const { data } = await http.post('/auth/register', { username, password })
  return data
}

export async function login(username, password) {
  const { data } = await http.post('/auth/login', { username, password })
  return data
}

export async function logout() {
  const { data } = await http.post('/auth/logout')
  return data
}

export async function me() {
  const { data } = await http.get('/auth/me')
  return data
}

// Favorites
export async function listFavorites() {
  const { data } = await http.get('/favorites')
  return data
}

export async function addFavorite(event) {
  const { data } = await http.post('/favorites', event)
  return data
}

export async function removeFavorite(eventId) {
  const { data } = await http.delete(`/favorites/${encodeURIComponent(eventId)}`)
  return data
}


