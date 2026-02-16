from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, Response, stream_with_context, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from config import Config
from models import db, User, HealthProfile, Recommendation
from forms import SignUpForm, SignInForm, HealthProfileForm
from groq_service import GroqService
import os
from dotenv import load_dotenv
from google import genai
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for API routes
CORS(app)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'
login_manager.login_message = 'Please log in to access this page.'

# Initialize Groq service
try:
    groq_service = GroqService()
except ValueError as e:
    print(f"Warning: {e}")
    groq_service = None

# ==================== Initialize Gemini API ====================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
GEMINI_CLIENT = None

if GEMINI_API_KEY:
    try:
        GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Gemini client initialized successfully.")
    except Exception as e:
        print(f"⚠️ Gemini initialization failed: {e}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== Authentication & Profile Routes ====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data.lower())
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created! Please complete your profile.', 'success')
            return redirect(url_for('health_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Registration error. Please try again.', 'error')
    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('signin.html', form=form)

@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/health-profile', methods=['GET', 'POST'])
@login_required
def health_profile():
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    form = HealthProfileForm()
    
    if form.validate_on_submit():
        try:
            if not profile:
                profile = HealthProfile(user_id=current_user.id)
                db.session.add(profile)
            
            form.populate_obj(profile) # Efficiently maps form fields to model
            profile.calculate_bmi()
            db.session.commit()
            flash('Health profile saved!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    if profile and request.method == 'GET':
        form.process(obj=profile)
    return render_template('health_profile.html', form=form, profile=profile)

@app.route('/dashboard')
@login_required
def dashboard():
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('health_profile'))
    
    recent_recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(
        Recommendation.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html', profile=profile, recommendations=recent_recommendations)

# ==================== NEW: Gemini PulseAI Streaming Routes ====================

@app.route('/api/stream', methods=['POST'])
@login_required
def stream_recommendation():

    if not GEMINI_CLIENT:
        return jsonify({'error': 'Gemini not initialized'}), 500

    try:
        data = request.get_json()
        disease = data.get('disease', '').strip()
        language = data.get('language', 'English')

        profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
        if not profile:
            return jsonify({'error': 'Profile missing'}), 400

        prompt = f"""
Respond entirely in {language}.
Provide an Indian diet plan for {disease}.
Age: {profile.age}
Gender: {profile.gender}
Conditions: {profile.health_conditions or 'None'}
Include bold headings and 1-day table.
"""

        response = GEMINI_CLIENT.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        rec = Recommendation(
            user_id=current_user.id,
            condition=disease,
            recommendation_text=response.text,
            language=language
        )
        db.session.add(rec)
        db.session.commit()

        return jsonify({
            "recommendation": response.text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/chat', methods=['POST'])
@login_required
def chat_stream():

    if not GEMINI_CLIENT:
        return jsonify({'error': 'Gemini not initialized'}), 500

    try:
        data = request.get_json()
        messages = data.get('messages', [])
        language = data.get('language', 'English')

        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        # Build conversation text
        conversation_text = ""
        for msg in messages:
            conversation_text += f"{msg['role']}: {msg['text']}\n"

        prompt = f"""
Respond entirely in {language}.

Conversation so far:
{conversation_text}

Continue the conversation.
"""

        response = GEMINI_CLIENT.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        return jsonify({
            "reply": response.text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== History & Plan Routes ====================

@app.route('/history')
@login_required
def history():
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(
        Recommendation.created_at.desc()
    ).all()
    return render_template('history.html', recommendations=recommendations)

@app.route('/generate-plan/<plan_type>')
@login_required
def generate_plan(plan_type):
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    if not profile: return redirect(url_for('health_profile'))
    
    # Use Groq or Gemini for static long-form plans
    plan = groq_service.generate_specific_plan(plan_type, profile) if groq_service else "Service Unavailable"
    
    rec = Recommendation(user_id=current_user.id, condition=f"{plan_type.title()} Plan", recommendation_text=plan)
    db.session.add(rec)
    db.session.commit()
    return render_template('plan_view.html', plan=plan, plan_type=plan_type)

@app.route('/delete-recommendation/<int:rec_id>', methods=['POST'])
@login_required
def delete_recommendation(rec_id):
    rec = Recommendation.query.get_or_404(rec_id)
    if rec.user_id == current_user.id:
        db.session.delete(rec)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Unauthorized'}), 403

# ==================== Init & Run ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)