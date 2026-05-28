import { motion } from 'framer-motion'
import { Users, Star, MessageSquare, Search, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

const mentors = [
  { name: 'Dr. Rajesh Kumar', expertise: 'Data Science', rating: 4.9, students: 342, sessions: 89, available: true },
  { name: 'Priya Sharma', expertise: 'Web Development', rating: 4.8, students: 256, sessions: 67, available: true },
  { name: 'Amit Patel', expertise: 'Digital Marketing', rating: 4.7, students: 198, sessions: 54, available: false },
  { name: 'Sneha Reddy', expertise: 'Finance', rating: 4.9, students: 421, sessions: 112, available: true },
  { name: 'Vikram Singh', expertise: 'Agriculture Tech', rating: 4.6, students: 167, sessions: 43, available: true },
]

export default function Mentors() {
  return (
    <div className="space-y-8 pb-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 p-2.5 shadow-lg">
            <Users className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Mentors</h1>
            <p className="text-muted-foreground">Connect with expert mentors for personalized guidance</p>
          </div>
        </div>
      </motion.div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search mentors by name or expertise..." className="pl-9 bg-muted/50 border-0 focus-visible:ring-1" />
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {mentors.map((mentor, i) => (
          <motion.div
            key={mentor.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="group card-hover">
              <CardHeader>
                <div className="flex items-center gap-4">
                  <Avatar className="h-14 w-14 ring-2 ring-primary/10">
                    <AvatarFallback className="bg-gradient-to-br from-primary/20 to-primary/10 text-primary font-semibold text-lg">
                      {mentor.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold truncate">{mentor.name}</h3>
                    <p className="text-sm text-muted-foreground">{mentor.expertise}</p>
                  </div>
                  {mentor.available ? (
                    <Badge variant="success" className="shrink-0">Available</Badge>
                  ) : (
                    <Badge variant="secondary" className="shrink-0">Busy</Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                  <span className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-amber-500 text-amber-500" /> {mentor.rating}
                  </span>
                  <span>{mentor.students.toLocaleString()} students</span>
                  <span>{mentor.sessions} sessions</span>
                </div>
                <Button className="w-full gap-2" variant={mentor.available ? 'default' : 'outline'}>
                  {mentor.available ? (
                    <><Calendar className="h-4 w-4" /> Book Session</>
                  ) : (
                    <><MessageSquare className="h-4 w-4" /> Send Message</>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
