import { motion } from 'framer-motion'
import {
  BookOpen, Zap, Trophy, Users, TrendingUp, Clock, Sparkles,
  Brain, ArrowRight, GraduationCap, Target, BarChart3, Languages,
} from 'lucide-react'
import { StatCard } from '@/components/dashboard/StatCard'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { AiHelpWidget } from '@/components/dashboard/AiHelpWidget'
import { CourseProgress } from '@/components/dashboard/CourseProgress'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useNavigate } from 'react-router-dom'
import { cn } from '@/utils/cn'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const quickActions = [
  { icon: Brain, label: 'AI Assistant', path: '/ai-assistant', color: 'from-blue-500 to-purple-600', desc: 'Get instant help' },
  { icon: Languages, label: 'Translator', path: '/translator', color: 'from-emerald-500 to-teal-500', desc: '8 Indian languages' },
  { icon: BookOpen, label: 'My Courses', path: '/courses', color: 'from-amber-500 to-orange-500', desc: 'Track progress' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics', color: 'from-rose-500 to-pink-500', desc: 'View insights' },
]

const weeklyData = [
  { day: 'Mon', hours: 2.5 },
  { day: 'Tue', hours: 1.8 },
  { day: 'Wed', hours: 3.2 },
  { day: 'Thu', hours: 2.0 },
  { day: 'Fri', hours: 4.1 },
  { day: 'Sat', hours: 1.5 },
  { day: 'Sun', hours: 0 },
]

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8 pb-8"
    >
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <Badge variant="success" className="gap-1 text-[10px]">
              <Sparkles className="h-3 w-3" />
              Live
            </Badge>
          </div>
          <p className="text-muted-foreground">Welcome back! Continue your learning journey.</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/50 rounded-lg px-3 py-1.5">
          <Clock className="h-4 w-4" />
          <span>Updated today</span>
        </div>
      </motion.div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Enrolled Courses" value="6" icon={BookOpen} description="4 in progress" trend={{ value: 12, positive: true }} color="from-blue-500 to-cyan-500" delay={0} />
        <StatCard title="Total XP" value="2,450" icon={Zap} description="Level 8" trend={{ value: 8, positive: true }} color="from-amber-500 to-orange-500" delay={0.1} />
        <StatCard title="Badges Earned" value="12" icon={Trophy} description="3 this month" trend={{ value: 25, positive: true }} color="from-purple-500 to-pink-500" delay={0.2} />
        <StatCard title="Mentor Sessions" value="8" icon={Users} description="2 upcoming" trend={{ value: 5, positive: false }} color="from-emerald-500 to-teal-500" delay={0.3} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {quickActions.map((action, i) => (
            <motion.button
              key={action.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 + i * 0.05 }}
              onClick={() => navigate(action.path)}
              className="group relative overflow-hidden rounded-xl border bg-card p-4 text-left card-hover"
            >
              <div className={cn('absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-500 bg-gradient-to-br', action.color)} />
              <div className={cn('rounded-lg p-2.5 bg-gradient-to-br shadow-lg w-fit mb-3', action.color)}>
                <action.icon className="h-5 w-5 text-white" />
              </div>
              <p className="font-semibold text-sm">{action.label}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{action.desc}</p>
            </motion.button>
          ))}
        </div>
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <CourseProgress />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
          >
            <Card className="overflow-hidden">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <div className="rounded-lg bg-primary/10 p-1.5">
                    <TrendingUp className="h-4 w-4 text-primary" />
                  </div>
                  Weekly Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-2 h-32">
                  {weeklyData.map((d, i) => (
                    <div key={d.day} className="flex-1 flex flex-col items-center gap-1.5">
                      <span className="text-[10px] text-muted-foreground tabular-nums">{d.hours}h</span>
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${Math.max(d.hours / 5 * 100, 4)}%` }}
                        transition={{ delay: 0.4 + i * 0.05, duration: 0.5, ease: 'easeOut' }}
                        className={cn(
                          'w-full rounded-t-md bg-gradient-to-t from-primary/80 to-primary/30',
                          d.hours === 0 && 'opacity-20'
                        )}
                        style={{ maxHeight: '100%' }}
                      />
                      <span className="text-[10px] text-muted-foreground">{d.day}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <div className="rounded-lg bg-primary/10 p-1.5">
                    <Target className="h-4 w-4 text-primary" />
                  </div>
                  Learning Streak
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-bold text-primary tabular-nums">7</span>
                      <span className="text-muted-foreground">day streak</span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">Keep going! You're on fire</p>
                  </div>
                  <div className="flex gap-1.5">
                    {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, i) => (
                      <div
                        key={i}
                        className={cn(
                          'flex h-10 w-10 items-center justify-center rounded-full text-xs font-medium transition-all',
                          i < 5
                            ? 'bg-primary/10 text-primary ring-1 ring-primary/20'
                            : 'bg-muted text-muted-foreground'
                        )}
                      >
                        {day}
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        <div className="space-y-6">
          <AiHelpWidget />
          <RecentActivity />

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="relative overflow-hidden rounded-xl border bg-gradient-to-br from-primary/5 to-purple-500/5 p-6"
          >
            <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-bl from-primary/10 to-transparent rounded-full blur-3xl pointer-events-none" />
            <div className="relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="rounded-xl p-2.5 bg-gradient-to-br from-amber-500 to-orange-500 shadow-lg">
                  <GraduationCap className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold">Skill Goal</h3>
                  <p className="text-xs text-muted-foreground">Complete this week</p>
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Web Dev Path</span>
                    <span className="font-semibold">65%</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: '65%' }}
                      transition={{ delay: 0.6, duration: 0.8, ease: 'easeOut' }}
                      className="h-full rounded-full bg-gradient-to-r from-amber-500 to-orange-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
