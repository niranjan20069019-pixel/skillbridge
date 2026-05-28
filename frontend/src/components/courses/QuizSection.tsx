import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle2, XCircle, ArrowRight, RotateCcw, Trophy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/utils/cn'

interface Question {
  id: number
  question: string
  options: string[]
  correct: number
}

interface QuizSectionProps {
  questions: Question[]
  title?: string
}

export function QuizSection({ questions, title = 'Course Quiz' }: QuizSectionProps) {
  const [currentQ, setCurrentQ] = useState(0)
  const [selected, setSelected] = useState<number | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [score, setScore] = useState(0)
  const [answers, setAnswers] = useState<number[]>([])
  const [finished, setFinished] = useState(false)

  const handleAnswer = (idx: number) => {
    if (showResult) return
    setSelected(idx)
  }

  const confirmAnswer = () => {
    if (selected === null) return
    const correct = selected === questions[currentQ].correct
    if (correct) setScore(s => s + 1)
    setAnswers(prev => [...prev, selected])
    setShowResult(true)
  }

  const nextQuestion = () => {
    if (currentQ < questions.length - 1) {
      setCurrentQ(c => c + 1)
      setSelected(null)
      setShowResult(false)
    } else {
      setFinished(true)
    }
  }

  const resetQuiz = () => {
    setCurrentQ(0)
    setSelected(null)
    setShowResult(false)
    setScore(0)
    setAnswers([])
    setFinished(false)
  }

  if (finished) {
    const percentage = Math.round((score / questions.length) * 100)
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center py-8"
      >
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-amber-500 to-orange-500 shadow-lg mb-4">
          <Trophy className="h-8 w-8 text-white" />
        </div>
        <h3 className="text-xl font-bold mb-1">Quiz Complete!</h3>
        <p className="text-3xl font-bold text-primary mb-2">{score}/{questions.length}</p>
        <p className="text-muted-foreground mb-6">
          {percentage >= 80 ? 'Excellent work!' : percentage >= 50 ? 'Good effort!' : 'Keep practicing!'}
        </p>
        <div className="w-full bg-muted rounded-full h-2 mb-6 max-w-xs mx-auto">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            className={cn(
              'h-full rounded-full',
              percentage >= 80 ? 'bg-emerald-500' : percentage >= 50 ? 'bg-amber-500' : 'bg-red-500'
            )}
          />
        </div>
        <div className="space-y-2 text-left max-w-md mx-auto mb-6">
          {questions.map((q, i) => (
            <div key={q.id} className="flex items-start gap-2 text-sm p-2 rounded-lg bg-muted/30">
              {answers[i] === q.correct ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="h-4 w-4 text-red-500 shrink-0 mt-0.5" />
              )}
              <span className="text-muted-foreground">{q.question}</span>
            </div>
          ))}
        </div>
        <Button onClick={resetQuiz} variant="outline" className="gap-2">
          <RotateCcw className="h-4 w-4" /> Retry Quiz
        </Button>
      </motion.div>
    )
  }

  const q = questions[currentQ]

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold text-sm">{title}</h4>
        <span className="text-sm text-muted-foreground tabular-nums">
          {currentQ + 1} / {questions.length}
        </span>
      </div>
      <div className="w-full bg-muted rounded-full h-1.5 mb-6">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${((currentQ + 1) / questions.length) * 100}%` }}
          className="h-full rounded-full bg-primary"
        />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentQ}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
        >
          <p className="font-medium mb-4">{q.question}</p>
          <div className="space-y-2">
            {q.options.map((opt, idx) => (
              <button
                key={idx}
                onClick={() => handleAnswer(idx)}
                disabled={showResult}
                className={cn(
                  'w-full text-left rounded-lg border p-3 text-sm transition-all',
                  selected === idx && !showResult && 'border-primary bg-primary/5 ring-1 ring-primary/20',
                  showResult && idx === q.correct && 'border-emerald-500 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
                  showResult && idx === selected && idx !== q.correct && 'border-red-500 bg-red-500/10 text-red-600 dark:text-red-400',
                  !showResult && 'hover:border-primary/50 hover:bg-muted/50'
                )}
              >
                <span className="font-medium mr-2 text-muted-foreground">
                  {String.fromCharCode(65 + idx)}.
                </span>
                {opt}
              </button>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="flex justify-between mt-6">
        <div />
        {!showResult ? (
          <Button onClick={confirmAnswer} disabled={selected === null} size="sm" className="gap-1">
            Check Answer <ArrowRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button onClick={nextQuestion} size="sm" className="gap-1">
            {currentQ < questions.length - 1 ? 'Next Question' : 'See Results'}
            <ArrowRight className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}
