import 'dotenv/config'
import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import rateLimit from 'express-rate-limit'
import { logger } from './utils/logger.js'
import { aiRouter } from './routes/ai.js'
import { authRouter } from './routes/auth.js'

const app = express()
const PORT = process.env.PORT || 3001

app.use(helmet())
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true,
}))
app.use(express.json({ limit: '10mb' }))

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Too many requests, please try again later.' },
})
app.use('/api/', limiter)

app.use('/api/ai', aiRouter)
app.use('/api/auth', authRouter)

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    ai: {
      gemini: !!process.env.GEMINI_API_KEY,
      openai: !!process.env.OPENAI_API_KEY,
    },
    timestamp: new Date().toISOString(),
  })
})

app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err)
  res.status(500).json({ error: 'Internal server error' })
})

app.listen(PORT, () => {
  logger.info(`SkillBridge API server running on port ${PORT}`)
  if (!process.env.GEMINI_API_KEY && !process.env.OPENAI_API_KEY) {
    logger.warn('No AI API keys configured - AI features will use fallback responses')
  }
})
