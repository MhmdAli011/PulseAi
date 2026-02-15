from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models import User

class SignUpForm(FlaskForm):
    """Sign up form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    def validate_email(self, field):
        """Check if email already exists"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered. Please use a different email.')


class SignInForm(FlaskForm):
    """Sign in form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])


class HealthProfileForm(FlaskForm):
    """Health profile form for collecting user health data"""
    
    # Personal Information
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    
    age = IntegerField('Age', validators=[
        DataRequired(message='Age is required'),
        NumberRange(min=1, max=120, message='Please enter a valid age')
    ])
    
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Gender is required')])
    
    # Physical Measurements
    height = FloatField('Height (cm)', validators=[
        DataRequired(message='Height is required'),
        NumberRange(min=50, max=300, message='Please enter a valid height')
    ])
    
    weight = FloatField('Weight (kg)', validators=[
        DataRequired(message='Weight is required'),
        NumberRange(min=20, max=500, message='Please enter a valid weight')
    ])
    
    # Health Conditions
    health_conditions = TextAreaField('Health Conditions', validators=[
        Length(max=500, message='Maximum 500 characters allowed')
    ])
    
    allergies = TextAreaField('Allergies', validators=[
        Length(max=500, message='Maximum 500 characters allowed')
    ])
    
    medications = TextAreaField('Current Medications', validators=[
        Length(max=500, message='Maximum 500 characters allowed')
    ])
    
    # Lifestyle
    activity_level = SelectField('Activity Level', choices=[
        ('', 'Select Activity Level'),
        ('sedentary', 'Sedentary (Little or no exercise)'),
        ('light', 'Light (Exercise 1-3 days/week)'),
        ('moderate', 'Moderate (Exercise 3-5 days/week)'),
        ('active', 'Active (Exercise 6-7 days/week)'),
        ('very_active', 'Very Active (Physical job or intense training)')
    ], validators=[DataRequired(message='Activity level is required')])
    
    dietary_preference = SelectField('Dietary Preference', choices=[
        ('', 'Select Dietary Preference'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('non_vegetarian', 'Non-Vegetarian'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Keto'),
        ('paleo', 'Paleo'),
        ('no_preference', 'No Preference')
    ], validators=[DataRequired(message='Dietary preference is required')])
    
    sleep_hours = FloatField('Average Sleep Hours per Night', validators=[
        DataRequired(message='Sleep hours is required'),
        NumberRange(min=0, max=24, message='Please enter valid sleep hours (0-24)')
    ])
    
    water_intake = FloatField('Water Intake (glasses per day)', validators=[
        DataRequired(message='Water intake is required'),
        NumberRange(min=0, max=30, message='Please enter valid water intake')
    ])
    
    # Goals
    health_goal = SelectField('Primary Health Goal', choices=[
        ('', 'Select Health Goal'),
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('general_health', 'General Health & Wellness'),
        ('disease_management', 'Disease Management'),
        ('improved_fitness', 'Improved Fitness'),
        ('better_sleep', 'Better Sleep'),
        ('stress_management', 'Stress Management')
    ], validators=[DataRequired(message='Health goal is required')])
