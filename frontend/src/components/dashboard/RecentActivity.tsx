import { motion } from 'framer-motion'
import { Clock, BookOpen, Award, MessageSquare, Zap } from 'lucide-react'
import { cn } from '@/utils/cn'

const activities = [
  { icon: BookOpen, text: 'Completed "Python Basics" module 3', time: '2 hours ago', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { icon: Award, text: 'Earned "Quick Learner" badge', time: '5 hours ago', color: 'text-amber-500', bg: 'bg-amber-500/10' },
  { icon: MessageSquare, text: 'Asked a doubt in Data Science forum', time: '1 day ago', color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { icon: Zap, text: 'Started "Web Development" skill path', time: '2 days ago', color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { icon: BookOpen, text: 'Scored 85% in JavaScript quiz', time: '3 days ago', color: 'text-rose-500', bg: 'bg-rose-500/10' },
]

export function RecentActivity() {
  return (
    <div className="rounded-xl border bg-card p-6">
      <div className="flex items-center gap-2.5 mb-5">
        <div className="rounded-lg bg-primary/10 p-2">
          <Clock className="h-4 w-4 text-primary" />
        </div>
        <h3 className="font-semibold">Recent Activity</h3>
      </div>
      <div className="space-y-3">
        {activities.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className="group flex items-start gap-3 rounded-lg p-2 -mx-2 hover:bg-muted/30 transition-colors"
          >
            <div className={cn('rounded-lg p-2 shrink-0', item.bg, item.color)}>
              <item.icon className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm leading-snug">{item.text}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{item.time}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
