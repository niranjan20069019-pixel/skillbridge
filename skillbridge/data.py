"""data.py — All static data constants, seed data, and helper functions for SkillBridge.
Self-contained module (no broken imports from app.py)."""
import json

SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "हिन्दी", "kn": "ಕನ್ನಡ",
    "ta": "தமிழ்", "te": "తెలుగు", "bn": "বাংলা",
    "mr": "मराठी", "gu": "ગુજરાતી",
}

SUBTITLE_LANGS = {"en": "en", "hi": "hi", "kn": "kn", "ta": "ta", "te": "te",
                  "bn": "bn", "mr": "mr", "gu": "gu"}

NEXT_STEP_MSG = {
    "en": "Next step: **{title}** — {desc}",
    "hi": "अगला कदम: **{title}** — {desc}",
    "kn": "ಮುಂದಿನ ಹೆಜ್ಜೆ: **{title}** — {desc}",
    "ta": "அடுத்த படி: **{title}** — {desc}",
    "te": "తదుపరి దశ: **{title}** — {desc}",
}

I18N = {
    "next_step": {"en": "Next Step", "hi": "अगला कदम", "kn": "ಮುಂದಿನ ಹೆಜ್ಜೆ",
                  "ta": "அடுத்த படி", "te": "తదుపరి దశ"},
    "step_done": {"en": "All steps completed! 🎉", "hi": "सभी चरण पूर्ण! 🎉",
                  "kn": "ಎಲ್ಲ ಹಂತಗಳು ಪೂರ್ಣಗೊಂಡಿವೆ! 🎉",
                  "ta": "அனைத்து படிகளும் முடிந்தன! 🎉",
                  "te": "అన్ని దశలు పూర్తయ్యాయి! 🎉"},
    "start": {"en": "Start", "hi": "शुरू करें", "kn": "ಪ್ರಾರಂಭಿಸಿ",
              "ta": "தொடங்கு", "te": "ప్రారంభించు"},
    "continue_learning": {"en": "Continue", "hi": "जारी रखें", "kn": "ಮುಂದುವರಿಸಿ",
                          "ta": "தொடரவும்", "te": "కొనసాగించు"},
    "review": {"en": "Review", "hi": "समीक्षा", "kn": "ಪುನರ್ ವೀಕ್ಷಿಸಿ",
               "ta": "மறுபார்வை", "te": "సమీక్ష"},
    "back": {"en": "Back", "hi": "वापस", "kn": "ಹಿಂತಿರುಗಿ", "ta": "பின்", "te": "వెనుక"},
    "skill_paths": {"en": "Skill Paths", "hi": "कौशल पथ", "kn": "ಕೌಶಲ್ಯ ಮಾರ್ಗಗಳು", "ta": "திறன் பாதைகள்", "te": "నైపుణ్య మార్గాలు"},
    "enrolled": {"en": "Enrolled", "hi": "नामांकित", "kn": "ನೋಂದಾಯಿಸಲಾಗಿದೆ", "ta": "பதிவு செய்யப்பட்டது", "te": "నమోదు చేయబడింది"},
    "career_outcomes": {"en": "Career Outcomes", "hi": "करियर परिणाम", "kn": "ವೃತ್ತಿ ಫಲಿತಾಂಶಗಳು", "ta": "தொழில் விளைவுகள்", "te": "కెరీర్ ఫలితాలు"},
    "progress": {"en": "Progress", "hi": "प्रगति", "kn": "ಪ್ರಗತಿ", "ta": "முன்னேற்றம்", "te": "పురోగతి"},
    "steps_completed": {"en": "completed", "hi": "पूर्ण", "kn": "ಪೂರ್ಣಗೊಂಡಿದೆ", "ta": "முடிந்தது", "te": "పూర్తయింది"},
    "start_path": {"en": "Start Path", "hi": "पथ शुरू करें", "kn": "ಮಾರ್ಗ ಪ್ರಾರಂಭಿಸಿ", "ta": "பாதையைத் தொடங்கு", "te": "మార్గాన్ని ప్రారంభించండి"},
    "next_rec": {"en": "Next Recommendation", "hi": "अगली अनुशंसा", "kn": "ಮುಂದಿನ ಶಿಫಾರಸು", "ta": "அடுத்த பரிந்துரை", "te": "తదుపరి సిఫార్సు"},
    "notes": {"en": "Notes", "hi": "नोट्स", "kn": "ಟಿಪ್ಪಣಿಗಳು", "ta": "குறிப்புகள்", "te": "గమనికలు"},
    "subtitles": {"en": "Subtitles", "hi": "उपशीर्षक", "kn": "ಉಪಶೀರ್ಷಿಕೆಗಳು", "ta": "வசனங்கள்", "te": "ఉపశీర్షికలు"},
    "subtitle_hint": {"en": "Enable subtitles in the video player for translated captions.", "hi": "अनुवादित कैप्शन के लिए वीडियो प्लेयर में उपशीर्षक सक्षम करें।", "kn": "ಅನುವಾದಿಸಿದ ಶೀರ್ಷಿಕೆಗಳಿಗಾಗಿ ವೀಡಿಯೊ ಪ್ಲೇಯರ್‌ನಲ್ಲಿ ಉಪಶೀರ್ಷಿಕೆಗಳನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಿ.", "ta": "மொழிபெயர்க்கப்பட்ட வசனங்களுக்கு வீடியோ பிளேயரில் வசனங்களை இயக்கவும்.", "te": "అనువదించిన శీర్షికల కోసం వీడియో ప్లేయర్‌లో ఉపశీర్షికలను ప్రారంభించండి."},
    "learning_roadmap": {"en": "Learning Roadmap", "hi": "सीखने का रोडमैप", "kn": "ಕಲಿಕೆಯ ರೋಡ್ಮ್ಯಾಪ್", "ta": "கற்றல் வரைபடம்", "te": "లెర్నింగ్ రోడ్మ్యాప్"},
    "milestone": {"en": "Milestone", "hi": "माइलस्टोन", "kn": "ಮೈಲಿಗಲ್ಲು", "ta": "மைல்கல்", "te": "మైలురాయి"},
    "locked": {"en": "Locked", "hi": "बंद", "kn": "ಲಾಕ್ ಮಾಡಲಾಗಿದೆ", "ta": "பூட்டப்பட்டது", "te": "లాక్ చేయబడింది"},
    "lessons": {"en": "Lessons", "hi": "पाठ", "kn": "ಪಾಠಗಳು", "ta": "பாடங்கள்", "te": "పాఠాలు"},
    "view_course": {"en": "View Course", "hi": "कोर्स देखें", "kn": "ಕೋರ್ಸ್ ವೀಕ್ಷಿಸಿ", "ta": "பாடத்தைப் பார்", "te": "కోర్స్‌ను చూడండి"},
    "quick_quiz": {"en": "Quick Quiz", "hi": "त्वरित प्रश्नोत्तरी", "kn": "ತ್ವರಿತ ಕ್ವಿಜ್", "ta": "விரைவு வினாடி வினா", "te": "శీఘ్ర క్విజ్"},
    "mark_complete": {"en": "Mark Complete", "hi": "पूर्ण चिह्नित करें", "kn": "ಪೂರ್ಣಗೊಂಡಿದೆ ಎಂದು ಗುರುತಿಸಿ", "ta": "நிறைவு செய்", "te": "పూర్తి చేసినట్లు గుర్తు"},
    "correct": {"en": "✓ Correct!", "hi": "✓ सही!", "kn": "✓ ಸರಿ!", "ta": "✓ சரி!", "te": "✓ సరైనది!"},
    "incorrect": {"en": "✗ Incorrect", "hi": "✗ गलत", "kn": "✗ ತಪ್ಪು", "ta": "✗ தவறு", "te": "✗ తప్పు"},
}

SKILL_RECOMMENDATIONS = {
    "Technology": [
        "Python for Data Science", "Web Development with React",
        "JavaScript Fundamentals", "Cloud Computing with AWS",
        "Machine Learning Basics",
    ],
    "Programming": [
        "Python for Data Science", "JavaScript Fundamentals",
        "Web Development with React", "C++ Programming",
        "Mobile App Development",
    ],
    "Marketing": [
        "Digital Marketing 101", "SEO & Content Strategy",
        "Social Media Marketing", "Email Marketing",
        "Brand Management",
    ],
    "Finance": [
        "Financial Literacy", "GST & Taxation Basics",
        "Personal Finance Management", "Investment Banking 101",
        "Accounting with Tally",
    ],
    "Agriculture": [
        "AgriTech & Smart Farming", "Organic Farming Methods",
        "Drip Irrigation Systems", "Crop Management",
        "Agricultural Economics",
    ],
    "Language": [
        "English Communication", "Business English",
        "Hindi for Professionals", "Spoken English",
        "Technical Writing",
    ],
    "Healthcare": [
        "First Aid & Emergency Care", "Nutrition & Wellness",
        "Community Health Worker Training", "Mental Health Awareness",
        "Hospital Administration",
    ],
    "Design": [
        "UI/UX Design Fundamentals", "Graphic Design with Canva",
        "Video Editing Basics", "Figma for Beginners",
        "Design Thinking",
    ],
}

SKILL_PATHS = [
    {
        "slug": "data-scientist",
        "title": "Data Scientist",
        "icon": "📊",
        "color": "#3b82f6",
        "level": "Intermediate",
        "duration": "6 months",
        "description": "Master data analysis, ML, and visualization to become a job-ready data scientist.",
        "skills": "Python, Statistics, ML, SQL, Visualization",
        "jobs": ["Data Scientist", "ML Engineer", "AI Researcher"],
        "steps": [
            {"title": "Python Fundamentals", "description": "Learn Python basics: variables, loops, functions", "milestone": False, "duration": "2 weeks", "lessons": ["Variables & Data Types", "Loops & Conditionals", "Functions & Modules"], "course": "Python for Data Science", "quiz": [{"q": "What is a list comprehension?", "options": ["Loop shorthand", "Function definition", "Error handler", "Type converter"], "answer": 0}, {"q": "What keyword defines a function?", "options": ["func", "define", "def", "lambda"], "answer": 2}]},
            {"title": "Data Analysis with Pandas", "description": "Manipulate and analyze data using Pandas", "milestone": False, "duration": "3 weeks", "lessons": ["Series & DataFrames", "Filtering & Grouping", "Merging Datasets"], "course": "Python for Data Science", "quiz": [{"q": "Which method reads a CSV?", "options": ["load_csv()", "read_csv()", "open_csv()", "import_csv()"], "answer": 1}]},
            {"title": "Data Visualization", "description": "Create charts and dashboards with Matplotlib/Seaborn", "milestone": True, "duration": "2 weeks", "lessons": ["Line & Bar Charts", "Heatmaps & Subplots", "Interactive Dashboards"], "course": "Data Visualization", "quiz": [{"q": "Which library is built on Matplotlib?", "options": ["Plotly", "Seaborn", "Bokeh", "Ggplot"], "answer": 1}]},
            {"title": "SQL for Data Science", "description": "Query databases and extract insights", "milestone": False, "duration": "2 weeks", "lessons": ["SELECT & WHERE", "JOINs & Subqueries", "Aggregation & Grouping"], "course": "SQL for Data Science", "quiz": []},
            {"title": "Machine Learning Basics", "description": "Build predictive models with scikit-learn", "milestone": True, "duration": "4 weeks", "lessons": ["Supervised Learning", "Unsupervised Learning", "Model Evaluation"], "course": "Machine Learning Basics", "quiz": [{"q": "Which metric is used for classification?", "options": ["MSE", "Accuracy", "RMSE", "R-squared"], "answer": 1}]},
            {"title": "Capstone Project", "description": "Apply all skills to a real-world dataset", "milestone": True, "duration": "4 weeks", "lessons": ["Problem Definition", "Data Wrangling", "Modeling & Presentation"], "course": "", "quiz": []},
        ],
    },
    {
        "slug": "web-developer",
        "title": "Web Developer",
        "icon": "💻",
        "color": "#a855f7",
        "level": "Beginner",
        "duration": "5 months",
        "description": "Build modern web applications from scratch — frontend to backend.",
        "skills": "HTML, CSS, JavaScript, React, Flask, Databases",
        "jobs": ["Frontend Developer", "Backend Developer", "Full-Stack Engineer"],
        "steps": [
            {"title": "HTML & CSS", "description": "Structure and style web pages", "milestone": False, "duration": "2 weeks", "lessons": ["HTML Tags & Semantics", "CSS Selectors & Box Model", "Flexbox & Grid"], "course": "Web Development with React", "quiz": [{"q": "Which CSS property makes a layout flexible?", "options": ["display: block", "display: flex", "display: inline", "position: absolute"], "answer": 1}]},
            {"title": "JavaScript Essentials", "description": "Add interactivity and logic to websites", "milestone": False, "duration": "3 weeks", "lessons": ["Variables & Functions", "DOM Manipulation", "Async & Fetch"], "course": "Web Development with React", "quiz": [{"q": "Which keyword declares a constant?", "options": ["let", "var", "const", "static"], "answer": 2}]},
            {"title": "Frontend Frameworks (React)", "description": "Build dynamic UIs with React", "milestone": True, "duration": "4 weeks", "lessons": ["JSX & Components", "State & Props", "Hooks & Effects"], "course": "Web Development with React", "quiz": []},
            {"title": "Backend with Flask", "description": "Create REST APIs and server logic", "milestone": False, "duration": "3 weeks", "lessons": ["Routes & Views", "Templates & Forms", "REST APIs"], "course": "Web Development with React", "quiz": [{"q": "What decorator creates a route in Flask?", "options": ["@app.url()", "@app.route()", "@app.get()", "@app.endpoint()"], "answer": 1}]},
            {"title": "Databases & SQL", "description": "Design and query relational databases", "milestone": False, "duration": "2 weeks", "lessons": ["Schema Design", "CRUD Operations", "ORM with SQLAlchemy"], "course": "", "quiz": []},
            {"title": "Full-Stack Project", "description": "Build and deploy a complete web app", "milestone": True, "duration": "4 weeks", "lessons": ["Planning & Architecture", "Implementation", "Deployment"], "course": "", "quiz": []},
        ],
    },
    {
        "slug": "digital-marketer",
        "title": "Digital Marketing Specialist",
        "icon": "📣",
        "color": "#f59e0b",
        "level": "Beginner",
        "duration": "4 months",
        "description": "Drive growth through SEO, social media, and data-driven campaigns.",
        "skills": "SEO, SEM, Social Media, Analytics, Content",
        "jobs": ["Digital Marketing Specialist", "SEO Manager", "Social Media Strategist"],
        "steps": [
            {"title": "Marketing Fundamentals", "description": "Understand core marketing concepts and funnels", "milestone": False, "duration": "2 weeks", "lessons": ["Marketing Mix", "Customer Journey", "Funnel Optimization"], "course": "Digital Marketing 101", "quiz": [{"q": "What is the top of the marketing funnel?", "options": ["Conversion", "Awareness", "Retention", "Advocacy"], "answer": 1}]},
            {"title": "SEO & Content Strategy", "description": "Optimize content for search engines", "milestone": False, "duration": "3 weeks", "lessons": ["Keyword Research", "On-Page SEO", "Content Planning"], "course": "Digital Marketing 101", "quiz": []},
            {"title": "Social Media Marketing", "description": "Run campaigns on Instagram, LinkedIn, YouTube", "milestone": True, "duration": "3 weeks", "lessons": ["Platform Strategy", "Ad Creation", "Analytics & ROI"], "course": "Digital Marketing 101", "quiz": [{"q": "Which metric measures engagement rate?", "options": ["Impressions", "Reach", "Likes/Followers", "Click-through rate"], "answer": 2}]},
            {"title": "Google Ads & Analytics", "description": "Set up paid campaigns and track performance", "milestone": False, "duration": "3 weeks", "lessons": ["Campaign Setup", "Bidding Strategies", "Conversion Tracking"], "course": "", "quiz": []},
            {"title": "Email Marketing", "description": "Build and nurture email lists", "milestone": False, "duration": "2 weeks", "lessons": ["List Building", "Automation Flows", "A/B Testing"], "course": "", "quiz": []},
            {"title": "Marketing Capstone", "description": "Create a complete marketing strategy", "milestone": True, "duration": "3 weeks", "lessons": ["Audit & Research", "Strategy Development", "Presentation"], "course": "", "quiz": []},
        ],
    },
    {
        "slug": "financial-analyst",
        "title": "Financial Analyst",
        "icon": "💰",
        "color": "#22c55e",
        "level": "Intermediate",
        "duration": "5 months",
        "description": "Analyze financial data, create reports, and make data-driven investment decisions.",
        "skills": "Excel, Accounting, Financial Modeling, Analysis",
        "jobs": ["Financial Analyst", "Investment Analyst", "Risk Manager"],
        "steps": [
            {"title": "Financial Accounting Basics", "description": "Understand balance sheets, income statements", "milestone": False, "duration": "3 weeks", "lessons": ["Balance Sheets", "Income Statements", "Cash Flow"], "course": "", "quiz": [{"q": "What does EBITDA stand for?", "options": ["Earnings Before Interest Tax Depreciation Amortization", "Estimated Budget Income Total Debt Average", "Equity Based Investment Trading Analysis", "European Banking International Development Authority"], "answer": 0}]},
            {"title": "Excel for Finance", "description": "Master spreadsheets for financial analysis", "milestone": False, "duration": "3 weeks", "lessons": ["Pivot Tables", "Financial Formulas", "Data Visualization"], "course": "", "quiz": []},
            {"title": "Financial Modeling", "description": "Build financial models and forecasts", "milestone": True, "duration": "4 weeks", "lessons": ["Model Design", "Forecasting Methods", "Sensitivity Analysis"], "course": "", "quiz": []},
            {"title": "Investment Analysis", "description": "Evaluate stocks, bonds, and investment opportunities", "milestone": False, "duration": "3 weeks", "lessons": ["DCF Analysis", "Comparable Analysis", "Portfolio Theory"], "course": "", "quiz": [{"q": "What does NPV stand for?", "options": ["Net Present Value", "Net Profit Variance", "New Portfolio Value", "Nominal Price Vector"], "answer": 0}]},
            {"title": "Risk Management", "description": "Identify and mitigate financial risks", "milestone": False, "duration": "2 weeks", "lessons": ["Risk Types", "Hedging Strategies", "Regulatory Compliance"], "course": "", "quiz": []},
            {"title": "Finance Capstone", "description": "Analyze a real company's financial health", "milestone": True, "duration": "3 weeks", "lessons": ["Data Collection", "Ratio Analysis", "Report Writing"], "course": "", "quiz": []},
        ],
    },
    {
        "slug": "data-analyst",
        "title": "Data Analyst",
        "icon": "📈",
        "color": "#06b6d4",
        "level": "Beginner",
        "duration": "4 months",
        "description": "Turn raw data into actionable insights using SQL, Excel, and visualization tools.",
        "skills": "SQL, Excel, Python, Tableau, Statistics",
        "jobs": ["Data Analyst", "Business Analyst", "BI Analyst"],
        "steps": [
            {"title": "Excel for Data Analysis", "description": "Pivot tables, VLOOKUP, and data cleaning", "milestone": False, "duration": "2 weeks", "lessons": ["Formulas & Functions", "Pivot Tables", "Data Cleaning"], "course": "", "quiz": [{"q": "Which function looks up a value vertically?", "options": ["HLOOKUP", "VLOOKUP", "INDEX", "MATCH"], "answer": 1}]},
            {"title": "SQL Fundamentals", "description": "Query, filter, and aggregate data", "milestone": False, "duration": "3 weeks", "lessons": ["Basic Queries", "Joins & Unions", "Window Functions"], "course": "", "quiz": []},
            {"title": "Python for Data Analysis", "description": "Pandas, NumPy, and data wrangling", "milestone": True, "duration": "3 weeks", "lessons": ["NumPy Arrays", "Pandas Operations", "Data Cleaning"], "course": "Python for Data Science", "quiz": [{"q": "Which Pandas method removes null values?", "options": ["remove_na()", "dropna()", "deletena()", "cleanna()"], "answer": 1}]},
            {"title": "Data Visualization", "description": "Build dashboards with Tableau / Power BI", "milestone": False, "duration": "2 weeks", "lessons": ["Chart Types", "Dashboard Design", "Storytelling"], "course": "Data Visualization", "quiz": []},
            {"title": "Statistics Essentials", "description": "Descriptive stats, probability, A/B testing", "milestone": False, "duration": "3 weeks", "lessons": ["Descriptive Statistics", "Probability Distributions", "Hypothesis Testing"], "course": "", "quiz": [{"q": "Which test compares two group means?", "options": ["Chi-square", "T-test", "ANOVA", "Z-test"], "answer": 1}]},
            {"title": "Analyst Capstone", "description": "End-to-end analysis project", "milestone": True, "duration": "3 weeks", "lessons": ["Problem Framing", "Analysis & Insights", "Presentation"], "course": "", "quiz": []},
        ],
    },
]

COURSE_NOTES = {
    "Python for Data Science": (
        "# Python for Data Science - Course Notes\n\n"
        "## Key Concepts\n"
        "- Variables, Data Types, Control Flow\n"
        "- Functions and Modules\n"
        "- NumPy for numerical computing\n"
        "- Pandas for data manipulation\n"
        "- Matplotlib and Seaborn for visualization\n\n"
        "## Tips\n"
        "- Practice daily with small datasets\n"
        "- Use Jupyter notebooks for exploration\n"
        "- Join Kaggle competitions for real practice\n"
    ),
    "Web Development with React": (
        "# Web Development with React\n\n"
        "## Core Topics\n"
        "- JSX syntax and components\n"
        "- State and props management\n"
        "- React Hooks (useState, useEffect)\n"
        "- Routing with React Router\n"
        "- API integration with fetch/axios\n\n"
        "## Best Practices\n"
        "- Use functional components\n"
        "- Keep components small and focused\n"
        "- Use TypeScript for type safety\n"
    ),
    "Digital Marketing 101": (
        "# Digital Marketing 101\n\n"
        "## Modules\n"
        "- Marketing Funnel and Customer Journey\n"
        "- SEO Fundamentals and Keyword Research\n"
        "- Social Media Strategy\n"
        "- Content Marketing\n"
        "- Email Marketing Automation\n\n"
        "## Tools\n"
        "- Google Analytics, SEMrush, Canva, Mailchimp\n"
    ),
}

PATH_NOTES = {
    "data-scientist": {
        "en": "Follow this path sequentially. Each step builds on the previous one.",
        "hi": "इस पथ का क्रम से पालन करें। प्रत्येक चरण पिछले चरण पर आधारित है।",
    },
    "web-developer": {
        "en": "Start with HTML/CSS, then add JavaScript before moving to frameworks.",
        "hi": "HTML/CSS से शुरू करें, फिर फ्रेमवर्क पर जाने से पहले JavaScript सीखें।",
    },
    "digital-marketer": {
        "en": "Begin with fundamentals, then specialize in your area of interest.",
        "hi": "मूल बातों से शुरू करें, फिर अपनी रुचि के क्षेत्र में विशेषज्ञता प्राप्त करें।",
    },
    "financial-analyst": {
        "en": "Build a strong foundation in accounting before moving to modeling and analysis.",
        "hi": "मॉडलिंग और विश्लेषण पर जाने से पहले लेखांकन में एक मजबूत नींव बनाएं।",
    },
    "data-analyst": {
        "en": "Start with Excel and SQL, then progress to Python and visualization tools.",
        "hi": "Excel और SQL से शुरू करें, फिर Python और विज़ुअलाइज़ेशन टूल की ओर बढ़ें।",
    },
}

SEED_COURSES = [
    {
        "title": "Python for Data Science",
        "description": "Master Python programming for data analysis, visualization, and machine learning. Covers NumPy, Pandas, Matplotlib, and scikit-learn with hands-on projects.",
        "category": "Technology",
        "level": "Beginner",
        "duration_hrs": 24,
        "instructor": "Dr. Priya Sharma",
        "youtube_id": "r-uOLxNrNk8",
        "modules": json.dumps([
            {"title": "Python Basics", "duration": "2h 30m"},
            {"title": "NumPy for Numerical Computing", "duration": "3h"},
            {"title": "Pandas for Data Analysis", "duration": "4h"},
            {"title": "Data Visualization", "duration": "3h"},
            {"title": "Machine Learning Intro", "duration": "5h"},
            {"title": "Capstone Project", "duration": "6h 30m"},
        ]),
    },
    {
        "title": "Web Development with React",
        "description": "Build modern web applications using React. Covers components, state management, hooks, routing, and API integration with real-world projects.",
        "category": "Technology",
        "level": "Intermediate",
        "duration_hrs": 30,
        "instructor": "Amit Verma",
        "youtube_id": "w7ejDZ8SWv8",
        "modules": json.dumps([
            {"title": "JavaScript Refresher", "duration": "3h"},
            {"title": "React Fundamentals", "duration": "5h"},
            {"title": "State & Props", "duration": "4h"},
            {"title": "Hooks Deep Dive", "duration": "5h"},
            {"title": "Routing & Navigation", "duration": "3h"},
            {"title": "API Integration", "duration": "4h"},
            {"title": "Full-Stack Project", "duration": "6h"},
        ]),
    },
    {
        "title": "JavaScript Fundamentals",
        "description": "Learn JavaScript from scratch — variables, functions, DOM manipulation, ES6+, async programming, and more.",
        "category": "Technology",
        "level": "Beginner",
        "duration_hrs": 18,
        "instructor": "Rahul Kapoor",
        "youtube_id": "PkZNo7MFNFg",
        "modules": json.dumps([
            {"title": "Variables & Data Types", "duration": "2h"},
            {"title": "Functions & Scope", "duration": "2h 30m"},
            {"title": "DOM Manipulation", "duration": "3h"},
            {"title": "ES6+ Features", "duration": "3h"},
            {"title": "Async JavaScript", "duration": "3h 30m"},
            {"title": "Final Project", "duration": "4h"},
        ]),
    },
    {
        "title": "Digital Marketing 101",
        "description": "Complete introduction to digital marketing — SEO, social media, content marketing, email campaigns, and analytics.",
        "category": "Marketing",
        "level": "Beginner",
        "duration_hrs": 15,
        "instructor": "Neha Gupta",
        "youtube_id": "nU-II7BWPoE",
        "modules": json.dumps([
            {"title": "Marketing Fundamentals", "duration": "2h"},
            {"title": "SEO & Keyword Research", "duration": "3h"},
            {"title": "Social Media Strategy", "duration": "3h"},
            {"title": "Content Marketing", "duration": "2h 30m"},
            {"title": "Email Marketing", "duration": "2h"},
            {"title": "Analytics & Reporting", "duration": "2h 30m"},
        ]),
    },
    {
        "title": "Financial Literacy",
        "description": "Understand personal finance, budgeting, saving, investing, and basic tax concepts. Build a strong financial foundation.",
        "category": "Finance",
        "level": "Beginner",
        "duration_hrs": 12,
        "instructor": "CA Suresh Iyer",
        "youtube_id": "Hjp6G3H7kYg",
        "modules": json.dumps([
            {"title": "Money Mindset", "duration": "1h 30m"},
            {"title": "Budgeting Basics", "duration": "2h"},
            {"title": "Savings & Investments", "duration": "3h"},
            {"title": "Tax Fundamentals", "duration": "2h 30m"},
            {"title": "Retirement Planning", "duration": "1h 30m"},
            {"title": "Financial Goals Workshop", "duration": "1h 30m"},
        ]),
    },
    {
        "title": "AgriTech & Smart Farming",
        "description": "Learn modern agricultural techniques, smart irrigation, IoT in farming, and sustainable practices for increased yields.",
        "category": "Agriculture",
        "level": "Intermediate",
        "duration_hrs": 20,
        "instructor": "Dr. Lakshmi Bai",
        "youtube_id": "D7k7WfHVfY0",
        "modules": json.dumps([
            {"title": "Introduction to AgriTech", "duration": "2h"},
            {"title": "Soil & Crop Management", "duration": "3h"},
            {"title": "Smart Irrigation Systems", "duration": "3h 30m"},
            {"title": "IoT in Agriculture", "duration": "4h"},
            {"title": "Sustainable Practices", "duration": "3h"},
            {"title": "Farm Business Planning", "duration": "4h 30m"},
        ]),
    },
    {
        "title": "English Communication",
        "description": "Improve your spoken and written English for professional and everyday use. Focus on grammar, vocabulary, and conversation skills.",
        "category": "Language",
        "level": "Beginner",
        "duration_hrs": 16,
        "instructor": "Sarah Johnson",
        "youtube_id": "RZ8RfW3SI0c",
        "modules": json.dumps([
            {"title": "Basic Grammar", "duration": "2h 30m"},
            {"title": "Vocabulary Building", "duration": "2h"},
            {"title": "Conversation Practice", "duration": "3h"},
            {"title": "Business English", "duration": "3h"},
            {"title": "Writing Skills", "duration": "2h 30m"},
            {"title": "Presentation Skills", "duration": "3h"},
        ]),
    },
    {
        "title": "UI/UX Design Fundamentals",
        "description": "Learn user-centered design principles, wireframing, prototyping, and design thinking for digital products.",
        "category": "Design",
        "level": "Beginner",
        "duration_hrs": 18,
        "instructor": "Ananya Patel",
        "youtube_id": "c9Wg6Cb_YlU",
        "modules": json.dumps([
            {"title": "Design Thinking", "duration": "2h 30m"},
            {"title": "User Research", "duration": "3h"},
            {"title": "Wireframing", "duration": "3h"},
            {"title": "Visual Design", "duration": "3h 30m"},
            {"title": "Prototyping", "duration": "3h"},
            {"title": "Portfolio Project", "duration": "3h"},
        ]),
    },
    {
        "title": "First Aid & Emergency Care",
        "description": "Essential first aid skills for emergencies — CPR, wound care, burns, fractures, and emergency response protocols.",
        "category": "Healthcare",
        "level": "Beginner",
        "duration_hrs": 10,
        "instructor": "Dr. Rajesh Kumar",
        "youtube_id": "uWBMKKqtLLY",
        "modules": json.dumps([
            {"title": "Emergency Response Basics", "duration": "1h 30m"},
            {"title": "CPR & Rescue Breathing", "duration": "2h"},
            {"title": "Wound Care & Bleeding", "duration": "1h 30m"},
            {"title": "Burns & Fractures", "duration": "2h"},
            {"title": "Medical Emergencies", "duration": "1h 30m"},
            {"title": "First Aid Kit & Preparedness", "duration": "1h 30m"},
        ]),
    },
    {
        "title": "Mobile App Development",
        "description": "Build Android and iOS apps with React Native. Learn from scratch to app store deployment.",
        "category": "Technology",
        "level": "Intermediate",
        "duration_hrs": 28,
        "instructor": "Vikram Singh",
        "youtube_id": "0-S5a0eWoc8",
        "modules": json.dumps([
            {"title": "React Native Setup", "duration": "2h"},
            {"title": "Core Components", "duration": "4h"},
            {"title": "Navigation", "duration": "4h"},
            {"title": "State Management", "duration": "4h"},
            {"title": "API Integration", "duration": "4h"},
            {"title": "Device Features", "duration": "3h"},
            {"title": "App Store Deployment", "duration": "2h"},
            {"title": "Capstone Project", "duration": "5h"},
        ]),
    },
    {
        "title": "Cloud Computing with AWS",
        "description": "Master Amazon Web Services — EC2, S3, Lambda, RDS, and architecting cloud solutions. Prepare for AWS Certified Cloud Practitioner.",
        "category": "Technology",
        "level": "Advanced",
        "duration_hrs": 22,
        "instructor": "Arun Nair",
        "youtube_id": "3hLmDSMa4Rk",
        "modules": json.dumps([
            {"title": "Cloud Concepts", "duration": "2h"},
            {"title": "EC2 & Compute", "duration": "4h"},
            {"title": "S3 & Storage", "duration": "3h"},
            {"title": "Databases (RDS, DynamoDB)", "duration": "3h 30m"},
            {"title": "Lambda & Serverless", "duration": "3h"},
            {"title": "Networking & Security", "duration": "3h 30m"},
            {"title": "Architecture & Best Practices", "duration": "3h"},
        ]),
    },
]

SEED_QUIZZES = [
    {
        "course_title": "Python for Data Science",
        "title": "Python Fundamentals Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"question": "What is the correct way to create a list in Python?", "option_a": "list = (1, 2, 3)", "option_b": "list = [1, 2, 3]", "option_c": "list = {1, 2, 3}", "option_d": "list = <1, 2, 3>", "correct": "b", "explanation": "Square brackets [] are used to create lists in Python."},
            {"question": "Which library is used for numerical computing in Python?", "option_a": "Pandas", "option_b": "Matplotlib", "option_c": "NumPy", "option_d": "Seaborn", "correct": "c", "explanation": "NumPy is the fundamental library for numerical computing in Python."},
            {"question": "What does the 'len()' function return?", "option_a": "First element", "option_b": "Last element", "option_c": "Length of object", "option_d": "Type of object", "correct": "c", "explanation": "len() returns the number of items in an object."},
            {"question": "Which of the following is NOT a Python data type?", "option_a": "int", "option_b": "float", "option_c": "char", "option_d": "str", "correct": "c", "explanation": "Python does not have a 'char' data type; single characters are strings of length 1."},
            {"question": "What is the output of 'print(2 ** 3)'?", "option_a": "6", "option_b": "8", "option_c": "9", "option_d": "5", "correct": "b", "explanation": "The ** operator performs exponentiation: 2 to the power of 3 = 8."},
        ],
    },
    {
        "course_title": "Web Development with React",
        "title": "React Basics Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"question": "What is JSX?", "option_a": "A database query language", "option_b": "A JavaScript XML syntax extension", "option_c": "A CSS framework", "option_d": "A build tool", "correct": "b", "explanation": "JSX is a syntax extension for JavaScript that looks like HTML."},
            {"question": "Which hook is used for side effects in React?", "option_a": "useState", "option_b": "useEffect", "option_c": "useContext", "option_d": "useReducer", "correct": "b", "explanation": "useEffect handles side effects like API calls and subscriptions."},
            {"question": "What does 'props' stand for?", "option_a": "Properties", "option_b": "Proposals", "option_c": "Processes", "option_d": "Programs", "correct": "a", "explanation": "Props (properties) are read-only inputs passed to components."},
            {"question": "Which command creates a new React app?", "option_a": "npm init react-app", "option_b": "npx create-react-app", "option_c": "npm new react-app", "option_d": "node create-react-app", "correct": "b", "explanation": "npx create-react-app is the standard way to bootstrap a React app."},
            {"question": "What is the virtual DOM?", "option_a": "A real DOM copy in memory", "option_b": "A database", "option_c": "A CSS preprocessor", "option_d": "A server", "correct": "a", "explanation": "The virtual DOM is a lightweight copy of the real DOM kept in memory."},
        ],
    },
    {
        "course_title": "Digital Marketing 101",
        "title": "Digital Marketing Fundamentals",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"question": "What does SEO stand for?", "option_a": "Social Engagement Optimization", "option_b": "Search Engine Optimization", "option_c": "Site Efficiency Overview", "option_d": "Search Enhancement Option", "correct": "b", "explanation": "SEO stands for Search Engine Optimization."},
            {"question": "Which metric measures how many people clicked on a link?", "option_a": "Impressions", "option_b": "Reach", "option_c": "Click-Through Rate (CTR)", "option_d": "Bounce Rate", "correct": "c", "explanation": "CTR measures the percentage of people who clicked on a link."},
            {"question": "What is a 'call to action' (CTA)?", "option_a": "A phone call", "option_b": "A prompt for user response", "option_c": "An email", "option_d": "A social media post", "correct": "b", "explanation": "A CTA prompts the user to take a specific action."},
            {"question": "Which platform is best for B2B marketing?", "option_a": "Instagram", "option_b": "LinkedIn", "option_c": "TikTok", "option_d": "Snapchat", "correct": "b", "explanation": "LinkedIn is the primary platform for professional and B2B marketing."},
            {"question": "What is A/B testing?", "option_a": "Testing two versions to compare performance", "option_b": "Testing with two users", "option_c": "A programming language", "option_d": "A design tool", "correct": "a", "explanation": "A/B testing compares two versions to see which performs better."},
        ],
    },
    {
        "course_title": "Financial Literacy",
        "title": "Personal Finance Quiz",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"question": "What is compound interest?", "option_a": "Interest on principal only", "option_b": "Interest on principal + accumulated interest", "option_c": "A flat fee", "option_d": "Tax on interest", "correct": "b", "explanation": "Compound interest earns interest on both principal and previously earned interest."},
            {"question": "What does 'credit score' measure?", "option_a": "Your IQ", "option_b": "Creditworthiness", "option_c": "Your salary", "option_d": "Your age", "correct": "b", "explanation": "Credit score measures how likely you are to repay borrowed money."},
            {"question": "What is a budget?", "option_a": "A bank account", "option_b": "A spending plan", "option_c": "A loan", "option_d": "An investment", "correct": "b", "explanation": "A budget is a plan for how to spend your income."},
            {"question": "What is the 50/30/20 rule?", "option_a": "A diet plan", "option_b": "A budgeting guideline", "option_c": "An investment strategy", "option_d": "A tax rule", "correct": "b", "explanation": "50% needs, 30% wants, 20% savings is a popular budgeting guideline."},
            {"question": "What is an emergency fund?", "option_a": "Money for vacations", "option_b": "Savings for unexpected expenses", "option_c": "A retirement account", "option_d": "A type of insurance", "correct": "b", "explanation": "An emergency fund covers unexpected expenses like medical bills or job loss."},
        ],
    },
    {
        "course_title": "English Communication",
        "title": "English Grammar Basics",
        "time_limit": 600,
        "pass_pct": 60,
        "questions": [
            {"question": "Which is correct?", "option_a": "She go to school", "option_b": "She goes to school", "option_c": "She going to school", "option_d": "She gone to school", "correct": "b", "explanation": "Third person singular requires 'goes' in simple present tense."},
            {"question": "What is a noun?", "option_a": "An action word", "option_b": "A naming word", "option_c": "A describing word", "option_d": "A connecting word", "correct": "b", "explanation": "Nouns name people, places, things, or ideas."},
            {"question": "Choose the correct article: '___ apple a day keeps the doctor away.'", "option_a": "A", "option_b": "An", "option_c": "The", "option_d": "None", "correct": "b", "explanation": "Use 'an' before words starting with vowel sounds."},
            {"question": "What tense is 'I had finished'?", "option_a": "Simple past", "option_b": "Past perfect", "option_c": "Present perfect", "option_d": "Future perfect", "correct": "b", "explanation": "'Had + past participle' is the past perfect tense."},
            {"question": "Which sentence is correct?", "option_a": "He don't like coffee", "option_b": "He doesn't likes coffee", "option_c": "He doesn't like coffee", "option_d": "He not like coffee", "correct": "c", "explanation": "Use 'doesn't' + base form of verb for third person negative."},
        ],
    },
]

SEED_BADGES = [
    {"slug": "first_step", "name": "First Step", "icon": "👣", "description": "Complete your first path step", "xp_reward": 50},
    {"slug": "quiz_master", "name": "Quiz Passer", "icon": "🧠", "description": "Pass your first quiz", "xp_reward": 100},
    {"slug": "streak_3", "name": "3-Day Streak", "icon": "🔥", "description": "Learn 3 days in a row", "xp_reward": 75},
    {"slug": "streak_7", "name": "Week Warrior", "icon": "⚡", "description": "Learn 7 days in a row", "xp_reward": 200},
    {"slug": "path_complete", "name": "Path Master", "icon": "🗺️", "description": "Complete an entire skill path", "xp_reward": 500},
    {"slug": "course_done", "name": "Course Graduate", "icon": "🎓", "description": "Reach 100% on any course", "xp_reward": 150},
    {"slug": "first_enroll", "name": "Enrolled", "icon": "📚", "description": "Enroll in your first course", "xp_reward": 20},
    {"slug": "top10", "name": "Top 10", "icon": "🏆", "description": "Reach top 10 on the leaderboard", "xp_reward": 300},
]


def get_videos_for_course(course, lang="en"):
    """Return curated or YouTube-sourced videos for a course by language."""
    import os, json, urllib.request, urllib.parse

    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    query_map = {
        "en": f"{course.title} tutorial",
        "hi": f"{course.title} ट्यूटोरियल",
        "kn": f"{course.title} ಟ್ಯುಟೋರಿಯಲ್",
        "ta": f"{course.title} பயிற்சி",
        "te": f"{course.title} ట్యుటోరియల్",
        "bn": f"{course.title} টিউটোরিয়াল",
        "mr": f"{course.title} शिकवणी",
        "gu": f"{course.title} ટ્યુટોરિયલ",
    }
    query = query_map.get(lang, query_map["en"])

    if api_key:
        try:
            params = urllib.parse.urlencode({
                "part": "snippet",
                "q": query,
                "maxResults": 10,
                "type": "video",
                "key": api_key,
                "relevanceLanguage": lang if lang in ("en","hi") else "en",
            })
            url = f"https://www.googleapis.com/youtube/v3/search?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            return [
                {"video_id": item["id"]["videoId"],
                 "title": item["snippet"]["title"],
                 "channel": item["snippet"]["channelTitle"],
                 "thumbnail": item["snippet"]["thumbnails"]["high"]["url"] if "high" in item["snippet"]["thumbnails"] else item["snippet"]["thumbnails"]["default"]["url"],
                 "duration": ""}
                for item in data.get("items", [])
            ]
        except Exception as e:
            print(f"[YouTube API] Error: {e}")

    # Fallback curated videos (used when no YouTube API key is set)
    fallback_videos = {
        "Python for Data Science": [
            {"video_id": "r-uOLxNrNk8", "title": "Python for Data Science - Full Course", "channel": "FreeCodeCamp", "duration": "5h 30m"},
            {"video_id": "LHBE6h9U6eU", "title": "Python Pandas Tutorial", "channel": "DataCamp", "duration": "3h"},
            {"video_id": "GPVsHOlRBBI", "title": "NumPy Crash Course", "channel": "NeuralNine", "duration": "1h 45m"},
        ],
        "Web Development with React": [
            {"video_id": "w7ejDZ8SWv8", "title": "React Tutorial for Beginners", "channel": "Programming with Mosh", "duration": "3h"},
            {"video_id": "Ke90Tje7VS0", "title": "React JS Full Course", "channel": "FreeCodeCamp", "duration": "10h"},
            {"video_id": "DLX62G4s3gs", "title": "React Hooks Tutorial", "channel": "Web Dev Simplified", "duration": "1h 30m"},
        ],
        "JavaScript Fundamentals": [
            {"video_id": "PkZNo7MFNFg", "title": "JavaScript Programming - Full Course", "channel": "FreeCodeCamp", "duration": "7h 44m"},
            {"video_id": "2Ji-clqUYnA", "title": "JavaScript Fundamentals - Full Course", "channel": "Coding Addict", "duration": "10h 23m"},
            {"video_id": "jS4aFq5-91M", "title": "Learn JavaScript - Full Course", "channel": "Scrimba", "duration": "7h 44m"},
        ],
        "Digital Marketing 101": [
            {"video_id": "nU-II7BWPoE", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "duration": "9h 4m"},
            {"video_id": "3BjwbpIzROk", "title": "Digital Marketing Full Course 2026", "channel": "Simplilearn", "duration": "9h 4m"},
            {"video_id": "hiEb1m7CXH4", "title": "Digital Marketing Course in 7 Hours", "channel": "Edureka", "duration": "7h 32m"},
        ],
        "Financial Literacy": [
            {"video_id": "Hjp6G3H7kYg", "title": "Financial Literacy for Beginners", "channel": "SkillBridge", "duration": "2h"},
            {"video_id": "WEDIj9JBTC8", "title": "Everything About Finance & Investing", "channel": "Big Think", "duration": "44m"},
            {"video_id": "LK16dJgqoTs", "title": "Personal Finance for Beginners", "channel": "Jon Law", "duration": "57m"},
        ],
        "AgriTech & Smart Farming": [
            {"video_id": "D7k7WfHVfY0", "title": "AgriTech & Smart Farming Overview", "channel": "SkillBridge", "duration": "2h"},
            {"video_id": "mNjFot7KZaY", "title": "Smart Garden 2.0 - DIY Automation", "channel": "3Dtec Studio", "duration": "12m"},
            {"video_id": "fuwZmgKenqs", "title": "Smart Farm Automation - Complete Guide", "channel": "Geekble", "duration": "30m"},
        ],
        "English Communication": [
            {"video_id": "RZ8RfW3SI0c", "title": "English Communication Skills", "channel": "SkillBridge", "duration": "2h"},
            {"video_id": "QkXfWALFQ68", "title": "Learn English in 10 Hours", "channel": "JForrest English", "duration": "10h"},
            {"video_id": "s-PBojpveAU", "title": "English Listening & Speaking Practice", "channel": "English with Maria", "duration": "10h"},
        ],
        "UI/UX Design Fundamentals": [
            {"video_id": "c9Wg6Cb_YlU", "title": "UI/UX Design Fundamentals", "channel": "SkillBridge", "duration": "2h"},
            {"video_id": "kbZejnPXyLM", "title": "Free Figma UX Design UI Essentials", "channel": "Bring Your Own Laptop", "duration": "2h 58m"},
            {"video_id": "y6L1fQA5yc0", "title": "UI UX Design Full Course", "channel": "Simplilearn", "duration": "9h 13m"},
        ],
        "First Aid & Emergency Care": [
            {"video_id": "uWBMKKqtLLY", "title": "First Aid & Emergency Care", "channel": "SkillBridge", "duration": "2h"},
            {"video_id": "8gdGKvpZago", "title": "Complete Guide to First Aid", "channel": "Heart2Heart CPR", "duration": "57m"},
            {"video_id": "ea1RJUOiNfQ", "title": "How to do the Primary Survey", "channel": "St John Ambulance", "duration": "4m"},
        ],
        "Mobile App Development": [
            {"video_id": "0-S5a0eWoc8", "title": "Mobile App Development Overview", "channel": "SkillBridge", "duration": "2h"},
            {"video_id": "fis26HvvDII", "title": "Android Development for Beginners", "channel": "FreeCodeCamp", "duration": "11h 36m"},
            {"video_id": "ZBCUegTZF7M", "title": "React Native Course for Beginners", "channel": "JavaScript Mastery", "duration": "4h 29m"},
            {"video_id": "CzRQ9mnmh44", "title": "Complete Dart & Flutter Developer Course", "channel": "Rivaan Ranawat", "duration": "20h 48m"},
        ],
        "Cloud Computing with AWS": [
            {"video_id": "3hLmDSMa4Rk", "title": "Cloud Computing with AWS", "channel": "SkillBridge", "duration": "2h"},
            {"video_id": "c3Cn4xYfxJY", "title": "AWS Solutions Architect Full Course", "channel": "FreeCodeCamp", "duration": "50h 29m"},
            {"video_id": "TTcyhhH2FWE", "title": "AWS Developer Associate Certification", "channel": "FreeCodeCamp", "duration": "81h 10m"},
        ],
    }
    return fallback_videos.get(course.title, [
        {"video_id": course.youtube_id or "dQw4w9WgXcQ", "title": course.title, "channel": course.instructor, "duration": "2h"},
    ])
