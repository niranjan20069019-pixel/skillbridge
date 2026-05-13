/**
 * SkillBridge i18n — lightweight client-side translation system
 * Supports: en, hi, kn, ta, te
 * Usage: data-i18n="key" on any element
 */
const SB_TRANSLATIONS = {
  // Navigation
  dashboard:       {en:"Dashboard",       hi:"डैशबोर्ड",      kn:"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",  ta:"டாஷ்போர்டு",    te:"డాష్‌బోర్డ్"},
  courses:         {en:"Courses",         hi:"कोर्स",          kn:"ಕೋರ್ಸ್‌ಗಳು",    ta:"பாடங்கள்",      te:"కోర్సులు"},
  my_courses:      {en:"My Courses",      hi:"मेरे कोर्स",     kn:"ನನ್ನ ಕೋರ್ಸ್‌ಗಳು",ta:"என் பாடங்கள்",  te:"నా కోర్సులు"},
  progress:        {en:"Progress",        hi:"प्रगति",         kn:"ಪ್ರಗತಿ",          ta:"முன்னேற்றம்",   te:"పురోగతి"},
  skill_paths:     {en:"Skill Paths",     hi:"कौशल पथ",        kn:"ಕೌಶಲ್ ಮಾರ್ಗಗಳು", ta:"திறன் பாதைகள்", te:"నైపుణ్య మార్గాలు"},
  mentors:         {en:"Mentors",         hi:"मेंटर",           kn:"ಮಾರ್ಗದರ್ಶಕರು",  ta:"வழிகாட்டிகள்",  te:"మెంటర్లు"},
  analytics:       {en:"Analytics",       hi:"विश्लेषण",        kn:"ವಿಶ್ಲೇಷಣೆ",      ta:"பகுப்பாய்வு",   te:"విశ్లేషణలు"},
  logout:          {en:"Logout",          hi:"लॉग आउट",        kn:"ಲಾಗ್ ಔಟ್",       ta:"வெளியேறு",      te:"లాగ్ అవుట్"},
  sign_in:         {en:"Sign In",         hi:"साइन इन",        kn:"ಸೈನ್ ಇನ್",       ta:"உள்நுழை",       te:"సైన్ ఇన్"},
  get_started:     {en:"Get Started",     hi:"शुरू करें",      kn:"ಪ್ರಾರಂಭಿಸಿ",     ta:"தொடங்குங்கள்",  te:"ప్రారంభించండి"},

  // Dashboard
  overview:        {en:"Overview",        hi:"अवलोकन",         kn:"ಅವಲೋಕನ",         ta:"கண்ணோட்டம்",    te:"అవలోకనం"},
  skill_score:     {en:"Skill Score",     hi:"कौशल स्कोर",     kn:"ಕೌಶಲ್ ಸ್ಕೋರ್",   ta:"திறன் மதிப்பெண்",te:"నైపుణ్య స్కోర్"},
  enrolled:        {en:"Enrolled",        hi:"नामांकित",        kn:"ನೋಂದಾಯಿಸಲಾಗಿದೆ", ta:"சேர்க்கப்பட்டது",te:"నమోదైంది"},
  continue:        {en:"Continue",        hi:"जारी रखें",      kn:"ಮುಂದುವರಿಸಿ",     ta:"தொடரவும்",      te:"కొనసాగించు"},
  start_learning:  {en:"Start Learning",  hi:"सीखना शुरू करें",kn:"ಕಲಿಕೆ ಪ್ರಾರಂಭಿಸಿ",ta:"கற்கத் தொடங்கு",te:"నేర్చుకోవడం ప్రారంభించు"},
  view_all:        {en:"View All",        hi:"सभी देखें",      kn:"ಎಲ್ಲ ನೋಡಿ",      ta:"அனைத்தும் பார்",te:"అన్నీ చూడు"},
  recommendations: {en:"Recommendations", hi:"सिफारिशें",       kn:"ಶಿಫಾರಸುಗಳು",     ta:"பரிந்துரைகள்",  te:"సిఫార్సులు"},
  welcome_back:    {en:"Welcome back",    hi:"वापस स्वागत है", kn:"ಮರಳಿ ಸ್ವಾಗತ",    ta:"மீண்டும் வரவேற்கிறோம்",te:"తిరిగి స్వాగతం"},
  your_progress:   {en:"Your Progress",   hi:"आपकी प्रगति",    kn:"ನಿಮ್ಮ ಪ್ರಗತಿ",   ta:"உங்கள் முன்னேற்றம்",te:"మీ పురోగతి"},
  completed:       {en:"Completed",       hi:"पूर्ण",           kn:"ಪೂರ್ಣ",           ta:"முடிந்தது",      te:"పూర్తైంది"},
  in_progress:     {en:"In Progress",     hi:"प्रगति में",     kn:"ಪ್ರಗತಿಯಲ್ಲಿ",    ta:"நடந்து கொண்டிருக்கிறது",te:"పురోగతిలో ఉంది"},
  not_started:     {en:"Not Started",     hi:"शुरू नहीं",      kn:"ಪ್ರಾರಂಭಿಸಿಲ್ಲ",  ta:"தொடங்கவில்லை",  te:"ప్రారంభించలేదు"},
  ai_mentor:       {en:"AI Mentor",       hi:"AI मेंटर",        kn:"AI ಮಾರ್ಗದರ್ಶಕ",  ta:"AI வழிகாட்டி",  te:"AI మెంటర్"},
  ask_mentor:      {en:"Ask your mentor…",hi:"मेंटर से पूछें…", kn:"ಮಾರ್ಗದರ್ಶಕರನ್ನು ಕೇಳಿ…",ta:"வழிகாட்டியிடம் கேளுங்கள்…",te:"మెంటర్‌ని అడగండి…"},
  send:            {en:"Send",            hi:"भेजें",           kn:"ಕಳುಹಿಸಿ",         ta:"அனுப்பு",        te:"పంపు"},

  // Courses
  all_courses:     {en:"All Courses",     hi:"सभी कोर्स",      kn:"ಎಲ್ಲ ಕೋರ್ಸ್‌ಗಳು",ta:"அனைத்து பாடங்கள்",te:"అన్ని కోర్సులు"},
  search_courses:  {en:"Search courses…", hi:"कोर्स खोजें…",   kn:"ಕೋರ್ಸ್ ಹುಡುಕಿ…", ta:"பாடங்கள் தேடு…", te:"కోర్సులు వెతకండి…"},
  modules:         {en:"modules",         hi:"मॉड्यूल",         kn:"ಮಾಡ್ಯೂಲ್‌ಗಳು",   ta:"தொகுதிகள்",     te:"మాడ్యూళ్ళు"},
  free:            {en:"Free",            hi:"मुफ्त",           kn:"ಉಚಿತ",            ta:"இலவசம்",        te:"ఉచితం"},
  enroll_now:      {en:"Enroll Now",      hi:"अभी नामांकन करें",kn:"ಈಗ ನೋಂದಾಯಿಸಿ",  ta:"இப்போது சேரு",  te:"ఇప్పుడు నమోదు చేయండి"},
  course_modules:  {en:"Course Modules",  hi:"कोर्स मॉड्यूल",  kn:"ಕೋರ್ಸ್ ಮಾಡ್ಯೂಲ್‌ಗಳು",ta:"பாட தொகுதிகள்",te:"కోర్సు మాడ్యూళ్ళు"},
  expand_all:      {en:"Expand All",      hi:"सभी खोलें",      kn:"ಎಲ್ಲ ತೆರೆಯಿರಿ",  ta:"அனைத்தும் விரி",te:"అన్నీ విస్తరించు"},
  collapse_all:    {en:"Collapse All",    hi:"सभी बंद करें",   kn:"ಎಲ್ಲ ಮುಚ್ಚಿರಿ",  ta:"அனைத்தும் மூடு",te:"అన్నీ కుదించు"},

  // Learn page
  mark_complete:   {en:"Mark Complete",   hi:"पूर्ण करें",     kn:"ಪೂರ್ಣಗೊಳಿಸಿ",   ta:"முடிந்தது",      te:"పూర్తి చేయి"},
  take_quiz:       {en:"Take Quiz",       hi:"क्विज़ लें",     kn:"ರಸಪ್ರಶ್ನೆ ತೆಗೆಯಿರಿ",ta:"வினாடி வினா",  te:"క్విజ్ తీసుకో"},
  certificate:     {en:"Certificate",     hi:"प्रमाणपत्र",     kn:"ಪ್ರಮಾಣಪತ್ರ",     ta:"சான்றிதழ்",     te:"సర్టిఫికేట్"},
  overview_tab:    {en:"Overview",        hi:"अवलोकन",         kn:"ಅವಲೋಕನ",         ta:"கண்ணோட்டம்",    te:"అవలోకనం"},
  notes_tab:       {en:"Notes",           hi:"नोट्स",          kn:"ಟಿಪ್ಪಣಿಗಳು",     ta:"குறிப்புகள்",   te:"నోట్స్"},
  resources_tab:   {en:"Resources",       hi:"संसाधन",         kn:"ಸಂಪನ್ಮೂಲಗಳು",   ta:"வளங்கள்",       te:"వనరులు"},
  qa_tab:          {en:"Q&A",             hi:"प्रश्नोत्तर",    kn:"ಪ್ರಶ್ನೋತ್ತರ",    ta:"கேள்வி பதில்",  te:"ప్రశ్నోత్తరాలు"},
  videos_tab:      {en:"Videos",          hi:"वीडियो",         kn:"ವೀಡಿಯೊಗಳು",      ta:"வீடியோக்கள்",   te:"వీడియోలు"},
  course_outline:  {en:"Course Outline",  hi:"कोर्स रूपरेखा",  kn:"ಕೋರ್ಸ್ ರೂಪರೇಖೆ", ta:"பாட அமைப்பு",   te:"కోర్సు రూపురేఖ"},

  // Quiz
  quiz_title:      {en:"Course Quiz",     hi:"कोर्स क्विज़",   kn:"ಕೋರ್ಸ್ ರಸಪ್ರಶ್ನೆ",ta:"பாட வினாடி வினா",te:"కోర్సు క్విజ్"},
  submit_quiz:     {en:"Submit Quiz",     hi:"क्विज़ जमा करें",kn:"ರಸಪ್ರಶ್ನೆ ಸಲ್ಲಿಸಿ",ta:"வினாடி வினா சமர்ப்பி",te:"క్విజ్ సమర్పించు"},
  translating:     {en:"Translating…",    hi:"अनुवाद हो रहा है…",kn:"ಅನುವಾದಿಸಲಾಗುತ್ತಿದೆ…",ta:"மொழிபெயர்க்கிறது…",te:"అనువదిస్తోంది…"},
  translate_quiz:  {en:"Translate Quiz",  hi:"क्विज़ अनुवाद करें",kn:"ರಸಪ್ರಶ್ನೆ ಅನುವಾದಿಸಿ",ta:"வினாடி வினா மொழிபெயர்",te:"క్విజ్ అనువదించు"},
  time_left:       {en:"Time Left",       hi:"समय शेष",        kn:"ಉಳಿದ ಸಮಯ",       ta:"மீதமுள்ள நேரம்",te:"మిగిలిన సమయం"},
  question:        {en:"Question",        hi:"प्रश्न",          kn:"ಪ್ರಶ್ನೆ",         ta:"கேள்வி",         te:"ప్రశ్న"},
  of:              {en:"of",              hi:"में से",          kn:"ರಲ್ಲಿ",           ta:"இல்",            te:"లో"},

  // Notifications / misc
  language_changed:{en:"Language updated!",hi:"भाषा बदली!",    kn:"ಭಾಷೆ ಬದಲಾಯಿತು!", ta:"மொழி மாற்றப்பட்டது!",te:"భాష మార్చబడింది!"},
  loading:         {en:"Loading…",        hi:"लोड हो रहा है…", kn:"ಲೋಡ್ ಆಗುತ್ತಿದೆ…",ta:"ஏற்றுகிறது…",    te:"లోడ్ అవుతోంది…"},
  error:           {en:"Something went wrong.",hi:"कुछ गलत हुआ।",kn:"ಏನೋ ತಪ್ಪಾಯಿತು.",ta:"ஏதோ தவறு.",     te:"ఏదో తప్పు జరిగింది."},
  save:            {en:"Save",            hi:"सहेजें",         kn:"ಉಳಿಸಿ",           ta:"சேமி",           te:"సేవ్ చేయి"},
  cancel:          {en:"Cancel",          hi:"रद्द करें",      kn:"ರದ್ದುಮಾಡಿ",       ta:"ரத்து செய்",    te:"రద్దు చేయి"},
  search:          {en:"Search",          hi:"खोजें",          kn:"ಹುಡುಕಿ",          ta:"தேடு",           te:"వెతకండి"},
  back:            {en:"Back",            hi:"वापस",           kn:"ಹಿಂದೆ",           ta:"திரும்பு",       te:"వెనక్కి"},
  next:            {en:"Next",            hi:"अगला",           kn:"ಮುಂದೆ",           ta:"அடுத்து",        te:"తదుపరి"},
  prev:            {en:"Previous",        hi:"पिछला",          kn:"ಹಿಂದಿನ",          ta:"முந்தைய",        te:"మునుపటి"},
  duration:        {en:"Duration",        hi:"अवधि",           kn:"ಅವಧಿ",            ta:"கால அளவு",      te:"వ్యవధి"},
  level:           {en:"Level",           hi:"स्तर",           kn:"ಹಂತ",             ta:"நிலை",           te:"స్థాయి"},
  instructor:      {en:"Instructor",      hi:"प्रशिक्षक",      kn:"ಬೋಧಕ",            ta:"பயிற்றுவிப்பாளர்",te:"శిక్షకుడు"},
  language:        {en:"Language",        hi:"भाषा",           kn:"ಭಾಷೆ",            ta:"மொழி",           te:"భాష"},
  select_language: {en:"Select Language", hi:"भाषा चुनें",     kn:"ಭಾಷೆ ಆಯ್ಕೆ ಮಾಡಿ",ta:"மொழி தேர்ந்தெடு",te:"భాష ఎంచుకోండి"},
};

// ── Core i18n engine ──────────────────────────────────────────────────────────

const I18N = {
  _lang: localStorage.getItem('sb_lang') || document.documentElement.lang || 'en',

  get lang() { return this._lang; },

  t(key) {
    const entry = SB_TRANSLATIONS[key];
    if (!entry) return key;
    return entry[this._lang] || entry['en'] || key;
  },

  setLang(code) {
    this._lang = code;
    localStorage.setItem('sb_lang', code);
    document.documentElement.lang = code;
    this.applyAll();
    this._syncServer(code);
  },

  applyAll() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      const val = this.t(key);
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        if (el.placeholder !== undefined) el.placeholder = val;
      } else {
        el.textContent = val;
      }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      el.placeholder = this.t(el.dataset.i18nPlaceholder);
    });
    // Update lang switcher active state
    document.querySelectorAll('.lang-option').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === this._lang);
    });
  },

  _syncServer(code) {
    fetch('/api/set-language', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({language: code})
    }).catch(() => {});
  },

  init() {
    // Sync from server lang if user is logged in (html lang attr set by Flask)
    const serverLang = document.documentElement.lang;
    if (serverLang && serverLang !== 'en' && serverLang !== this._lang) {
      this._lang = serverLang;
      localStorage.setItem('sb_lang', serverLang);
    }
    this.applyAll();
  }
};

// ── Language switcher UI builder ──────────────────────────────────────────────

function buildLangSwitcher(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const langs = [
    {code:'en', label:'EN', name:'English'},
    {code:'hi', label:'हि', name:'Hindi'},
    {code:'kn', label:'ಕ', name:'Kannada'},
    {code:'ta', label:'த', name:'Tamil'},
    {code:'te', label:'తె', name:'Telugu'},
  ];

  const wrapper = document.createElement('div');
  wrapper.className = 'lang-switcher';
  wrapper.setAttribute('role', 'group');
  wrapper.setAttribute('aria-label', 'Select language');

  langs.forEach(({code, label, name}) => {
    const btn = document.createElement('button');
    btn.className = 'lang-option' + (code === I18N.lang ? ' active' : '');
    btn.dataset.lang = code;
    btn.title = name;
    btn.textContent = label;
    btn.setAttribute('aria-label', name);
    btn.onclick = () => {
      I18N.setLang(code);
      // Show brief toast
      showLangToast(I18N.t('language_changed'));
    };
    wrapper.appendChild(btn);
  });

  container.appendChild(wrapper);
}

function showLangToast(msg) {
  let t = document.getElementById('lang-toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'lang-toast';
    t.style.cssText = 'position:fixed;bottom:20px;right:20px;background:var(--brand);color:#fff;padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;z-index:9999;opacity:0;transition:opacity 0.3s;pointer-events:none;';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.opacity = '1';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.opacity = '0'; }, 2000);
}

// ── Auto-init on DOM ready ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  I18N.init();
  buildLangSwitcher('lang-switcher-mount');
});
