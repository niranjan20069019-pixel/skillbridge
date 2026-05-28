import { motion } from 'framer-motion'
import {
  Languages,
  ArrowRightLeft,
  Copy,
  Check,
  Volume2,
  Sparkles,
  Loader2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useTranslation, LANGUAGES, type LanguageCode, type SourceLanguageCode } from '@/hooks/useTranslation'
import { useState } from 'react'

export default function Translator() {
  const {
    sourceLang,
    targetLang,
    inputText,
    translatedText,
    isTranslating,
    error,
    setSourceLang,
    setTargetLang,
    setInputText,
    translate,
    swapLanguages,
  } = useTranslation()

  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(translatedText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {}
  }

  const handleSpeak = (text: string, lang: string) => {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang === 'en' ? 'en-IN' : lang
    speechSynthesis.speak(utterance)
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 max-w-4xl mx-auto pb-8"
    >
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 p-2.5 shadow-lg">
            <Languages className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Language Translator</h1>
            <p className="text-muted-foreground">
              Translate between 8 Indian languages powered by AI
            </p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="overflow-hidden border-0 shadow-md bg-gradient-to-br from-card to-muted/30">
          <CardContent className="p-6 md:p-8 space-y-6">
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="gap-1">
                <Sparkles className="h-3 w-3" />
                AI Powered
              </Badge>
              {sourceLang !== 'auto' && (
                <Badge variant="outline" className="text-[10px]">
                  Auto-detect ON
                </Badge>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-[1fr,auto,1fr] gap-4 items-start">
              <div className="space-y-3">
                <Select value={sourceLang} onValueChange={(v: SourceLanguageCode) => setSourceLang(v)}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Source language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">🔍 Auto Detect</SelectItem>
                    {LANGUAGES.map((lang) => (
                      <SelectItem key={lang.code} value={lang.code}>
                        {lang.native} ({lang.name})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="relative">
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Enter text to translate..."
                    className="min-h-[180px] w-full rounded-xl border border-input bg-background/50 p-4 text-sm resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring placeholder:text-muted-foreground transition-all"
                    rows={6}
                  />
                  <div className="absolute bottom-3 right-3 flex gap-1">
                    {inputText && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => handleSpeak(inputText, sourceLang === 'auto' ? 'en' : sourceLang)}
                      >
                        <Volume2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex md:flex-col items-center justify-center gap-2 pt-8">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={swapLanguages}
                  disabled={sourceLang === 'auto'}
                  className="rounded-full h-10 w-10 border-2 hover:bg-primary/5 hover:border-primary/30 transition-all"
                >
                  <ArrowRightLeft className="h-4 w-4" />
                </Button>
                <Button
                  onClick={() => translate()}
                  disabled={!inputText.trim() || isTranslating}
                  className="gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
                >
                  {isTranslating ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Languages className="h-4 w-4" />
                  )}
                  Translate
                </Button>
              </div>

              <div className="space-y-3">
                <Select value={targetLang} onValueChange={(v: LanguageCode) => setTargetLang(v)}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Target language" />
                  </SelectTrigger>
                  <SelectContent>
                    {LANGUAGES.map((lang) => (
                      <SelectItem key={lang.code} value={lang.code}>
                        {lang.native} ({lang.name})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="relative">
                  <div className="min-h-[180px] w-full rounded-xl border bg-background/30 p-4 text-sm transition-all">
                    {isTranslating ? (
                      <div className="flex items-center gap-2 text-muted-foreground h-full">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Translating...</span>
                      </div>
                    ) : translatedText ? (
                      <p className="leading-relaxed">{translatedText}</p>
                    ) : (
                      <p className="text-muted-foreground/60">Translation will appear here...</p>
                    )}
                  </div>
                  {translatedText && (
                    <div className="absolute bottom-3 right-3 flex gap-1">
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleCopy}>
                        {copied ? (
                          <Check className="h-4 w-4 text-emerald-500" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => handleSpeak(translatedText, targetLang)}
                      >
                        <Volume2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {error && (
              <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20">
                {error}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {LANGUAGES.filter(l => l.code !== 'en').map((lang, i) => (
          <motion.button
            key={lang.code}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.05 }}
            onClick={() => {
              setTargetLang(lang.code)
              if (inputText) translate(inputText, sourceLang === 'auto' ? undefined : sourceLang, lang.code)
            }}
            className={`rounded-xl border p-4 text-center transition-all hover:border-primary/50 hover:bg-muted/50 hover:shadow-sm ${
              targetLang === lang.code ? 'border-primary bg-primary/5 ring-1 ring-primary/20' : ''
            }`}
          >
            <p className="text-lg font-semibold">{lang.native}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{lang.name}</p>
          </motion.button>
        ))}
      </div>
    </motion.div>
  )
}
