document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  initScrollAnimations();
  initStatCounters();
});

/* --- LIGHT / DARK MODE TOGGLE --- */
function initTheme() {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeButtonText(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  updateThemeButtonText(newTheme);
}

function updateThemeButtonText(theme) {
  const btn = document.getElementById("themeToggleBtn");
  if (!btn) return;
  const isUrdu = document.body.classList.contains("lang-ur");
  if (theme === "dark") {
    btn.textContent = isUrdu ? "☀️ روشنی" : "☀️ Light";
  } else {
    btn.textContent = isUrdu ? "🌙 تاریکی" : "🌙 Dark";
  }
}

/* --- ENGLISH / URDU LANGUAGE TOGGLE --- */
const translations = {
  en: {
    brand_name: "The Educators (Soban Campus)",
    tagline: "Join Conceptual Learning",
    home: "Home",
    about: "About Us",
    academics: "Academics",
    admissions: "Admissions",
    status_check: "Check Application Status",
    timetable: "Timetable",
    gallery: "Gallery",
    contact: "Contact Us",
    news: "News",
    events: "Events",
    login: "Login / Register",
    dashboard: "Dashboard",
    admin: "Admin",
    logout: "Logout",
    explore_btn: "Explore Our School",
    apply_btn: "Apply for Admission",
    stat_years: "8+ Years of Excellence",
    stat_students: "500+ Students enrolled",
    stat_staff: "30+ Staff Members",
    stat_success: "96% Academic Success Rate"
  },
  ur: {
    brand_name: "دی ایجوکیٹرز (ثوبان کیمپس)",
    tagline: "تفہیمی و تصوّراتی تعلیم حاصل کریں",
    home: "صفحہ اول",
    about: "ہمارے بارے میں",
    academics: "تعلیمی امور",
    admissions: "داخلہ جات",
    status_check: "درخواست کی صورتحال",
    timetable: "ٹائم ٹیبل",
    gallery: "تصاویر",
    contact: "رابطہ کریں",
    news: "خبریں",
    events: "تقریبات",
    login: "لاگ ان / رجسٹریشن",
    dashboard: "ڈیش بورڈ",
    admin: "ایڈمن",
    logout: "لاگ آؤٹ",
    explore_btn: "اسکول کا جائزہ لیں",
    apply_btn: "داخلہ کی درخواست دیں",
    stat_years: "8+ سالہ شاندار تعلیمی سفر",
    stat_students: "500+ زیر تعلیم طلباء",
    stat_staff: "30+ تجربہ کار اساتذہ و عملہ",
    stat_success: "96% سالانہ کامیابی کی شرح"
  }
};

function initLanguage() {
  const savedLang = localStorage.getItem("lang") || "en";
  applyLanguage(savedLang);
}

function toggleLanguage() {
  const currentLang = localStorage.getItem("lang") === "ur" ? "en" : "ur";
  localStorage.setItem("lang", currentLang);
  applyLanguage(currentLang);
}

function applyLanguage(lang) {
  if (lang === "ur") {
    document.body.classList.add("lang-ur");
  } else {
    document.body.classList.remove("lang-ur");
  }

  // Translate all elements with data-i18n attribute
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (translations[lang] && translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });

  const langBtn = document.getElementById("langToggleBtn");
  if (langBtn) {
    langBtn.textContent = lang === "ur" ? "English" : "اردو";
  }

  const currentTheme = document.documentElement.getAttribute("data-theme");
  updateThemeButtonText(currentTheme);
}

/* --- POPUP MODAL CLOSER --- */
function closePopup() {
  const popup = document.getElementById("flashPopup");
  if (popup) popup.remove();
}

/* --- SCROLL ANIMATIONS --- */
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(".animate-scroll").forEach(el => observer.observe(el));
}

/* --- STAT COUNTERS ANIMATION --- */
function initStatCounters() {
  const counters = document.querySelectorAll(".counter");
  if (counters.length === 0) return;

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = +entry.target.getAttribute("data-target");
        let count = 0;
        const speed = target / 50;
        const updateCount = () => {
          count += speed;
          if (count < target) {
            entry.target.innerText = Math.ceil(count);
            setTimeout(updateCount, 25);
          } else {
            entry.target.innerText = target;
          }
        };
        updateCount();
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(c => observer.observe(c));
}

/* --- RULE-BASED FAQ CHATBOT --- */
const faqDatabase = [
  { keywords: ["timing", "time", "hours", "schedule", "open"], answer: "School hours are Monday through Friday, 7:45 AM to 1:30 PM. Saturday & Sunday are OFF." },
  { keywords: ["fee", "dues", "charges", "cost"], answer: "Fee structures vary by class (Class 1 to Matric). Please visit our accounts office or contact us on WhatsApp (0300-7331807)." },
  { keywords: ["admission", "apply", "document", "requirements"], answer: "Admissions are open for Class 1 to Class 10 (Matric). Required documents: B-Form copy, Father's CNIC, Previous School Leaving Certificate, and 2 Photos." },
  { keywords: ["facility", "lab", "computer", "library"], answer: "We provide state-of-the-art Computer & Science/Chemistry Labs, well-lit Classrooms, and a stocked Library." },
  { keywords: ["principal", "head", "fozia"], answer: "Our honorable Principal is Mam Fozia Mughees." },
  { keywords: ["director", "maqbool"], answer: "Our respected Director is Maqbool Ahmad." },
  { keywords: ["address", "location", "where"], answer: "Ahmad Cottage, Opp. Best Way CNG, Raja Pur Stop, Khanewal Road, Multan." },
  { keywords: ["phone", "contact", "whatsapp", "number"], answer: "You can reach us directly at 0300-7331807 (Phone & WhatsApp)." },
  { keywords: ["classes", "level", "grade", "subject"], answer: "We offer education from Class 1 to Matric (Class 10). Key subjects include English, Physics, Chemistry, Math, Urdu, Pak Studies/Islamiat, and Computer." },
  { keywords: ["exam", "test", "board"], answer: "Regular evaluation includes monthly assessment tests and BISE Multan Board preparation for Matric students." }
];

function toggleChatbot() {
  const win = document.getElementById("chatbotWindow");
  if (win.style.display === "flex") {
    win.style.display = "none";
  } else {
    win.style.display = "flex";
  }
}

function handleChatSubmit(event) {
  if (event.key === "Enter" || event.type === "click") {
    const input = document.getElementById("chatInput");
    const text = input.value.trim().toLowerCase();
    if (!text) return;

    appendChatMessage(input.value.trim(), "user");
    input.value = "";

    setTimeout(() => {
      let botReply = "Thank you for asking! For detailed inquiries, please call or WhatsApp our main office at 0300-7331807.";
      for (const item of faqDatabase) {
        if (item.keywords.some(kw => text.includes(kw))) {
          botReply = item.answer;
          break;
        }
      }
      appendChatMessage(botReply, "bot");
    }, 400);
  }
}

function appendChatMessage(text, sender) {
  const body = document.getElementById("chatBody");
  const msgDiv = document.createElement("div");
  msgDiv.className = `chat-msg ${sender}`;
  msgDiv.textContent = text;
  body.appendChild(msgDiv);
  body.scrollTop = body.scrollHeight;
}
