import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, Clock, Target, BookOpen, Brain } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Analytics() {
  return (
    <div className="space-y-8 pb-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 shadow-lg">
            <BarChart3 className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Learning Analytics</h1>
            <p className="text-muted-foreground">Track your learning patterns and performance</p>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Study Hours', value: '127', icon: Clock, color: 'from-blue-500 to-cyan-500', change: '+12%' },
          { label: 'Courses Completed', value: '4', icon: BookOpen, color: 'from-emerald-500 to-teal-500', change: '+2' },
          { label: 'Quiz Avg Score', value: '82%', icon: Target, color: 'from-amber-500 to-orange-500', change: '+5%' },
          { label: 'Consistency', value: 'A', icon: Brain, color: 'from-purple-500 to-pink-500', change: 'Top 10%' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
                  <div className={`rounded-lg p-2 bg-gradient-to-br ${stat.color} shadow-sm`}>
                    <stat.icon className="h-4 w-4 text-white" />
                  </div>
                </div>
                <p className="text-2xl font-bold tracking-tight">{stat.value}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  <span className="text-emerald-500 font-medium">{stat.change}</span> vs last month
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <div className="rounded-lg bg-primary/10 p-1.5">
                <TrendingUp className="h-4 w-4 text-primary" />
              </div>
              Weekly Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-2 h-44">
              {[40, 65, 35, 80, 55, 90, 70].map((height, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-2">
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height }}
                    transition={{ delay: i * 0.1, duration: 0.5, ease: 'easeOut' }}
                    className="w-full rounded-lg bg-gradient-to-t from-primary/50 to-primary shadow-sm"
                    style={{ height: `${height}%` }}
                  />
                  <span className="text-xs text-muted-foreground">
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i]}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <div className="rounded-lg bg-primary/10 p-1.5">
                <Brain className="h-4 w-4 text-primary" />
              </div>
              Skills Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-5">
              {[
                { skill: 'Python', level: 80, color: 'from-blue-500 to-cyan-500' },
                { skill: 'JavaScript', level: 60, color: 'from-amber-500 to-orange-500' },
                { skill: 'Data Analysis', level: 45, color: 'from-purple-500 to-pink-500' },
                { skill: 'Communication', level: 70, color: 'from-emerald-500 to-teal-500' },
              ].map((item) => (
                <div key={item.skill}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="font-medium">{item.skill}</span>
                    <span className="text-muted-foreground tabular-nums">{item.level}%</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.level}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className={`h-full rounded-full bg-gradient-to-r ${item.color}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
