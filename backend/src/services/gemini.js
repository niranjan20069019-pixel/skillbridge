import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from '@google/generative-ai'
import { logger } from '../utils/logger.js'

const API_KEY = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY
const MODEL_NAME = 'gemini-2.0-flash'
const MAX_INPUT_TOKENS = 4000
const MAX_OUTPUT_TOKENS = 1024

const LANGUAGE_MAP = {
  en: 'English', hi: 'Hindi', kn: 'Kannada', ta: 'Tamil',
  te: 'Telugu', ml: 'Malayalam', mr: 'Marathi', bn: 'Bengali',
}
const LANG_CODES = new Set(Object.keys(LANGUAGE_MAP))

let genAI = null
let model = null

const safetySettings = [
  { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH },
  { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH },
  { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH },
  { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_ONLY_HIGH },
]

const generationConfig = {
  temperature: 0.7,
  topP: 0.95,
  topK: 40,
  maxOutputTokens: MAX_OUTPUT_TOKENS,
}

if (API_KEY) {
  try {
    genAI = new GoogleGenerativeAI(API_KEY)
    model = genAI.getGenerativeModel({
      model: MODEL_NAME,
      safetySettings,
      generationConfig,
    })
    logger.info('Gemini AI initialized successfully')
  } catch (err) {
    logger.error('Failed to initialize Gemini:', err.message)
  }
} else {
  logger.warn('No Gemini API key found - AI features will use fallback mode')
}

const SYSTEM_PROMPT = `You are SkillBridge AI — a supportive, expert educational assistant for Indian students, especially from rural areas.

## YOUR JOB
Help users learn, find courses, plan careers, prepare for exams, and navigate government schemes. Respond in whichever language the user writes to you.

## RESPONSE RULES
- Use **markdown** for structure (bold, lists, code blocks, tables)
- Keep responses **concise**: 2–4 short paragraphs or bullet lists
- Give **actionable steps**, not just theory
- Format lists with **bold labels** and clear separators
- If the user seems confused, ask one clarifying question
- Never invent specific URLs, scheme details, or legal info — tell them to verify on official sites
- For technical topics, include a brief code example or relatable analogy

## TOPICS YOU COVER
- Course & skill path recommendations (Technology, Marketing, Finance, Agriculture, Design, Healthcare)
- Career guidance and job readiness
- Exam preparation strategies
- Government education & skill schemes (PMKVY, NSP, etc.)
- Digital literacy and entrepreneurship
- Translating concepts between English and Indian languages

## TONE
Encouraging, patient, clear. Assume the user may be a first-time learner. Celebrate small wins.`

function trimHistory(history, maxTurns = 6) {
  if (!history || history.length <= maxTurns) return history || []
  return history.slice(history.length - maxTurns)
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function retryWithBackoff(fn, maxRetries = 2) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (err) {
      if (attempt === maxRetries) throw err
      if (err.message?.includes('SAFETY') || err.message?.includes('API_KEY')) throw err
      logger.warn(`Gemini retry ${attempt + 1}/${maxRetries}: ${err.message}`)
      await sleep(1000 * (attempt + 1))
    }
  }
}

export async function generateChatResponse(message, history = []) {
  if (!model) return fallbackResponse(message)

  try {
    const trimmed = trimHistory(history)
    const mapped = trimmed.map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content.slice(0, MAX_INPUT_TOKENS) }],
    }))

    const chat = model.startChat({
      history: mapped,
      systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
    })

    const result = await retryWithBackoff(() => chat.sendMessage(message.slice(0, MAX_INPUT_TOKENS)))
    return result.response.text()
  } catch (error) {
    return handleGeminiError(error, message)
  }
}

const FALLBACK_TRANSLATIONS = {
  hi: { hello: 'नमस्ते', how: 'कैसे', are: 'हैं', you: 'आप', thank: 'धन्यवाद', welcome: 'स्वागत', please: 'कृपया', help: 'मदद', yes: 'हाँ', no: 'नहीं' },
  kn: { hello: 'ನಮಸ್ಕಾರ', how: 'ಹೇಗೆ', are: 'ಇದ್ದೀರಿ', you: 'ನೀವು', thank: 'ಧನ್ಯವಾದಗಳು', welcome: 'ಸ್ವಾಗತ', please: 'ದಯವಿಟ್ಟು', help: 'ಸಹಾಯ', yes: 'ಹೌದು', no: 'ಇಲ್ಲ' },
  ta: { hello: 'வணக்கம்', how: 'எப்படி', are: 'இருக்கிறீர்கள்', you: 'நீங்கள்', thank: 'நன்றி', welcome: 'வரவேற்கிறோம்', please: 'தயவுசெய்து', help: 'உதவி', yes: 'ஆம்', no: 'இல்லை' },
  te: { hello: 'నమస్కారం', how: 'ఎలా', are: 'ఉన్నారు', you: 'మీరు', thank: 'ధన్యవాదాలు', welcome: 'స్వాగతం', please: 'దయచేసి', help: 'సహాయం', yes: 'అవును', no: 'కాదు' },
  ml: { hello: 'നമസ്കാരം', how: 'എങ്ങനെ', are: 'ആകുന്നു', you: 'നിങ്ങൾ', thank: 'നന്ദി', welcome: 'സ്വാഗതം', please: 'ദയവായി', help: 'സഹായം', yes: 'അതെ', no: 'ഇല്ല' },
  mr: { hello: 'नमस्कार', how: 'कसे', are: 'आहात', you: 'तुम्ही', thank: 'धन्यवाद', welcome: 'स्वागत', please: 'कृपया', help: 'मदत', yes: 'होय', no: 'नाही' },
  bn: { hello: 'নমস্কার', how: 'কেমন', are: 'আছেন', you: 'আপনি', thank: 'ধন্যবাদ', welcome: 'স্বাগতম', please: 'অনুগ্রহ', help: 'সাহায্য', yes: 'হ্যাঁ', no: 'না' },
}

function fallbackTranslate(text, sourceLang, targetLang) {
  if (targetLang === 'en') return text
  const dict = FALLBACK_TRANSLATIONS[targetLang]
  if (!dict) return null
  const words = text.split(/\s+/)
  let changed = false
  const translated = words.map(w => {
    const clean = w.replace(/[^\w]/g, '').toLowerCase()
    const punctPrefix = w.match(/^\W+/)
    const punctSuffix = w.match(/\W+$/)
    if (dict[clean]) {
      changed = true
      return (punctPrefix ? punctPrefix[0] : '') + dict[clean] + (punctSuffix ? punctSuffix[0] : '')
    }
    return w
  }).join(' ')
  return changed ? translated : null
}

export async function translateText(text, sourceLang, targetLang) {
  if (!model) return null

  const src = LANGUAGE_MAP[sourceLang] || sourceLang
  const tgt = LANGUAGE_MAP[targetLang] || targetLang

  const prompt = `Translate from ${src} to ${tgt}.

Rules:
- Output ONLY the translation
- Preserve meaning, tone, and line breaks
- If already ${tgt}, return as-is

Text:
${text.slice(0, MAX_INPUT_TOKENS)}

Translation:`

  try {
    const result = await retryWithBackoff(() => model.generateContent(prompt), 1)
    const translated = result.response.text().trim().replace(/^["']|["']$/g, '')
    if (translated) return translated
    return fallbackTranslate(text, sourceLang, targetLang)
  } catch (error) {
    logger.warn('Gemini translation unavailable, using fallback:', error.message)
    return fallbackTranslate(text, sourceLang, targetLang)
  }
}

const COMMON_WORDS = {
  en: [/^(the|a|an|is|are|am|i|you|he|she|it|we|they|this|that|these|those)/i],
  hi: [/^(है|हैं|का|की|के|में|से|को|पर|और|एक|यह|वह|मैं|हम|तुम|आप)/],
  kn: [/^(ಇದು|ಅದು|ನಾನು|ನಾವು|ನೀವು|ಅವನು|ಅವಳು|ಅವರು|ಮತ್ತು|ಒಂದು)/],
  ta: [/^(இது|அது|நான்|நாங்கள்|நீங்கள்|அவன்|அவள்|அவர்கள்|மற்றும்|ஒரு)/],
  te: [/^(ఇది|అది|నేను|మేము|మీరు|అతను|ఆమె|వారు|మరియు|ఒక)/],
  ml: [/^(ഇത്|അത്|ഞാൻ|നാം|നിങ്ങൾ|അവൻ|അവൾ|അവർ|ഉം|ഒരു)/],
  mr: [/^(हे|ही|ते|मी|आम्ही|तुम्ही|तो|ती|ते|आणि|एक)/],
  bn: [/^(এটি|সেটি|আমি|আমরা|তুমি|সে|সে|তারা|এবং|এক)/],
}

function simpleDetect(text) {
  for (const [code, patterns] of Object.entries(COMMON_WORDS)) {
    if (patterns.some(p => p.test(text.trim()))) return code
  }
  return null
}

export async function detectLanguage(text) {
  if (!model) return simpleDetect(text) || 'en'

  const prompt = `Identify the language of this text. Return ONLY the 2-letter code from: en, hi, kn, ta, te, ml, mr, bn.

Text: ${text.slice(0, 300)}

Code:`

  try {
    const result = await model.generateContent(prompt)
    const code = result.response.text().trim().toLowerCase().slice(0, 2)
    return LANG_CODES.has(code) ? code : simpleDetect(text) || 'en'
  } catch {
    return simpleDetect(text) || 'en'
  }
}

function handleGeminiError(err, originalMessage) {
  const msg = err.message || ''

  if (msg.includes('SAFETY')) {
    return 'I apologise, but I cannot respond to that. Please ask a learning-related question (courses, careers, study tips, etc.).'
  }
  if (msg.includes('API_KEY') || msg.includes('not found')) {
    return '⚠️ Gemini API key is missing or invalid. Set a valid `GEMINI_API_KEY` in backend/.env and restart the server.'
  }
  if (msg.includes('quota') || msg.includes('rate')) {
    return '⚠️ API rate limit reached. Please wait a moment and try again.'
  }
  if (msg.includes('timeout') || msg.includes('network')) {
    return '⚠️ Network issue reaching the AI service. Please check your internet and try again.'
  }

  return fallbackResponse(originalMessage)
}

function fallbackResponse(message) {
  const lower = message.toLowerCase()

  if (/^(hey|hello|hi\b|namaste|namaskar|good\s*(morning|afternoon|evening))/.test(lower)) {
    return `Namaste! 👋 I'm SkillBridge AI.

I can help you find courses, plan careers, prepare for exams, and learn about government schemes. Ask in English, Hindi, Kannada, Tamil, or any language!

What would you like to explore?`
  }

  if (/\b(course|learn|study|recommend|suggest|train)\b/.test(lower)) {
    if (/\b(python|code|program|javascript|react|web)\b/.test(lower)) {
      return `**Programming courses available:**

🐍 **Python for Beginners** — 8 weeks — perfect start
🌐 **Web Development** — HTML/CSS → JS → React (16 weeks)
📊 **Data Science Fundamentals** — 12 weeks

*Tip:* Start with Python if you're new. Which one interests you?`
    }
    if (/\b(data|analytics|sql|machine.?learn)\b/.test(lower)) {
      return `**Data & Analytics courses:**

📊 **Data Science Fundamentals** — 12 wks — Python, Stats, ML
📈 **Data Analyst Path** — 3 mo — SQL, Viz, Python
💰 **Financial Analyst** — 4 mo — Excel, Accounting

Which path sounds right for you?`
    }
    return `**Available categories:** Technology, Marketing, Finance, Agriculture, Design, Healthcare.

Reply with a category name and I'll recommend specific courses.`
  }

  if (/\b(skill.?path|career|job|salary|lpa)\b/.test(lower)) {
    return `**Career Skill Paths:**

1. 🥇 **Data Scientist** (6 mo) → ₹6–12 LPA — 4 projects
2. 🥈 **Web Developer** (5 mo) → ₹4–8 LPA — 5 projects
3. 🥉 **Digital Marketer** (4 mo) → ₹3–6 LPA — 3 projects
4. 💰 **Financial Analyst** (4 mo) → ₹4–7 LPA — 3 projects

Each includes mentor support, quizzes, and a certificate. Which one fits your goal?`
  }

  if (/\b(mentor|doubt|help|support|guide)\b/.test(lower)) {
    return `**Mentor support is available** for 1-on-1 sessions, doubt solving, career advice, and project reviews.

Visit the **Mentors** page in the sidebar to book a session.`
  }

  if (/\b(translate|language|hindi|kannada|tamil|telugu)\b/.test(lower)) {
    return `🌐 We support **8 languages**: Hindi, Kannada, Tamil, Telugu, Malayalam, Marathi, Bengali, English.

Use the **Translator** tool in the sidebar to convert text between any of these. You can also ask me questions in your mother tongue!`
  }

  if (/\b(government|scheme|scholarship|subsidy|pmkvy|nsp)\b/.test(lower)) {
    return `**Major education schemes:**

📋 **National Scholarship Portal** — SC/ST/OBC/EWS scholarships
🎓 **Pragati** — Girls in technical education
🔧 **PMKVY** — Free skill training & certification
💼 **DDU-GKY** — Rural youth employment

Check official websites for the latest details. Want to know more about a specific scheme?`
  }

  if (/\b(exam|test|quiz|prepare|strategy|tip)\b/.test(lower)) {
    return `**Exam tips:**

1. 📅 Study 2 hrs daily — consistency beats cramming
2. 🎯 Focus on weak areas first
3. 🔁 Revise within 24 hrs, then at 1 week
4. 💪 Use SkillBridge quizzes to test yourself

Which subject or exam are you preparing for?`
  }

  return `I'm your SkillBridge AI. Ask me about:

📚 **Courses** — "recommend a course for beginners"
🛤️ **Careers** — "which skill path is best for me"
👨‍🏫 **Study tips** — "how to prepare for exams"
🌐 **Translation** — "translate this to Kannada"
🏛️ **Schemes** — "tell me about education schemes"

What would you like help with? 😊`
}
