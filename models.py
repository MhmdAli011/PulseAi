from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with health profile
    health_profile = db.relationship('HealthProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class HealthProfile(db.Model):
    """Health profile model for storing user health data"""
    __tablename__ = 'health_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Personal Information
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    
    # Physical Measurements
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    bmi = db.Column(db.Float)
    
    # Health Conditions
    health_conditions = db.Column(db.Text)  # Comma-separated conditions
    allergies = db.Column(db.Text)  # Comma-separated allergies
    medications = db.Column(db.Text)  # Current medications
    
    # Lifestyle
    activity_level = db.Column(db.String(50))  # Sedentary, Light, Moderate, Active, Very Active
    dietary_preference = db.Column(db.String(50))  # Vegetarian, Vegan, Non-Vegetarian, etc.
    sleep_hours = db.Column(db.Float)
    water_intake = db.Column(db.Float)  # glasses per day
    
    # Goals
    health_goal = db.Column(db.String(100))  # Weight loss, Muscle gain, General health, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_bmi(self):
        """Calculate BMI from height and weight"""
        if self.height and self.weight:
            height_in_meters = self.height / 100
            self.bmi = round(self.weight / (height_in_meters ** 2), 2)
    
    def __repr__(self):
        return f'<HealthProfile {self.full_name}>'


class Recommendation(db.Model):
    """Model for storing generated health and diet recommendations"""
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Condition/Query
    condition = db.Column(db.String(200), nullable=False)
    
    # Generated Recommendation
    recommendation_text = db.Column(db.Text, nullable=False)
    
    # Metadata
    language = db.Column(db.String(20), default='English')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Recommendation {self.condition}>'
