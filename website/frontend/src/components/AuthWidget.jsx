import React, { useState } from 'react'
import { useAuth } from '../services/auth.jsx'

export default function AuthWidget() {
  const { user, loading, login, register, logout } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [mode, setMode] = useState('login') // or 'register'

  if (loading) return null

  if (user) {
    return (
      <div className="flex items-center gap-3">
        <span className="text-sm opacity-80">Signed in as <strong>{user.username || 'Unknown'}</strong></span>
        <button className="btn btn-xs" onClick={logout}>Logout</button>
      </div>
    )
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      if (mode === 'login') await login(username, password)
      else await register(username, password)
      setUsername('')
      setPassword('')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed')
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex items-center gap-2">
      <input
        type="text"
        placeholder="username"
        className="input input-bordered input-xs"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
        minLength={3}
        maxLength={50}
      />
      <input
        type="password"
        placeholder="password"
        className="input input-bordered input-xs"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        minLength={6}
        maxLength={128}
      />
      <button type="submit" className="btn btn-xs">
        {mode === 'login' ? 'Login' : 'Register'}
      </button>
      <button type="button" className="btn btn-ghost btn-xs" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? 'Need account?' : 'Have account?'}
      </button>
      {error && <span className="text-error text-xs ml-2">{error}</span>}
    </form>
  )
}


