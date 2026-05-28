import { useState, useCallback } from 'react'
import api from '@/utils/api'

export const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা' },
] as const

export type LanguageCode = (typeof LANGUAGES)[number]['code']
export type SourceLanguageCode = LanguageCode | 'auto'

export function useTranslation() {
  const [sourceLang, setSourceLang] = useState<SourceLanguageCode>('auto')
  const [targetLang, setTargetLang] = useState<LanguageCode>('hi')
  const [inputText, setInputText] = useState('')
  const [translatedText, setTranslatedText] = useState('')
  const [isTranslating, setIsTranslating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const translate = useCallback(
    async (text?: string, from?: SourceLanguageCode, to?: LanguageCode) => {
      const source = from || sourceLang
      const target = to || targetLang
      const txt = text || inputText

      if (!txt.trim()) return

      setIsTranslating(true)
      setError(null)

      try {
        const res = await api.post('/ai/translate', {
          text: txt.trim(),
          source_lang: source,
          target_lang: target,
        })
        setTranslatedText(res.data.translated_text || res.data.translation || '')
        if (res.data.detected && res.data.source_lang) {
          setSourceLang(res.data.source_lang as LanguageCode)
        }
      } catch (err: any) {
        setError(err?.response?.data?.error || err.message || 'Translation failed. Please try again.')
      } finally {
        setIsTranslating(false)
      }
    },
    [sourceLang, targetLang, inputText]
  )

  const swapLanguages = useCallback(() => {
    if (sourceLang === 'auto') return
    const newSource = targetLang
    const newTarget = sourceLang as LanguageCode
    setSourceLang(newSource)
    setTargetLang(newTarget)
    setInputText(translatedText)
    setTranslatedText(inputText)
  }, [sourceLang, targetLang, inputText, translatedText])

  return {
    sourceLang: sourceLang as SourceLanguageCode,
    targetLang: targetLang as LanguageCode,
    inputText,
    translatedText,
    isTranslating,
    error,
    setSourceLang: (v: SourceLanguageCode) => setSourceLang(v),
    setTargetLang: (v: LanguageCode) => setTargetLang(v),
    setInputText,
    setTranslatedText,
    translate,
    swapLanguages,
  }
}
