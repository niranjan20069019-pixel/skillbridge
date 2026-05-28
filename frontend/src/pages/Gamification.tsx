import { motion } from 'framer-motion'
import { Trophy, Zap, Award, Target, Flame, Star, Medal } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const badges = [
  { name: 'Quick Starter', icon: Zap, description: 'Complete your first course', earned: true, color: 'text-blue-500' },
  { name: 'Knowledge Seeker', icon: Trophy, description: 'Complete 5 courses', earned: true, color: 'text-amber-500' },
  { name: 'Streak Master', icon: Flame, description: '7-day learning streak', earned: true, color: 'text-orange-500' },
  { name: 'Quiz Champion', icon: Award, description: 'Score 100% on any quiz', earned: false, color: 'text-purple-500' },
  { name: 'Skill Explorer', icon: Target, description: 'Try 3 different skill paths', earned: false, color: 'text-emerald-500' },
  { name: 'Star Learner', icon: Star, description: 'Complete 10 courses', earned: false, color: 'text-rose-500' },
]

const leaderboard = [
  { rank: 1, name: 'Rahul K.', xp: 12500, badge: 'Gold', color: 'bg-amber-500' },
  { rank: 2, name: 'Priya S.', xp: 10800, badge: 'Silver', color: 'bg-slate-400' },
  { rank: 3, name: 'Amit P.', xp: 9200, badge: 'Bronze', color: 'bg-amber-700' },
  { rank: 4, name: 'Sneha R.', xp: 8500, badge: '', color: 'bg-muted' },
  { rank: 5, name: 'Vikram S.', xp: 7800, badge: '', color: 'bg-muted' },
]

export default function Gamification() {
  return (
    <div className="space-y-8 pb-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 p-2.5 shadow-lg">
            <Trophy className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Achievements</h1>
            <p className="text-muted-foreground">Track your badges, XP, and compete on the leaderboard</p>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <div className="rounded-lg bg-amber-500/10 p-1.5">
                  <Award className="h-4 w-4 text-amber-500" />
                </div>
                Badges ({badges.filter(b => b.earned).length}/{badges.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {badges.map((badge) => (
                  <div
                    key={badge.name}
                    className={`rounded-xl border p-4 text-center transition-all ${
                      badge.earned
                        ? 'bg-amber-500/5 border-amber-500/20 shadow-sm'
                        : 'opacity-40 hover:opacity-60'
                    }`}
                  >
                    <div
                      className={`inline-flex rounded-full p-3 mb-2 ${
                        badge.earned ? 'bg-amber-500/10' : 'bg-muted'
                      }`}
                    >
                      <badge.icon
                        className={`h-6 w-6 ${badge.earned ? badge.color : 'text-muted-foreground'}`}
                      />
                    </div>
                    <p className="text-sm font-medium">{badge.name}</p>
                    <p className="text-xs text-muted-foreground mt-1">{badge.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <div className="rounded-lg bg-amber-500/10 p-1.5">
                <Medal className="h-4 w-4 text-amber-500" />
              </div>
              Leaderboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {leaderboard.map((entry) => (
                <div
                  key={entry.rank}
                  className="flex items-center gap-3 rounded-lg p-3 hover:bg-muted/50 transition-all"
                >
                  <span
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold text-white shadow-sm ${
                      entry.color
                    }`}
                  >
                    {entry.rank}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{entry.name}</p>
                    <p className="text-xs text-muted-foreground">{entry.xp.toLocaleString()} XP</p>
                  </div>
                  {entry.badge && <Badge variant="success">{entry.badge}</Badge>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
