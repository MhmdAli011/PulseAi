from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, Response, stream_with_context
# Final trigger for Vercel deployment
import json
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from config import Config
from models import db, User, HealthProfile, Recommendation
from forms import SignUpForm, SignInForm, HealthProfileForm
from groq_service import GroqService
import os
from dotenv import load_dotenv

# ==================== Load Environment Variables ====================
load_dotenv()

# ==================== Initialize Flask App ====================
app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

# ==================== Initialize Extensions ====================
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'
login_manager.login_message = 'Please log in to access this page.'

# ==================== Initialize Groq Service ====================
try:
    groq_service = GroqService()
    print("✅ Groq initialized successfully.")
except Exception as e:
    print(f"⚠️ Groq initialization failed: {e}")
    groq_service = None


# ==================== User Loader ====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== Authentication Routes ====================

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
            flash('Account created successfully!', 'success')
            return redirect(url_for('health_profile'))
        except Exception:
            db.session.rollback()
            flash('Registration failed. Try again.', 'error')

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
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'error')

    return render_template('signin.html', form=form)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


# ==================== Health Profile ====================

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

            form.populate_obj(profile)
            profile.calculate_bmi()
            db.session.commit()

            flash('Profile saved successfully!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')

    if profile and request.method == 'GET':
        form.process(obj=profile)

    return render_template('health_profile.html', form=form, profile=profile)


# ==================== Dashboard ====================

@app.route('/dashboard')
@login_required
def dashboard():
    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()

    if not profile:
        flash('Please complete your health profile first.', 'info')
        return redirect(url_for('health_profile'))

    recent_recommendations = Recommendation.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Recommendation.created_at.desc()
    ).limit(5).all()

    return render_template(
        'dashboard.html',
        profile=profile,
        recommendations=recent_recommendations
    )


# ==================== Generate Plan (Groq) ====================

@app.route('/api/stream', methods=['POST'])
@login_required
def stream_recommendation():
    if not groq_service:
        return jsonify({'error': 'Groq service not available'}), 500

    data = request.get_json()
    disease = data.get('disease', '').strip()
    language = data.get('language', 'English')

    profile = HealthProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'error': 'Health profile missing'}), 400

    def generate():
        try:
            # Stream response from Groq
            stream = groq_service.generate_health_recommendation_stream(
                condition=disease,
                health_profile=profile,
                language=language
            )
            
            collected_text = ""
            for chunk in stream:
                if chunk:
                    collected_text += chunk
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
            
            # Save to database after complete generation
            with app.app_context():
                rec = Recommendation(
                    user_id=current_user.id,
                    condition=disease,
                    recommendation_text=collected_text,
                    language=language
                )
                db.session.add(rec)
                db.session.commit()
            
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )



# ==================== Chat Route (Groq) ====================

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_stream():
    if not groq_service:
        return jsonify({'error': 'Groq service not available'}), 500

    data = request.get_json()
    messages = data.get('messages', [])
    language = data.get('language', 'English')

    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    def generate():
        try:
            # Construct a conversation context
            conversation_context = "Conversation History:\n"
            for msg in messages[:-1]:
                conversation_context += f"{msg['role']}: {msg['text']}\n"
            
            last_user_msg = messages[-1]['text']
            
            # Use the streaming method (conceptually similar for chat)
            # For simplicity, we reuse the same streaming method but pass conversation as condition
            # Ideally, detailed chat logic would be a separate method, but this adapts the existing one
            full_prompt = f"{conversation_context}\nUser asks: {last_user_msg}"
            
            stream = groq_service.generate_health_recommendation_stream(
                condition=full_prompt,
                health_profile=None, # Context already in messages
                language=language
            )

            for chunk in stream:
                if chunk:
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


# ==================== History ====================

@app.route('/history')
@login_required
def history():
    recommendations = Recommendation.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Recommendation.created_at.desc()
    ).all()

    return render_template('history.html', recommendations=recommendations)


# ==================== Delete Recommendation ====================

@app.route('/delete-recommendation/<int:rec_id>', methods=['POST'])
@login_required
def delete_recommendation(rec_id):
    rec = Recommendation.query.get_or_404(rec_id)

    if rec.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(rec)
    db.session.commit()

    return jsonify({'success': True})


# ==================== Run ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
