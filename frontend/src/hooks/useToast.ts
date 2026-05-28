import { useState, useCallback } from 'react'

export interface Toast {
  id: string
  title: string
  description?: string
  variant?: 'default' | 'success' | 'destructive' | 'warning'
}

let toastListeners: ((toast: Toast) => void)[] = []
let toastIdCounter = 0

export function toast(toast: Omit<Toast, 'id'>) {
  const id = (++toastIdCounter).toString()
  const newToast = { ...toast, id }
  toastListeners.forEach(listener => listener(newToast))
  return id
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((t: Toast) => {
    setToasts(prev => [...prev, t])
    setTimeout(() => {
      setToasts(prev => prev.filter(item => item.id !== t.id))
    }, 4000)
  }, [])

  const dismissToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  useState(() => {
    toastListeners.push(addToast)
    return () => {
      toastListeners = toastListeners.filter(l => l !== addToast)
    }
  })

  return { toasts, dismissToast }
}
