import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { useToast, type Toast } from '@/hooks/useToast'
import { cn } from '@/utils/cn'

const iconMap = {
  success: CheckCircle,
  destructive: AlertCircle,
  warning: AlertTriangle,
  default: Info,
}

const colorMap = {
  success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  destructive: 'border-red-500/30 bg-red-500/10 text-red-600 dark:text-red-400',
  warning: 'border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400',
  default: 'border-primary/30 bg-primary/5 text-foreground',
}

export function ToastContainer() {
  const { toasts, dismissToast } = useToast()

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast: Toast) => {
          const Icon = iconMap[toast.variant || 'default']
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className={cn(
                'pointer-events-auto rounded-xl border bg-background p-4 shadow-lg backdrop-blur-xl',
                colorMap[toast.variant || 'default']
              )}
            >
              <div className="flex items-start gap-3">
                <Icon className="h-5 w-5 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold">{toast.title}</p>
                  {toast.description && (
                    <p className="text-xs mt-0.5 opacity-80">{toast.description}</p>
                  )}
                </div>
                <button
                  onClick={() => dismissToast(toast.id)}
                  className="shrink-0 rounded-lg p-1 hover:bg-white/10 dark:hover:bg-black/10 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
