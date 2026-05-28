import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, useScroll, useTransform } from 'framer-motion'
import {
  Sparkles,
  GraduationCap,
  MessageSquare,
  Languages,
  Bot,
  Globe,
  ArrowRight,
  Check,
  Star,
  Menu,
  X,
  BookOpen,
  Shield,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useMediaQuery } from '@/hooks/useMediaQuery'

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'Languages', href: '#languages' },
  { label: 'About', href: '#about' },
]

const features = [
  {
    icon: Bot,
    title: 'AI-Powered Learning Assistant',
    description: 'Get personalized help from our Gemini-powered AI assistant. Ask questions in any Indian language.',
    color: 'from-blue-500 to-purple-600',
  },
  {
    icon: Languages,
    title: 'Multi-Language Support',
    description: 'Learn in 8 Indian languages including Hindi, Kannada, Tamil, Telugu, and more.',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    icon: GraduationCap,
    title: 'Expert-Mentored Courses',
    description: 'Industry-aligned courses designed by experts with mentor support and certifications.',
    color: 'from-amber-500 to-orange-500',
  },
  {
    icon: MessageSquare,
    title: 'Community & Doubt Solving',
    description: 'Real-time doubt solving with mentors and a supportive peer community.',
    color: 'from-rose-500 to-pink-500',
  },
  {
    icon: Globe,
    title: 'Rural India Focus',
    description: 'Specially designed for rural learners with offline-friendly content and optimization.',
    color: 'from-cyan-500 to-blue-500',
  },
  {
    icon: BookOpen,
    title: 'Structured Skill Paths',
    description: 'Follow guided learning paths from beginner to job-ready with hands-on projects.',
    color: 'from-violet-500 to-purple-500',
  },
]

const languages = [
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা' },
  { code: 'en', name: 'English', native: 'English' },
]

const stats = [
  { label: 'Active Learners', value: '10,000+' },
  { label: 'Courses Available', value: '50+' },
  { label: 'Expert Mentors', value: '100+' },
  { label: 'Languages', value: '8' },
]

export default function Landing() {
  const navigate = useNavigate()
  const isMobile = useMediaQuery('(max-width: 768px)')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { scrollY } = useScroll()
  const heroScale = useTransform(scrollY, [0, 300], [1, 0.95])
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0.6])

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-transparent bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold">SkillBridge</span>
          </Link>

          {isMobile ? (
            <>
              <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
              {mobileMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute top-16 left-0 right-0 border-b bg-background p-4 space-y-2 shadow-lg"
                >
                  {navLinks.map((link) => (
                    <a
                      key={link.label}
                      href={link.href}
                      className="block rounded-lg px-3 py-2 text-sm hover:bg-muted"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {link.label}
                    </a>
                  ))}
                  <div className="flex gap-2 pt-2 border-t">
                    <Button variant="outline" size="sm" className="flex-1" onClick={() => navigate('/login')}>
                      Login
                    </Button>
                    <Button size="sm" className="flex-1" onClick={() => navigate('/register')}>
                      Sign Up
                    </Button>
                  </div>
                </motion.div>
              )}
            </>
          ) : (
            <>
              <nav className="flex items-center gap-8">
                {navLinks.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.label}
                  </a>
                ))}
              </nav>
              <div className="flex items-center gap-3">
                <Button variant="ghost" onClick={() => navigate('/login')}>Login</Button>
                <Button onClick={() => navigate('/register')} className="gap-2">
                  Get Started <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </>
          )}
        </div>
      </header>

      <motion.section
        style={{ scale: heroScale, opacity: heroOpacity }}
        className="relative pt-32 pb-20 sm:pt-40 sm:pb-28 overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-purple-500/5" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[128px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px]" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mb-6 inline-flex items-center gap-2 rounded-full border bg-muted/50 px-4 py-1.5 text-sm"
            >
              <Sparkles className="h-4 w-4 text-amber-500" />
              <span>Empowering Rural India with AI-Powered Education</span>
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl"
            >
              Bridge the{' '}
              <span className="text-gradient">Skill Gap</span>
              <br />
              With AI Guidance
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed"
            >
              Learn in your native language with AI-powered tutoring, expert mentorship,
              and industry-recognized certifications. Built for rural India, powered by Gemini AI.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Button
                size="lg"
                className="w-full sm:w-auto gap-2 text-base h-12 px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all"
                onClick={() => navigate('/register')}
              >
                Start Learning Free
                <ArrowRight className="h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto text-base h-12 px-8"
                onClick={() => navigate('/login')}
              >
                Sign In
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6"
            >
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="text-2xl font-bold text-gradient">{stat.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{stat.label}</p>
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </motion.section>

      <section id="features" className="py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything You Need to Succeed
            </h2>
            <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">
              AI-powered tools, multi-language support, and expert guidance — all in one platform.
            </p>
          </motion.div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group relative rounded-xl border bg-card p-6 hover:shadow-lg transition-all duration-300 card-hover"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500 rounded-xl`} />
                <div className={`rounded-xl p-3 bg-gradient-to-br ${feature.color} shadow-lg w-fit mb-4`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="languages" className="py-20 sm:py-28 bg-muted/30">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Learn in Your Language
            </h2>
            <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">
              Breaking language barriers with support for 8 Indian languages.
            </p>
          </motion.div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {languages.map((lang, i) => (
              <motion.div
                key={lang.code}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="rounded-xl border bg-card p-6 text-center hover:border-primary/50 transition-all group card-hover"
              >
                <p className="text-2xl font-bold mb-1">{lang.native}</p>
                <p className="text-sm text-muted-foreground">{lang.name}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="about" className="py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">
                Built for Rural India,<br />
                <span className="text-gradient">Powered by AI</span>
              </h2>
              <div className="space-y-4">
                {[
                  'AI assistant that understands your questions in any Indian language',
                  'Government scheme information and skill development programs',
                  'Industry-recognized certificates upon course completion',
                  'Offline-friendly content for areas with limited connectivity',
                  'Connect with expert mentors from top Indian companies',
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-start gap-3"
                  >
                    <div className="rounded-full p-1 bg-emerald-500/10 mt-0.5 shrink-0">
                      <Check className="h-4 w-4 text-emerald-500" />
                    </div>
                    <p className="text-muted-foreground">{item}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="rounded-2xl border bg-card p-8 shadow-xl">
                <div className="flex items-center gap-2 mb-6">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star key={star} className="h-4 w-4 fill-amber-500 text-amber-500" />
                    ))}
                  </div>
                  <span className="text-sm text-muted-foreground">4.9/5 from 2,000+ learners</span>
                </div>
                <div className="space-y-4">
                  {[
                    { name: 'Priya S.', text: 'The AI assistant helps me learn in Kannada. Finally, I can understand complex topics in my mother tongue!', role: 'Student, Karnataka' },
                    { name: 'Rahul K.', text: 'Got my first job after completing the Web Development skill path. The mentorship was incredible.', role: 'Developer, Tamil Nadu' },
                    { name: 'Lakshmi M.', text: 'The translation feature is a game-changer. I learn in Telugu and still get certified in English.', role: 'Learner, Andhra Pradesh' },
                  ].map((testimonial, i) => (
                    <div key={i} className="rounded-lg bg-muted/50 p-4">
                      <p className="text-sm text-muted-foreground mb-2 leading-relaxed">"{testimonial.text}"</p>
                      <div>
                        <p className="text-sm font-medium">{testimonial.name}</p>
                        <p className="text-xs text-muted-foreground">{testimonial.role}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="py-20 sm:py-28 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl text-white mb-6">
              Ready to Transform Your Future?
            </h2>
            <p className="text-lg text-white/80 mb-8 max-w-2xl mx-auto leading-relaxed">
              Join thousands of learners across India. Start your learning journey today — it's free!
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                variant="secondary"
                className="w-full sm:w-auto text-base h-12 px-8 gap-2 shadow-lg"
                onClick={() => navigate('/register')}
              >
                Create Free Account
                <ArrowRight className="h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto text-base h-12 px-8 border-white/20 text-white hover:text-white hover:bg-white/10"
                onClick={() => navigate('/login')}
              >
                I already have an account
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      <footer className="border-t py-12 bg-background">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <span className="text-lg font-bold">SkillBridge</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Empowering rural India with AI-powered education and skill development.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Platform</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Courses</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Skill Paths</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Mentors</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Certificates</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Support</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">AI Assistant</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Community</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Cookie Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>&copy; 2026 SkillBridge. Empowering rural India through AI-powered education.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
