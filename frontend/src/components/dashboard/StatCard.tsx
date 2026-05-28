import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/utils/cn'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  description?: string
  trend?: { value: number; positive: boolean }
  color?: string
  delay?: number
}

export function StatCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  color = 'from-blue-500 to-purple-600',
  delay = 0,
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: 'easeOut' }}
      className="group relative overflow-hidden rounded-xl border bg-card p-6 card-hover"
    >
      <div
        className={cn(
          'absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-500 bg-gradient-to-br',
          color
        )}
      />
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground font-medium">{title}</p>
          <p className="text-3xl font-bold tracking-tight">{value}</p>
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
        </div>
        <div className={cn('rounded-xl p-3 bg-gradient-to-br shadow-lg shrink-0', color)}>
          <Icon className="h-5 w-5 text-white" />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center gap-1.5">
          <span
            className={cn(
              'text-sm font-semibold',
              trend.positive ? 'text-emerald-500' : 'text-red-500'
            )}
          >
            {trend.positive ? '↑' : '↓'} {trend.value}%
          </span>
          <span className="text-xs text-muted-foreground">vs last month</span>
        </div>
      )}
    </motion.div>
  )
}
