import { motion } from 'framer-motion'
import { Compass, ArrowRight, Zap, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const skillPaths = [
  { title: 'Data Scientist', skills: ['Python', 'Statistics', 'Machine Learning', 'SQL'], duration: '6 months', projects: 4, color: 'from-blue-500 to-cyan-500' },
  { title: 'Web Developer', skills: ['HTML/CSS', 'JavaScript', 'React', 'Node.js'], duration: '5 months', projects: 5, color: 'from-purple-500 to-pink-500' },
  { title: 'Digital Marketer', skills: ['SEO', 'Social Media', 'Analytics', 'Content'], duration: '4 months', projects: 3, color: 'from-amber-500 to-orange-500' },
  { title: 'Financial Analyst', skills: ['Excel', 'Accounting', 'Analysis', 'Reporting'], duration: '4 months', projects: 3, color: 'from-emerald-500 to-teal-500' },
  { title: 'Data Analyst', skills: ['Python', 'SQL', 'Visualization', 'Statistics'], duration: '3 months', projects: 3, color: 'from-rose-500 to-pink-500' },
]

export default function SkillPaths() {
  return (
    <div className="space-y-8 pb-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 p-2.5 shadow-lg">
            <Compass className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Skill Paths</h1>
            <p className="text-muted-foreground">Follow structured learning paths to master in-demand skills</p>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {skillPaths.map((path, i) => (
          <motion.div
            key={path.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="group card-hover h-full">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg group-hover:text-primary transition-colors">{path.title}</CardTitle>
                  <Badge variant="success" className="shrink-0">{path.duration}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-1.5">
                  {path.skills.map((skill) => (
                    <Badge key={skill} variant="secondary" className="font-normal">
                      {skill}
                    </Badge>
                  ))}
                </div>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Zap className="h-4 w-4" /> {path.projects} projects
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {[1, 2, 3, 4, 5].map((step) => (
                    <div
                      key={step}
                      className={`flex-1 h-2 rounded-full transition-all ${
                        step <= 2 ? 'bg-gradient-to-r ' + path.color : 'bg-muted'
                      }`}
                    />
                  ))}
                </div>
                <Button className="w-full gap-2 group-hover:gap-3 transition-all">
                  Start Path <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
