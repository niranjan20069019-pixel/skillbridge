import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@/context/ThemeContext'
import { AuthProvider } from '@/context/AuthContext'
import { AppLayout } from '@/components/layout/AppLayout'
import { lazy, Suspense } from 'react'
import { ToastContainer } from '@/components/ui/toast'

const Landing = lazy(() => import('@/pages/Landing'))
const Login = lazy(() => import('@/pages/Login'))
const Register = lazy(() => import('@/pages/Register'))
const Dashboard = lazy(() => import('@/pages/Dashboard'))
const AiAssistant = lazy(() => import('@/pages/AiAssistant'))
const Translator = lazy(() => import('@/pages/Translator'))
const Courses = lazy(() => import('@/pages/Courses'))
const SkillPaths = lazy(() => import('@/pages/SkillPaths'))
const Mentors = lazy(() => import('@/pages/Mentors'))
const Gamification = lazy(() => import('@/pages/Gamification'))
const Analytics = lazy(() => import('@/pages/Analytics'))

function LoadingFallback() {
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <ToastContainer />
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route element={<AppLayout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/ai-assistant" element={<AiAssistant />} />
                <Route path="/translator" element={<Translator />} />
                <Route path="/courses" element={<Courses />} />
                <Route path="/skill-paths" element={<SkillPaths />} />
                <Route path="/mentors" element={<Mentors />} />
                <Route path="/gamification" element={<Gamification />} />
                <Route path="/analytics" element={<Analytics />} />
              </Route>
            </Routes>
          </Suspense>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}
