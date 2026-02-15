from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, Response, stream_with_context, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from config import Config
from models import db, User, HealthProfile, Recommendation
from forms import SignUpForm, SignInForm, HealthProfileForm
from groq_service import GroqService
import os
from dotenv import load_dotenv
import google.generativeai as genai
import sys

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

# Initialize Groq service (existing)
try:
    groq_service = GroqService()
except ValueError as e:
    print(f"Warning: {e}")
    groq_service = None

# ==================== NEW: Initialize Gemini API for PulseAI ====================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
GEMINI_MODEL = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try multiple models with fallback
        PREFERRED_MODELS = [
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        for model_name in PREFERRED_MODELS:
            try:
                GEMINI_MODEL = genai.GenerativeModel(model_name=model_name)
                print(f"✅ Gemini model '{model_name}' initialized successfully for PulseAI streaming.")
                break
            except Exception as e:
                print(f"⚠️ Gemini model '{model_name}' not available: {e}")
                continue
        
        if not GEMINI_MODEL:
            print("⚠️ No Gemini models available. PulseAI streaming features will be disabled.")
    except Exception as e:
        print(f"⚠️ Gemini API initialization failed: {e}")
else:
    print("ℹ️ GEMINI_API_KEY not found. PulseAI streaming features will be disabled.")

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# ==================== EXISTING Routes ====================

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(email=form.email.data.lower())
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Log the user in
            login_user(user)
            flash('Account created successfully! Please complete your health profile.', 'success')
            return redirect(url_for('health_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration. Please try again. Error: {str(e)}', 'error')
            print(f"Signup error: {e}")
    
    return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('signin.html', form=form)


@app.route('/signout')
@login_required
def signout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/health-profile', methods=['GET', 'POST'])
@login_required
def health_profile():
    """Health profile form"""
    # Check if profile already exists
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    
    form = HealthProfileForm()
    
    if form.validate_on_submit():
        try:
            if profile:
                # Update existing profile
                profile.full_name = form.full_name.data
                profile.age = form.age.data
                profile.gender = form.gender.data
                profile.height = form.height.data
                profile.weight = form.weight.data
                profile.health_conditions = form.health_conditions.data
                profile.allergies = form.allergies.data
                profile.medications = form.medications.data
                profile.activity_level = form.activity_level.data
                profile.dietary_preference = form.dietary_preference.data
                profile.sleep_hours = form.sleep_hours.data
                profile.water_intake = form.water_intake.data
                profile.health_goal = form.health_goal.data
                profile.calculate_bmi()
                
                flash('Health profile updated successfully!', 'success')
            else:
                # Create new profile
                profile = HealthProfile(
                    user_id=current_user.id,
                    full_name=form.full_name.data,
                    age=form.age.data,
                    gender=form.gender.data,
                    height=form.height.data,
                    weight=form.weight.data,
                    health_conditions=form.health_conditions.data,
                    allergies=form.allergies.data,
                    medications=form.medications.data,
                    activity_level=form.activity_level.data,
                    dietary_preference=form.dietary_preference.data,
                    sleep_hours=form.sleep_hours.data,
                    water_intake=form.water_intake.data,
                    health_goal=form.health_goal.data
                )
                profile.calculate_bmi()
                db.session.add(profile)
                
                flash('Health profile created successfully!', 'success')
            
            db.session.commit()
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while saving your profile. Error: {str(e)}', 'error')
            print(f"Profile save error: {e}")
    
    # Pre-fill form if profile exists
    if profile and request.method == 'GET':
        form.full_name.data = profile.full_name
        form.age.data = profile.age
        form.gender.data = profile.gender
        form.height.data = profile.height
        form.weight.data = profile.weight
        form.health_conditions.data = profile.health_conditions
        form.allergies.data = profile.allergies
        form.medications.data = profile.medications
        form.activity_level.data = profile.activity_level
        form.dietary_preference.data = profile.dietary_preference
        form.sleep_hours.data = profile.sleep_hours
        form.water_intake.data = profile.water_intake
        form.health_goal.data = profile.health_goal
    
    return render_template('health_profile.html', form=form, profile=profile)


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    
    # If no profile exists, redirect to create one
    if not profile:
        flash('Please complete your health profile first.', 'info')
        return redirect(url_for('health_profile'))
    
    # Get recent recommendations
    recent_recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(
        Recommendation.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html', profile=profile, recommendations=recent_recommendations)


@app.route('/get-recommendation', methods=['POST'])
@login_required
def get_recommendation():
    """Generate health recommendation using Groq API (EXISTING FUNCTIONALITY)"""
    try:
        data = request.get_json()
        condition = data.get('condition', '').strip()
        language = data.get('language', 'English')
        
        if not condition:
            return jsonify({'error': 'Please enter a condition or query'}), 400
        
        if not groq_service:
            return jsonify({'error': 'Groq API is not configured. Please set GROQ_API_KEY in .env file'}), 500
        
        # Get user's health profile
        profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
        
        # Generate recommendation
        recommendation_text = groq_service.generate_health_recommendation(
            condition=condition,
            health_profile=profile,
            language=language
        )
        
        # Save recommendation to database
        recommendation = Recommendation(
            user_id=current_user.id,
            condition=condition,
            recommendation_text=recommendation_text,
            language=language
        )
        db.session.add(recommendation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'recommendation': recommendation_text,
            'condition': condition
        })
        
    except Exception as e:
        print(f"Recommendation error: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


# ==================== NEW: PulseAI Streaming API Routes ====================

@app.route('/api/stream', methods=['POST'])
@login_required
def stream_recommendation():
    """NEW: Streaming API endpoint for real-time PulseAI recommendations"""
    try:
        data = request.get_json()
        if not data or 'disease' not in data:
            return jsonify({'error': 'No condition provided'}), 400

        disease = data['disease'].strip()
        language = data.get('language', 'English')
        
        if len(disease) < 2:
            return jsonify({'error': 'Condition name too short'}), 400
        
        if not GEMINI_MODEL:
            return jsonify({'error': 'Gemini API is not configured. Please set GEMINI_API_KEY in .env file'}), 500

        # Get user's health profile for personalized recommendations
        profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
        
        # Build personalized prompt
        profile_context = ""
        if profile:
            profile_context = f"""
User Profile Context:
- Age: {profile.age}, Gender: {profile.gender}
- Health Conditions: {profile.health_conditions or 'None'}
- Allergies: {profile.allergies or 'None'}
- Dietary Preference: {profile.dietary_preference}
- Activity Level: {profile.activity_level}
"""

        prompt = f"""
You are a helpful AI health assistant named PulseAI.

**IMPORTANT: Respond entirely in {language} language.**

Format the response in clean **Markdown** with bold section titles.
All diet suggestions must be based on **Indian cuisine and Indian food items** only.

{profile_context}

Sections:

### 🚫 Things to Avoid
- Each bullet with a short explanation.

### ✅ Recovery Actions
- Each bullet with a short explanation.

### 📅 Daily Life Advice
- Each bullet with a short explanation.

### 🍽️ Sample 1-Day Indian Diet Plan for Recovery
Present this as a **Markdown table** with columns: Meal, Food Items, Notes.
Include rows for: Early Morning, Breakfast, Mid-Morning Snack, Lunch, Evening Snack, Dinner, Before Bed.
All items must be Indian foods (e.g. dal, roti, khichdi, upma, poha, idli, dosa, sabzi, raita, curd, buttermilk, etc.)

Disease/Condition: {disease}
"""

        def generate():
            import json
            try:
                response = GEMINI_MODEL.generate_content(prompt, stream=True)
                for chunk in response:
                    try:
                        text = chunk.text
                        if text:
                            yield f"data: {json.dumps({'text': text})}\n\n"
                    except (ValueError, AttributeError):
                        pass
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                print(f"❌ Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive',
            }
        )
    except Exception as e:
        print(f"❌ Error in /api/stream: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
@login_required
def chat_stream():
    """NEW: Follow-up chat streaming endpoint for PulseAI"""
    import json
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'error': 'No messages provided'}), 400

        messages = data['messages']
        language = data.get('language', 'English')
        
        if not GEMINI_MODEL:
            return jsonify({'error': 'Gemini API is not configured'}), 500

        # Build Gemini chat history
        history = []
        for msg in messages[:-1]:
            history.append({
                'role': msg['role'],
                'parts': [{'text': msg['text']}]
            })

        current_message = f"[Respond in {language}] " + messages[-1]['text']

        def generate():
            try:
                chat = GEMINI_MODEL.start_chat(history=history)
                response = chat.send_message(current_message, stream=True)
                for chunk in response:
                    try:
                        text = chunk.text
                        if text:
                            yield f"data: {json.dumps({'text': text})}\n\n"
                    except (ValueError, AttributeError):
                        pass
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                print(f"❌ Chat stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive',
            }
        )
    except Exception as e:
        print(f"❌ Error in /api/chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """NEW: Health check endpoint for PulseAI"""
    return jsonify({
        'status': 'healthy',
        'groq_available': groq_service is not None,
        'gemini_available': GEMINI_MODEL is not None,
        'supported_languages': ['English', 'Hindi', 'Gujarati', 'Marathi', 'Tamil']
    })


# ==================== NEW: PulseAI Standalone Interface Routes ====================

@app.route('/pulseai')
def pulseai_interface():
    """NEW: Serve standalone PulseAI chat interface"""
    return send_from_directory('.', 'index3.html')


@app.route('/pulseai-simple')
def pulseai_simple():
    """NEW: Serve simple PulseAI interface"""
    return send_from_directory('.', 'index_pulseai.html')


# ==================== EXISTING Routes (continued) ====================

@app.route('/generate-plan/<plan_type>')
@login_required
def generate_plan(plan_type):
    """Generate specific plans (meal, workout, wellness)"""
    try:
        if not groq_service:
            flash('Groq API is not configured. Please set GROQ_API_KEY in .env file', 'error')
            return redirect(url_for('dashboard'))
        
        profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
        
        if not profile:
            flash('Please complete your health profile first.', 'error')
            return redirect(url_for('health_profile'))
        
        # Generate plan
        plan = groq_service.generate_specific_plan(plan_type, profile)
        
        # Save as recommendation
        plan_titles = {
            'meal': 'Personalized Meal Plan',
            'workout': 'Personalized Workout Routine',
            'wellness': 'Comprehensive Wellness Plan'
        }
        
        recommendation = Recommendation(
            user_id=current_user.id,
            condition=plan_titles.get(plan_type, 'Custom Plan'),
            recommendation_text=plan,
            language='English'
        )
        db.session.add(recommendation)
        db.session.commit()
        
        return render_template('plan_view.html', plan=plan, plan_type=plan_type)
        
    except Exception as e:
        print(f"Plan generation error: {e}")
        flash(f'An error occurred while generating the plan: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


@app.route('/history')
@login_required
def history():
    """View recommendation history"""
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(
        Recommendation.created_at.desc()
    ).all()
    
    return render_template('history.html', recommendations=recommendations)


@app.route('/delete-recommendation/<int:rec_id>', methods=['POST'])
@login_required
def delete_recommendation(rec_id):
    """Delete a recommendation"""
    try:
        recommendation = Recommendation.query.get_or_404(rec_id)
        
        # Check if recommendation belongs to current user
        if recommendation.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(recommendation)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Recommendation deleted successfully'})
        
    except Exception as e:
        print(f"Delete error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


# ==================== Database Initialization ====================

def init_database():
    """Initialize database and create tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")


if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Print status
    print("="*80)
    print("🚀 PulseAI Flask Application Starting...")
    print(f"📍 Running on: http://localhost:5000")
    print(f"🤖 Groq API: {'✅ Available' if groq_service else '❌ Not configured'}")
    print(f"🧠 Gemini API: {'✅ Available' if GEMINI_MODEL else '❌ Not configured'}")
    print("="*80)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
