import { useState, useCallback, useRef } from 'react'
import api from '@/utils/api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  provider?: 'gemini' | 'openai' | 'fallback'
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Namaste! 👋 I'm your **SkillBridge AI Assistant**.

I can help you with:
- 📚 **Course recommendations** — "Suggest courses for data science"
- 🛤️ **Career guidance** — "What skill path is best for me?"
- 👨‍🏫 **Study tips** — "How to prepare for exams?"
- 🌐 **Translation** — "Translate this to Kannada"
- 🏛️ **Schemes** — "Tell me about education schemes"

Feel free to ask in **English, Hindi, Kannada, Tamil,** or any Indian language!`,
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentProvider, setCurrentProvider] = useState<'gemini' | 'openai' | 'fallback'>('gemini')
  const abortRef = useRef<AbortController | null>(null)

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const recentHistory = messages.slice(-6).map(m => ({
        role: m.role,
        content: m.content,
      }))

      const res = await api.post(
        '/ai/chat',
        {
          message: content.trim(),
          history: recentHistory,
        },
        {
          signal: controller.signal,
          timeout: 90000,
        }
      )

      const provider = res.data.provider || 'gemini'
      setCurrentProvider(provider)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content:
          res.data.response ||
          res.data.message ||
          'I apologise, but I am unable to process that request at the moment.',
        timestamp: new Date(),
        provider,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err: any) {
      if (err.name === 'CanceledError' || err.name === 'AbortError') return

      const errorMsg =
        err.message || 'I apologise, but I am unable to process your request right now. Please try again later.'
      setError(errorMsg)
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `⚠️ ${errorMsg}`,
          timestamp: new Date(),
          provider: 'fallback',
        },
      ])
    } finally {
      setIsLoading(false)
      abortRef.current = null
    }
  }, [messages, isLoading])

  const clearMessages = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort()
    }
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: `Namaste! 👋 I'm your **SkillBridge AI Assistant**.

I can help you with:
- 📚 **Course recommendations** — "Suggest courses for data science"
- 🛤️ **Career guidance** — "What skill path is best for me?"
- 👨‍🏫 **Study tips** — "How to prepare for exams?"
- 🌐 **Translation** — "Translate this to Kannada"
- 🏛️ **Schemes** — "Tell me about education schemes"

Feel free to ask in **English, Hindi, Kannada, Tamil,** or any Indian language!`,
        timestamp: new Date(),
      },
    ])
    setError(null)
  }, [])

  return { messages, isLoading, error, currentProvider, sendMessage, clearMessages }
}
