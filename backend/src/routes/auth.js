import { Router } from 'express'
import { randomBytes, scryptSync, timingSafeEqual } from 'crypto'
import { logger } from '../utils/logger.js'

export const authRouter = Router()

const users = []
const sessions = new Map()
const SESSION_DURATION = 24 * 60 * 60 * 1000

function createSession(user) {
  const token = randomBytes(32).toString('hex')
  sessions.set(token, { userId: user.id, expiresAt: Date.now() + SESSION_DURATION })
  return token
}

function hashPassword(password, salt) {
  const s = salt || randomBytes(16).toString('hex')
  const hash = scryptSync(password, s, 64).toString('hex')
  return salt ? { hash, salt } : `${hash}:${s}`
}

function verifyPassword(password, stored) {
  const [hash, salt] = String(stored).split(':')
  if (!hash || !salt) return false
  const candidate = scryptSync(password, salt, 64)
  const expected = Buffer.from(hash, 'hex')
  return candidate.length === expected.length && timingSafeEqual(candidate, expected)
}

authRouter.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body

    if (!username || !email || !password) {
      return res.status(400).json({ error: 'All fields are required' })
    }
    if (username.length < 2) {
      return res.status(400).json({ error: 'Name must be at least 2 characters' })
    }
    if (password.length < 6) {
      return res.status(400).json({ error: 'Password must be at least 6 characters' })
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' })
    }
    if (users.find(u => u.email === email)) {
      return res.status(400).json({ error: 'An account with this email already exists' })
    }

    const user = {
      id: users.length + 1,
      username,
      email,
      passwordHash: hashPassword(password),
      role: 'student',
      createdAt: new Date().toISOString(),
    }
    users.push(user)

    const token = createSession(user)
    logger.info(`User registered: ${email}`)

    res.status(201).json({
      user: { id: user.id, username: user.username, email: user.email, role: user.role },
      token,
      message: 'Registration successful',
    })
  } catch (error) {
    logger.error('Registration error:', error)
    res.status(500).json({ error: 'Registration failed. Please try again.' })
  }
})

authRouter.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' })
    }

    const user = users.find(u => u.email === email)
    if (!user || !verifyPassword(password, user.passwordHash)) {
      return res.status(401).json({ error: 'Invalid email or password' })
    }

    const token = createSession(user)
    logger.info(`User logged in: ${email}`)

    res.json({
      user: { id: user.id, username: user.username, email: user.email, role: user.role },
      token,
      message: 'Login successful',
    })
  } catch (error) {
    logger.error('Login error:', error)
    res.status(500).json({ error: 'Login failed. Please try again.' })
  }
})

authRouter.get('/me', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '')
  if (!token) return res.json({ user: null })

  const session = sessions.get(token)
  if (!session || session.expiresAt < Date.now()) {
    sessions.delete(token)
    return res.json({ user: null })
  }

  const user = users.find(u => u.id === session.userId)
  if (!user) return res.json({ user: null })

  res.json({
    user: { id: user.id, username: user.username, email: user.email, role: user.role },
  })
})

authRouter.post('/logout', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '')
  if (token) sessions.delete(token)
  res.json({ message: 'Logged out successfully' })
})
