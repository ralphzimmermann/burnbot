import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { me as apiMe, login as apiLogin, register as apiRegister, logout as apiLogout } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Bootstrap session
  useEffect(() => {
    let cancelled = false
    async function bootstrap() {
      try {
        const me = await apiMe()
        if (!cancelled) {
          if (me && typeof me.username === 'string' && me.username.length > 0 && typeof me.id === 'number') {
            setUser(me)
          } else {
            setUser(null)
          }
        }
      } catch {
        if (!cancelled) setUser(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    bootstrap()
    return () => { cancelled = true }
  }, [])

  const login = useCallback(async (username, password) => {
    const data = await apiLogin(username, password)
    if (data && typeof data.username === 'string') setUser(data)
    else {
      // Fallback to /auth/me in case backend didn't return full payload
      try { const me = await apiMe(); setUser(me && me.username ? me : null) } catch { setUser(null) }
    }
    return data
  }, [])

  const register = useCallback(async (username, password) => {
    const data = await apiRegister(username, password)
    if (data && typeof data.username === 'string') setUser(data)
    else {
      try { const me = await apiMe(); setUser(me && me.username ? me : null) } catch { setUser(null) }
    }
    return data
  }, [])

  const logout = useCallback(async () => {
    try { await apiLogout() } catch { /* ignore */ }
    setUser(null)
  }, [])

  const value = useMemo(() => ({
    user,
    loading,
    login,
    register,
    logout,
  }), [user, loading, login, register, logout])

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}


