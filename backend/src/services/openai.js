import OpenAI from 'openai'
import { logger } from '../utils/logger.js'

const API_KEY = process.env.OPENAI_API_KEY

let openai = null

if (API_KEY) {
  openai = new OpenAI({ apiKey: API_KEY })
  logger.info('OpenAI initialized successfully')
} else {
  logger.warn('No OpenAI API key found - will use Gemini or fallback')
}

export async function generateChatResponseOpenAI(message, history = []) {
  if (!openai) return null

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'You are SkillBridge AI, a helpful educational assistant for Indian students. Respond in the language the user writes in. Use markdown. Be concise but thorough.',
        },
        ...history.slice(-10).map(m => ({
          role: m.role,
          content: m.content,
        })),
        { role: 'user', content: message },
      ],
      max_tokens: 800,
      temperature: 0.7,
    })

    return completion.choices[0]?.message?.content || null
  } catch (error) {
    logger.error('OpenAI API error:', error.message)
    return null
  }
}

export async function translateTextOpenAI(text, sourceLang, targetLang) {
  if (!openai) return null

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: `You are a translator. Translate from ${sourceLang} to ${targetLang}. Return ONLY the translated text.`,
        },
        { role: 'user', content: text },
      ],
      max_tokens: 500,
      temperature: 0.3,
    })

    return completion.choices[0]?.message?.content?.trim() || null
  } catch (error) {
    logger.error('OpenAI translation error:', error.message)
    return null
  }
}

export async function detectLanguageOpenAI(text) {
  if (!openai) return null

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'Identify the language code (en/hi/kn/ta/te/ml/mr/bn) of the given text. Return ONLY the 2-letter code.',
        },
        { role: 'user', content: text.substring(0, 200) },
      ],
      max_tokens: 10,
      temperature: 0.1,
    })

    return completion.choices[0]?.message?.content?.trim().toLowerCase().substring(0, 2) || null
  } catch (error) {
    logger.error('OpenAI language detection error:', error.message)
    return null
  }
}
