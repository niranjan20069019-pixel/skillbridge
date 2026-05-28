import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Brain, ArrowRight, Sparkles, Lightbulb, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const suggestions = [
  'What courses should I take for web development?',
  'How do I start learning data science?',
  'Explain blockchain technology simply',
  'What government schemes help rural students?',
]

export function AiHelpWidget() {
  const navigate = useNavigate()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.4 }}
      className="relative overflow-hidden rounded-xl border bg-gradient-to-br from-primary/5 via-primary/0 to-purple-500/5 p-6"
    >
      <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-primary/10 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="rounded-xl p-2.5 bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold flex items-center gap-2">
              AI Assistant
              <Badge variant="success" className="text-[10px] px-1.5 py-0">Gemini</Badge>
            </h3>
            <p className="text-xs text-muted-foreground">Ask me anything about learning</p>
          </div>
        </div>

        <div className="space-y-1.5 mb-4">
          {suggestions.map((text, i) => (
            <button
              key={i}
              onClick={() => navigate('/ai-assistant')}
              className="w-full text-left flex items-center gap-2.5 rounded-lg p-2.5 text-sm text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-all group"
            >
              <Lightbulb className="h-4 w-4 shrink-0 text-amber-500" />
              <span className="flex-1 truncate">{text}</span>
              <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
            </button>
          ))}
        </div>

        <Button
          variant="default"
          size="sm"
          className="w-full gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
          onClick={() => navigate('/ai-assistant')}
        >
          <Sparkles className="h-4 w-4" />
          Open AI Assistant
        </Button>
      </div>
    </motion.div>
  )
}
