# SkillBridge — AI-Powered Education Platform

> Bridging the skill gap with AI guidance. Built for rural India, powered by Gemini AI.

---

## Architecture

```
skillbridge/
├── frontend/          # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/  # UI & feature components
│   │   ├── pages/       # Route pages
│   │   ├── hooks/       # Custom React hooks
│   │   ├── context/     # React context providers
│   │   ├── services/    # API service layer
│   │   ├── utils/       # Utility functions
│   │   └── styles/      # Global CSS
│   └── package.json
├── backend/           # Node.js + Express API
│   ├── src/
│   │   ├── routes/     # API route handlers
│   │   ├── services/   # Gemini & OpenAI integrations
│   │   └── utils/      # Logger, helpers
│   └── package.json
└── README.md
```

---

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- (Optional) Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- (Optional) OpenAI API key from [OpenAI](https://platform.openai.com/api-keys)

### 1. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env and add your API keys (optional — app works with fallback)
npm install
npm run dev
```

The API server starts at **http://localhost:3001**

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend starts at **http://localhost:5173**

---

## API Key Configuration

Create `backend/.env` with:

```env
PORT=3001
FRONTEND_URL=http://localhost:5173

# Option 1: Google Gemini API (Recommended — Free tier available)
GEMINI_API_KEY=your_gemini_api_key

# Option 2: OpenAI API (Paid)
OPENAI_API_KEY=your_openai_api_key
```

> Without any API key, the AI assistant uses intelligent fallback responses and translation shows a setup guide. For full AI features, at least one API key is recommended.

---

## Features

### Dashboard
- Modern glassmorphism UI with dark/light mode
- Course progress tracking with animated bars
- Weekly activity chart
- Quick action tiles (AI Assistant, Translator, Courses, Analytics)
- Learning streak tracker

### AI Assistant
- Gemini/OpenAI powered chat with multilingual support
- Voice input (browser SpeechRecognition)
- Markdown rendering for structured responses
- Chat history with copy support
- Quick suggestion chips
- Typing indicator animation
- Error fallback handling

### Language Translator
- Supports 8 Indian languages:
  - English, Hindi, Kannada, Tamil, Telugu, Malayalam, Marathi, Bengali
- Auto-detect source language
- Text-to-speech for input/output
- Copy translated text
- Quick language buttons

### Authentication
- Login/Register with field validation
- Session management with tokens
- Toast notifications for success/errors
- User profile dropdown menu

---

## Build for Production

```bash
cd frontend
npm run build
# Output in frontend/dist/

cd backend
npm start
```

---

## Tech Stack

| Frontend | Backend |
|----------|---------|
| React 18 | Node.js + Express |
| TypeScript | ESM Modules |
| Vite | Gemini API |
| Tailwind CSS | OpenAI API |
| Framer Motion | Rate Limiting |
| shadcn/ui | Winston Logger |
| Radix UI | CORS + Helmet |
| Axios | |

---

## Deployment

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy dist/ directory
```

### Backend (Render/Railway)
```bash
cd backend
npm start
# Set environment variables in dashboard
```

Ensure the frontend's `VITE_API_URL` points to your deployed backend URL.
