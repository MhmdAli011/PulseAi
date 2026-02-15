"""
Database Initialization Script for PulseAI

This script creates all necessary database tables and can optionally
create a test user for development purposes.
"""

from app import app, db
from models import User, HealthProfile, Recommendation
from werkzeug.security import generate_password_hash
import sys

def init_database():
    """Initialize the database and create all tables"""
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Check if tables exist
            tables = db.engine.table_names()
            print(f"\nCreated tables: {', '.join(tables)}")
            
            return True
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        return False

def create_test_user():
    """Create a test user for development"""
    try:
        with app.app_context():
            # Check if test user already exists
            existing_user = User.query.filter_by(email='test@pulseai.com').first()
            if existing_user:
                print("\n! Test user already exists (test@pulseai.com)")
                return
            
            # Create test user
            test_user = User(email='test@pulseai.com')
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            
            # Create test health profile
            test_profile = HealthProfile(
                user_id=test_user.id,
                full_name='Test User',
                age=30,
                gender='male',
                height=175,
                weight=70,
                health_conditions='None',
                allergies='None',
                medications='None',
                activity_level='moderate',
                dietary_preference='no_preference',
                sleep_hours=7.5,
                water_intake=8,
                health_goal='general_health'
            )
            test_profile.calculate_bmi()
            db.session.add(test_profile)
            db.session.commit()
            
            print("\n✓ Test user created successfully!")
            print("  Email: test@pulseai.com")
            print("  Password: password123")
            print("\nYou can now log in with these credentials.")
            
    except Exception as e:
        print(f"\n✗ Error creating test user: {e}")
        db.session.rollback()

def drop_all_tables():
    """Drop all database tables (USE WITH CAUTION!)"""
    try:
        with app.app_context():
            print("\n⚠ WARNING: This will delete ALL data from the database!")
            confirm = input("Type 'YES' to confirm: ")
            
            if confirm == 'YES':
                db.drop_all()
                print("✓ All tables dropped successfully!")
            else:
                print("Operation cancelled.")
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")

def show_stats():
    """Display database statistics"""
    try:
        with app.app_context():
            user_count = User.query.count()
            profile_count = HealthProfile.query.count()
            recommendation_count = Recommendation.query.count()
            
            print("\n=== Database Statistics ===")
            print(f"Total Users: {user_count}")
            print(f"Total Health Profiles: {profile_count}")
            print(f"Total Recommendations: {recommendation_count}")
            
    except Exception as e:
        print(f"✗ Error getting statistics: {e}")

def main():
    """Main function to run database operations"""
    print("=" * 50)
    print("PulseAI Database Initialization")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'init':
            init_database()
        elif command == 'test':
            create_test_user()
        elif command == 'drop':
            drop_all_tables()
        elif command == 'stats':
            show_stats()
        elif command == 'reset':
            drop_all_tables()
            init_database()
            create_test_user()
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  init  - Create database tables")
            print("  test  - Create test user")
            print("  drop  - Drop all tables (DANGER!)")
            print("  stats - Show database statistics")
            print("  reset - Drop, recreate, and add test user")
    else:
        # Default: initialize database
        success = init_database()
        
        if success:
            print("\n" + "=" * 50)
            print("Database initialized successfully!")
            print("=" * 50)
            
            # Ask if user wants to create test user
            create_test = input("\nCreate a test user for development? (y/n): ")
            if create_test.lower() == 'y':
                create_test_user()
            
            print("\nYou can now run the application with:")
            print("  python app.py")

if __name__ == '__main__':
    main()
