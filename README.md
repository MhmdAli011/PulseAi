# 🏥 PulseAI - AI Health Assistant

PulseAI is a premium, AI-powered health and diet recommendation system. It uses **Google Gemini 2.0 Flash** as its primary diagnostic brain, with an automatic fallback to **Groq** to ensure 100% availability.

## ✨ Features

- **Personalized Health Plans**: Tailored advice based on your age, BMI, and conditions.
- **Dual-AI Architecture**: Seamlessly switches between Gemini and Groq.
- **Indian Diet Focus**: Specific recommendations for Indian cuisine (Dal, Sabzi, etc.).
- **Modern Dashboard**: Beautiful UI with teal-to-cyan gradients and smooth interaction.

## 📸 UI Showcase

![Homepage Showcase](file:///C:/Users/moham/.gemini/antigravity/brain/6eb3b379-789e-432a-9ec7-36fa7a1871d2/media__1772043960682.png)
*Modern Landing Page with Hero Section*

![PulseAI Branding](file:///C:/Users/moham/.gemini/antigravity/brain/6eb3b379-789e-432a-9ec7-36fa7a1871d2/media__1772044159879.png)
*Sleek Navbar and Branding*

![Dashboard UI](file:///C:/Users/moham/.gemini/antigravity/brain/6eb3b379-789e-432a-9ec7-36fa7a1871d2/media__1772046307663.png)
*Dashboard featuring the Gemini-powered Recommendation Input*

## 🚀 Quick Start

1. **Clone the project**
2. **Install requirements:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Configure API Keys in `.env`:**
   ```
   GEMINI_API_KEY=your_key
   GROQ_API_KEY=your_key
   ```
4. **Run the production server:**
   ```powershell
   python wsgi.py
   ```

## 🛠️ Tech Stack

- **Frontend**: Tailwind CSS, Vanilla JS, Google Fonts (Inter)
- **Backend**: Python, Flask, Waitress (WSGI)
- **Database**: MySQL / SQLAlchemy
- **AI**: Google Gemini SDK, Groq SDK
