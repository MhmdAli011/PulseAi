# 🏥 PulseAI - Smart Health & Diet Recommendation System

PulseAI is a premium, AI-powered health assistant designed to provide personalized medical insights and dietary plans. By leveraging a **Dual-AI Architecture**, PulseAI ensures extreme reliability and speed, switching seamlessly between **Google Gemini 2.0 Flash** and **Groq Cloud (Llama 3)**.

---

## 🌟 Why PulseAI?

In a world of generic advice, PulseAI stands out by creating a **Health Profile** for every user. It doesn't just answer questions; it considers your:
- **BMI & Physical Vitals** (Height, Weight, Age)
- **Medical History** (Allergies, Chronic Conditions)
- **Lifestyle** (Sleep patterns, Water intake, Activity levels)

---

## ✨ Features

### 🧠 Dual-AI Logic (Smart Fallback)
PulseAI is built for 100% uptime.
- **Primary**: Google Gemini 2.0 Flash (for deep medical reasoning and multilingual accuracy).
- **Secondary (Fallback)**: Groq / Llama 3 (Ultra-fast recovery if Gemini is rate-limited).

### 🇮🇳 Culturally Relevant Advice
Unlike Western-centric AIs, PulseAI defaults to **Indian Diet Plans**. It understands `Khichdi`, `Dal-Chawal`, `Roti-Sabzi`, and `Buttermilk`, making it practical for Indian households.

### 🌐 Multilingual Support
Built-in support for multiple languages:
- 🇺🇸 **English**
- 🇮🇳 **Hindi (हिन्दी)**
- 🇮🇳 **Gujarati (ગુજરાતી)**

### 📊 Comprehensive Dashboard
- **Instant Recommendations**: Type a condition and get a detailed plan instantly.
- **Streaming UI**: Experience a "Typewriter" effect as the AI thinks and responds.
- **Recommendations History**: Save and visit your previous AI-generated plans.
- **Profile Management**: Update your health data anytime to get better advice.

---

## 📸 UI Showcase

### Homepage
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/2822f5b1-bf76-419b-88f6-0fb2039e2d6f" />


### Dashboard
<img width="1231" height="627" alt="image" src="https://github.com/user-attachments/assets/1e3027a9-9e43-4e2f-86c0-4424404a9dba" />

---

## 🚀 Technical Setup

### Prerequisites
- Python 3.10+
- MySQL Server

### 1. Installation
```powershell
# Clone the repository
git clone https://github.com/MhmdAli011/PulseAi.git
cd PulseAi

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
# Database Configuration
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=pulseai_db

# Flask Configuration
SECRET_KEY=your_secret_key

# AI API Keys
GEMINI_API_KEY=your_google_ai_key
GROQ_API_KEY=your_groq_key
```

### 3. Running the Application
**Development Mode:**
```powershell
python app.py
```
**Production Mode (Stable):**
```powershell
python wsgi.py
```

---

## 📂 Project Structure

- `app.py`: Main Flask application and routing.
- `ai_service.py`: The unified AI provider with Gemini-Groq fallback logic.
- `models.py`: Database schemas for Users, Profiles, and History.
- `static/`: CSS (Tailwind + Custom), JavaScript, and Logo assets.
- `templates/`: Clean, responsive HTML5 Jinja2 templates.
- `wsgi.py`: Production-ready server entry point using Waitress.

---

## 🛠️ Developed With

- **Backend**: Flask, SQLAlchemy, Waitress
- **AI Integration**: Google Generative AI (Gemini), Groq SDK
- **Frontend**: Tailwind CSS, Vanilla JavaScript, Google Fonts
- **Database**: MySQL

---

## 👨‍💻 Author
**MhmdAli011**

*PulseAI - Empowering health with Intelligence.*
