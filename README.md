# SkillBridge — Digital Education & Upskilling Platform

> Bridging the gap between rural India and industry-ready skills.

---

## 📁 Project Structure

```
skillbridge/
├── app.py                  # Main Flask application
├── run.py                  # Cross-platform launcher
├── run.bat                 # Windows double-click launcher
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── instance/               # SQLite database (auto-created)
│   └── skillbridge.db
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Shared layout
│   ├── index.html          # Template A: Landing Page
│   ├── dashboard.html      # Template B: Student Dashboard
│   ├── learn.html          # Template C: Learning Interface
│   ├── courses.html        # Course listing page
│   ├── login.html          # Login form
│   └── register.html       # Registration form
└── static/                 # Static assets
    ├── css/
    ├── js/
    └── img/
```

---

## 🚀 Quick Start

### Option 1: Double-Click (Windows Only)
1. Install Python 3.8+ from https://python.org (check "Add Python to PATH")
2. Double-click `run.bat`
3. Open http://localhost:5000 in your browser

---

### Option 2: Python Launcher (Windows & Linux)
```bash
python run.py
```

---

### Option 3: Manual Setup

#### 🐧 Linux (Ubuntu/Mint)
```bash
# Clone or extract project
cd skillbridge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

#### 🪟 Windows (PowerShell)
```powershell
# Navigate to project
cd skillbridge

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

#### 🪟 Windows (Command Prompt)
```cmd
cd skillbridge
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

---

## 🌐 Access the Application

Once running, open: **http://localhost:5000**

| Page | URL |
|------|-----|
| Landing Page | http://localhost:5000/ |
| Register | http://localhost:5000/register |
| Login | http://localhost:5000/login |
| Dashboard | http://localhost:5000/dashboard |
| All Courses | http://localhost:5000/courses |
| Learning Interface | http://localhost:5000/learn/1 |

---

## ✨ Features

### Frontend (3 Professional Templates)
- **Template A — Landing Page**: Hero, mission stats, category grid, testimonials, CTA
- **Template B — Student Dashboard**: Sidebar nav, enrolled courses, skill progress bars, AI recommendations, peer mentor chat
- **Template C — Learning Interface**: YouTube video player, module sidebar, tabs (Overview/Resources/Notes/Q&A), progress tracking

### Backend (Flask + SQLite)
- User authentication (register/login/logout with hashed passwords)
- Course catalog with 6 seeded courses across 5 categories
- Enrollment system with progress tracking
- AI skill recommendation engine (interest-based)
- Peer mentor chat API
- Cross-platform path handling with `os.path.join`

### Database Models
- **User**: name, email, password_hash, interest, location, joined_at
- **Course**: title, description, category, level, duration, instructor, youtube_id, modules (JSON)
- **Enrollment**: user_id, course_id, progress (0-100), enrolled_at

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recommend` | AI skill recommendations for current user |
| POST | `/api/progress/<course_id>` | Update course progress |
| POST | `/api/chat` | Peer mentor chat response |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.8+, Flask 3.0, Flask-SQLAlchemy, Flask-Login |
| Database | SQLite (zero-config, cross-platform) |
| Frontend | HTML5, Tailwind CSS (CDN), Vanilla JS |
| Fonts | Google Fonts: Syne + DM Sans |
| Video | YouTube Embed API |
| Auth | Werkzeug password hashing |

---

## 📝 Demo Accounts
Register any new account — the system auto-enrolls you in a course matching your interest.

---

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Linux
lsof -ti:5000 | xargs kill -9
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Module not found:**
```bash
pip install -r requirements.txt --force-reinstall
```

**Database issues:**
```bash
# Delete and recreate
rm instance/skillbridge.db
python app.py
```

---

## 📄 License
Built for the Digital Education Hackathon. MIT License.
