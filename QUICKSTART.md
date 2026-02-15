# PulseAI - Quick Start Guide

Get PulseAI up and running in 5 minutes!

## Step 1: Prerequisites Check

Before starting, make sure you have:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] MySQL Server running
- [ ] Groq API key (get free at https://console.groq.com)

## Step 2: Install Dependencies

```bash
cd pulseai_project
pip install -r requirements.txt
```

## Step 3: Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your settings:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=pulseai_db

SECRET_KEY=your-secret-key-here
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

## Step 4: Create Database

In MySQL, run:
```sql
CREATE DATABASE pulseai_db;
```

Or use command line:
```bash
mysql -u root -p -e "CREATE DATABASE pulseai_db;"
```

## Step 5: Initialize Database Tables

```bash
python init_db.py
```

This will:
- Create all necessary tables
- Optionally create a test user

## Step 6: Run the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

## Step 7: First Use

1. Click **Sign Up** and create an account
2. Complete your **Health Profile**
3. Start getting personalized recommendations!

## Troubleshooting

### Can't connect to MySQL?
- Ensure MySQL is running: `mysql -u root -p`
- Check DB_PASSWORD in `.env`

### Groq API not working?
- Verify GROQ_API_KEY in `.env`
- Test your key at https://console.groq.com

### Port 5000 already in use?
Edit `app.py` line: `app.run(debug=True, host='0.0.0.0', port=5001)`

## Test Credentials (if you created test user)

- Email: `test@pulseai.com`
- Password: `password123`

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize health profile
- Explore different recommendation types
- Try multi-language support (Hindi, Gujarati)

---

**Need Help?** Check the full README or raise an issue.
