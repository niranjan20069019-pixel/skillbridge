import { logger } from '../utils/logger.js'

const MYMEMORY_API = 'https://api.mymemory.translated.net/get'
const TIMEOUT = 10000

export async function translateTextFree(text, sourceLang, targetLang) {
  const url = `${MYMEMORY_API}?q=${encodeURIComponent(text.slice(0, 500))}&langpair=${sourceLang}|${targetLang}`
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT)

  try {
    const res = await fetch(url, { signal: controller.signal })
    if (!res.ok) return null
    const data = await res.json()
    if (data.responseStatus === 200 && data.responseData?.translatedText) {
      return data.responseData.translatedText
    }
    return null
  } catch (error) {
    if (error.name === 'AbortError') {
      logger.warn('Free translation timed out')
    } else {
      logger.warn('Free translation failed:', error.message)
    }
    return null
  } finally {
    clearTimeout(timer)
  }
}
