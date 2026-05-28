import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '@/utils/api'

interface User {
  id: number
  username: string
  email: string
  role: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('skillbridge_token')
    if (token) {
      checkAuth()
    } else {
      setLoading(false)
    }
  }, [])

  async function checkAuth() {
    try {
      const res = await api.get('/auth/me')
      setUser(res.data.user)
    } catch {
      localStorage.removeItem('skillbridge_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  async function login(email: string, password: string) {
    const res = await api.post('/auth/login', { email, password })
    if (res.data.token) {
      localStorage.setItem('skillbridge_token', res.data.token)
    }
    setUser(res.data.user)
  }

  async function register(username: string, email: string, password: string) {
    const res = await api.post('/auth/register', { username, email, password })
    if (res.data.token) {
      localStorage.setItem('skillbridge_token', res.data.token)
    }
    setUser(res.data.user)
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {
    } finally {
      localStorage.removeItem('skillbridge_token')
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
