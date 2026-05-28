import { motion } from 'framer-motion'
import { BookOpen, ChevronRight } from 'lucide-react'
import { cn } from '@/utils/cn'
import { Badge } from '@/components/ui/badge'

const courses = [
  { name: 'Python for Beginners', progress: 75, category: 'Technology', color: 'from-blue-500 to-cyan-500' },
  { name: 'Digital Marketing 101', progress: 45, category: 'Marketing', color: 'from-purple-500 to-pink-500' },
  { name: 'Data Science Fundamentals', progress: 20, category: 'Technology', color: 'from-emerald-500 to-teal-500' },
]

export function CourseProgress() {
  return (
    <div className="rounded-xl border bg-card p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-primary/10 p-2">
            <BookOpen className="h-4 w-4 text-primary" />
          </div>
          <h3 className="font-semibold">Course Progress</h3>
        </div>
        <button className="group flex items-center gap-1 text-sm text-primary hover:underline">
          View all
          <ChevronRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
        </button>
      </div>
      <div className="space-y-5">
        {courses.map((course, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="group cursor-pointer"
          >
            <div className="flex items-center justify-between mb-2.5">
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm font-medium truncate">{course.name}</span>
                <Badge variant="secondary" className="text-[10px] shrink-0 px-1.5 py-0">
                  {course.category}
                </Badge>
              </div>
              <span className="text-sm font-semibold shrink-0 ml-2 tabular-nums">
                {course.progress}%
              </span>
            </div>
            <div className="relative h-2 rounded-full bg-muted overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${course.progress}%` }}
                transition={{ delay: i * 0.1 + 0.3, duration: 0.8, ease: 'easeOut' }}
                className={cn('h-full rounded-full bg-gradient-to-r', course.color)}
              />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
