# PulseAI - AI-Powered Health & Diet Recommendations

PulseAI is a comprehensive web application that provides personalized health and diet recommendations using AI technology powered by Groq API. Users can track their health data, receive customized recommendations, and generate meal plans, workout routines, and wellness plans.

## Features

- **User Authentication**: Secure sign up and sign in with email and password
- **Health Profile Management**: Comprehensive health data collection and tracking
- **AI-Powered Recommendations**: Get personalized health advice using Groq API
- **Multi-Language Support**: Recommendations in English, Hindi, and Gujarati
- **Quick Plans**: Generate meal plans, workout routines, and wellness plans
- **History Tracking**: View and manage all past recommendations
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **User Data Persistence**: MySQL database for secure data storage

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Integration**: Groq API (Mixtral model)
- **Authentication**: Flask-Login
- **Form Validation**: WTForms

## Prerequisites

Before running the application, ensure you have:

1. Python 3.8 or higher
2. MySQL Server 5.7 or higher
3. pip (Python package manager)
4. Groq API key (get from https://groq.com)

## Installation

### 1. Clone or Download the Project

```bash
cd pulseai_project
```

### 2. Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

Create a MySQL database for the application:

```sql
CREATE DATABASE pulseai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure Environment Variables

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=pulseai_db

# Flask Configuration
SECRET_KEY=your-very-secret-key-change-this
FLASK_ENV=development

# Groq API Configuration
GROQ_API_KEY=your-groq-api-key-here
```

**Important**: 
- Replace `your_mysql_password` with your MySQL root password
- Replace `your-groq-api-key-here` with your actual Groq API key
- Generate a secure SECRET_KEY for production

### 6. Initialize Database

The application will automatically create the necessary tables on first run. You can also manually initialize:

```python
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     print("Database tables created!")
>>> exit()
```

## Running the Application

### Development Mode

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Usage Guide

### 1. Sign Up

1. Navigate to http://localhost:5000
2. Click "Sign Up" in the navigation bar
3. Enter your email and password
4. Click "Sign Up" to create your account

### 2. Complete Health Profile

After signing up, you'll be redirected to complete your health profile:

- **Personal Information**: Name, age, gender
- **Physical Measurements**: Height, weight (BMI calculated automatically)
- **Health Conditions**: Any existing conditions, allergies, medications
- **Lifestyle**: Activity level, dietary preferences, sleep, water intake
- **Health Goals**: Weight loss, muscle gain, general health, etc.

### 3. Get Recommendations

From your dashboard:

1. Enter a health condition or query (e.g., "Common Cold", "Diabetes diet")
2. Select your preferred language (English, Hindi, or Gujarati)
3. Click "Get Plan" to receive personalized recommendations

### 4. Generate Quick Plans

Click on any quick plan card to generate:

- **Meal Plan**: 7-day personalized meal plan
- **Workout Routine**: Customized exercise schedule
- **Wellness Plan**: Comprehensive health and wellness guide

### 5. View History

Access all your past recommendations from the History page.

## Project Structure

```
pulseai_project/
│
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── forms.py               # WTForms for validation
├── groq_service.py        # Groq API integration
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── signup.html
│   ├── signin.html
│   ├── dashboard.html
│   ├── health_profile.html
│   ├── history.html
│   ├── plan_view.html
│   ├── 404.html
│   └── 500.html
│
└── static/                # Static files
    ├── css/
    │   └── style.css      # Main stylesheet
    └── js/
        └── main.js        # Frontend JavaScript
```

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- password_hash
- created_at

### Health Profiles Table
- id (Primary Key)
- user_id (Foreign Key → Users)
- full_name, age, gender
- height, weight, bmi
- health_conditions, allergies, medications
- activity_level, dietary_preference
- sleep_hours, water_intake
- health_goal
- created_at, updated_at

### Recommendations Table
- id (Primary Key)
- user_id (Foreign Key → Users)
- condition
- recommendation_text
- language
- created_at

## API Integration

### Groq API

The application uses the Groq API with the Mixtral-8x7b model for generating recommendations. The `groq_service.py` module handles:

- Health recommendation generation based on user profile
- Multi-language support
- Context-aware responses
- Specific plan generation (meal, workout, wellness)

## Security Features

- Password hashing using Werkzeug security
- CSRF protection with Flask-WTF
- Session management with Flask-Login
- SQL injection prevention with SQLAlchemy ORM
- Input validation and sanitization

## Troubleshooting

### Database Connection Error

**Error**: `Can't connect to MySQL server`

**Solution**:
- Ensure MySQL server is running
- Check DB_HOST, DB_USER, and DB_PASSWORD in `.env`
- Verify database `pulseai_db` exists

### Groq API Error

**Error**: `GROQ_API_KEY is not set`

**Solution**:
- Add your Groq API key to `.env` file
- Restart the application

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Change port in app.py or kill the process using port 5000
# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux
lsof -ti:5000 | xargs kill -9
```

## Future Enhancements

- Google OAuth integration
- Email verification
- Password reset functionality
- Export recommendations as PDF
- Nutrition tracking
- Exercise logging
- Community features
- Mobile app (React Native)
- Advanced analytics and insights

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please contact the development team.

## Acknowledgments

- Groq for providing the AI API
- Flask community for excellent documentation
- All open-source contributors

---

**Note**: This is an educational project. Always consult healthcare professionals for medical advice.
