import { Router } from 'express'
import { generateChatResponse, translateText, detectLanguage } from '../services/gemini.js'
import { generateChatResponseOpenAI, translateTextOpenAI, detectLanguageOpenAI } from '../services/openai.js'
import { translateTextFree } from '../services/free-translate.js'
import { logger } from '../utils/logger.js'

const UNICODE_RANGES = {
  hi: [/[\u0900-\u097F]/, /[\uA8E0-\uA8FF]/],
  kn: [/[\u0C80-\u0CFF]/],
  ta: [/[\u0B80-\u0BFF]/],
  te: [/[\u0C00-\u0C7F]/],
  ml: [/[\u0D00-\u0D7F]/],
  mr: [/[\u0900-\u097F]/, /[\uA8E0-\uA8FF]/],
  bn: [/[\u0980-\u09FF]/],
}

function quickDetect(text) {
  for (const [code, ranges] of Object.entries(UNICODE_RANGES)) {
    if (ranges.some(r => r.test(text))) return code
  }
  return null
}

export const aiRouter = Router()

const CHAT_TIMEOUT = 45000
const TRANSLATE_TIMEOUT = 30000

function withTimeout(promise, ms, label) {
  let timer
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`${label} timed out after ${ms}ms`)), ms)
  })
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer))
}

aiRouter.post('/chat', async (req, res) => {
  try {
    const { message, history } = req.body

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message is required' })
    }
    if (message.length > 4000) {
      return res.status(400).json({ error: 'Message exceeds 4000 character limit' })
    }

    let response = null
    let provider = 'fallback'

    if (process.env.GEMINI_API_KEY) {
      try {
        response = await withTimeout(
          generateChatResponse(message, history || []),
          CHAT_TIMEOUT,
          'Gemini chat'
        )
        if (response) provider = 'gemini'
      } catch (err) {
        logger.warn('Gemini failed, falling back:', err.message)
      }
    }

    if (!response) {
      try {
        response = await withTimeout(
          generateChatResponseOpenAI(message, history || []),
          CHAT_TIMEOUT,
          'OpenAI chat'
        )
        if (response) provider = 'openai'
      } catch (err) {
        logger.warn('OpenAI also failed:', err.message)
      }
    }

    res.json({
      response: response || 'I apologise, but I am unable to process your request right now. Please try again later.',
      timestamp: new Date().toISOString(),
      provider,
    })
  } catch (error) {
    logger.error('Chat route error:', error)
    res.status(500).json({
      response: 'I apologise, but the service is temporarily unavailable. Please try again later.',
      error: 'Internal server error',
    })
  }
})

aiRouter.post('/translate', async (req, res) => {
  try {
    let { text, source_lang, target_lang } = req.body

    if (!text || !target_lang) {
      return res.status(400).json({ error: 'text and target_lang are required' })
    }
    if (text.length > 5000) {
      return res.status(400).json({ error: 'Text exceeds 5000 character limit' })
    }

    const validLangs = ['en', 'hi', 'kn', 'ta', 'te', 'ml', 'mr', 'bn']
    if (!validLangs.includes(target_lang)) {
      return res.status(400).json({ error: 'Invalid target language code' })
    }

    if (!source_lang || source_lang === 'auto') {
      source_lang = quickDetect(text) || 'en'
    }

    if (!validLangs.includes(source_lang || '')) {
      source_lang = 'en'
    }

    let translation = null
    let provider = 'fallback'

    try {
      translation = await translateTextFree(text, source_lang, target_lang)
      if (translation) provider = 'free'
    } catch (err) {
      logger.warn('Free translation failed:', err.message)
    }

    if (!translation && process.env.GEMINI_API_KEY) {
      try {
        translation = await withTimeout(
          translateText(text, source_lang, target_lang),
          TRANSLATE_TIMEOUT,
          'Gemini translate'
        )
        if (translation) provider = 'gemini'
      } catch (err) {
        logger.warn('Gemini translate failed, falling back:', err.message)
      }
    }

    if (!translation) {
      try {
        translation = await withTimeout(
          translateTextOpenAI(text, source_lang, target_lang),
          TRANSLATE_TIMEOUT,
          'OpenAI translate'
        )
        if (translation) provider = 'openai'
      } catch (err) {
        logger.warn('OpenAI also failed:', err.message)
      }
    }

    res.json({
      translated_text: translation || '',
      source_lang,
      target_lang,
      detected: !req.body.source_lang || req.body.source_lang === 'auto',
      provider,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    logger.error('Translation route error:', error)
    res.status(500).json({ error: 'Translation failed. Please try again.' })
  }
})

aiRouter.post('/detect-language', async (req, res) => {
  try {
    const { text } = req.body
    if (!text) return res.status(400).json({ error: 'Text is required' })

    let lang = null
    if (process.env.OPENAI_API_KEY) {
      lang = await detectLanguageOpenAI(text)
    }
    if (!lang || !['en', 'hi', 'kn', 'ta', 'te', 'ml', 'mr', 'bn'].includes(lang)) {
      lang = await detectLanguage(text)
    }

    res.json({
      language: lang || 'en',
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    logger.error('Language detection route error:', error)
    res.status(500).json({ error: 'Language detection failed' })
  }
})
