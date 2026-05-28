import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BookOpen, Clock, Star, Users, Search, Youtube, FileText, Brain } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { CourseDetail } from '@/components/courses/CourseDetail'

export interface Course {
  id: number
  title: string
  category: string
  level: string
  duration: string
  rating: number
  students: number
  image: string
  color: string
  videoId?: string
}

const courses: Course[] = [
  { id: 1, title: 'Python for Beginners', category: 'Technology', level: 'Beginner', duration: '8 weeks', rating: 4.8, students: 1234, image: 'from-blue-500 to-cyan-500', color: 'bg-blue-500', videoId: 'eWRfhZUzrAc' },
  { id: 2, title: 'Digital Marketing 101', category: 'Marketing', level: 'Beginner', duration: '6 weeks', rating: 4.6, students: 892, image: 'from-purple-500 to-pink-500', color: 'bg-purple-500', videoId: 'j7gXepN1nJI' },
  { id: 3, title: 'Data Science Fundamentals', category: 'Technology', level: 'Intermediate', duration: '12 weeks', rating: 4.9, students: 756, image: 'from-emerald-500 to-teal-500', color: 'bg-emerald-500', videoId: 'ua-CiDNNj30' },
  { id: 4, title: 'Financial Literacy', category: 'Finance', level: 'Beginner', duration: '4 weeks', rating: 4.5, students: 2100, image: 'from-amber-500 to-orange-500', color: 'bg-amber-500', videoId: 'vJabNEwZIuc' },
  { id: 5, title: 'Web Development', category: 'Technology', level: 'Intermediate', duration: '16 weeks', rating: 4.7, students: 1567, image: 'from-rose-500 to-pink-500', color: 'bg-rose-500', videoId: 'zJSY8tbf_ys' },
  { id: 6, title: 'Organic Farming', category: 'Agriculture', level: 'Beginner', duration: '6 weeks', rating: 4.4, students: 678, image: 'from-green-500 to-emerald-500', color: 'bg-green-500', videoId: 'iaQjEDYyWKw' },
]

const categories = ['All', 'Technology', 'Marketing', 'Finance', 'Agriculture', 'Design', 'Healthcare']

export default function Courses() {
  const [activeCat, setActiveCat] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)

  const filtered = courses.filter(c => {
    const matchCat = activeCat === 'All' || c.category === activeCat
    const matchSearch = c.title.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCat && matchSearch
  })

  return (
    <div className="space-y-8 pb-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 p-2.5 shadow-lg">
            <BookOpen className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Explore Courses</h1>
            <p className="text-muted-foreground">Discover courses with video lessons, quizzes, and downloadable notes</p>
          </div>
        </div>
      </motion.div>

      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="relative flex-1 max-w-md w-full">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search courses..."
            className="pl-9 bg-muted/50 border-0 focus-visible:ring-1"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-2 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0 scrollbar-thin">
          {categories.map((cat) => (
            <Button
              key={cat}
              variant={cat === activeCat ? 'default' : 'outline'}
              size="sm"
              className="shrink-0"
              onClick={() => setActiveCat(cat)}
            >
              {cat}
            </Button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <BookOpen className="h-12 w-12" />
          </div>
          <h3 className="text-lg font-semibold mb-1">No courses found</h3>
          <p className="text-sm text-muted-foreground">Try adjusting your search or filter</p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((course, i) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card
                className="group overflow-hidden hover:shadow-lg transition-all duration-300 h-full card-hover cursor-pointer"
                onClick={() => setSelectedCourse(course)}
              >
                <div className={`h-40 bg-gradient-to-br ${course.image} relative overflow-hidden`}>
                  <div className="absolute inset-0 bg-black/10 group-hover:bg-black/0 transition-colors" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
                  <div className="absolute top-3 left-3 flex gap-2">
                    <Badge variant="secondary" className="bg-white/90 text-black border-0 font-medium">
                      {course.category}
                    </Badge>
                  </div>
                  <div className="absolute bottom-3 right-3">
                    <Badge variant="secondary" className="bg-white/90 text-black border-0">
                      {course.level}
                    </Badge>
                  </div>
                  {}
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="rounded-full bg-white/90 p-3 shadow-lg">
                      <Youtube className="h-6 w-6 text-red-500" />
                    </div>
                  </div>
                </div>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg group-hover:text-primary transition-colors">
                    {course.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" /> {course.duration}
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-amber-500 text-amber-500" /> {course.rating}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="h-4 w-4" /> {course.students.toLocaleString()}
                    </span>
                  </div>
                  {}
                  <div className="flex gap-2 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Youtube className="h-3.5 w-3.5" /> Video lessons
                    </span>
                    <span className="flex items-center gap-1">
                      <Brain className="h-3.5 w-3.5" /> Quiz
                    </span>
                    <span className="flex items-center gap-1">
                      <FileText className="h-3.5 w-3.5" /> Notes
                    </span>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button
                    className="w-full gap-2 group-hover:gap-3 transition-all"
                    onClick={(e) => { e.stopPropagation(); setSelectedCourse(course) }}
                  >
                    <Youtube className="h-4 w-4" /> Start Learning
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      <AnimatePresence>
        {selectedCourse && (
          <CourseDetail course={selectedCourse} onClose={() => setSelectedCourse(null)} />
        )}
      </AnimatePresence>
    </div>
  )
}
