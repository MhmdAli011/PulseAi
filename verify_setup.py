"""
PulseAI Setup Verification Script

This script checks if your environment is properly configured
and all dependencies are installed correctly.
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - NEEDS 3.8+")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'wtforms',
        'pymysql',
        'cryptography',
        'python-dotenv',
        'groq',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} - Installed")
        except ImportError:
            print(f"✗ {package} - NOT FOUND")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("✗ .env file - NOT FOUND")
        print("  Copy .env.example to .env and configure it")
        return False
    
    print("✓ .env file - EXISTS")
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'SECRET_KEY', 'GROQ_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your-'):
            missing_vars.append(var)
            print(f"  ⚠ {var} - NOT CONFIGURED")
        else:
            print(f"  ✓ {var} - Set")
    
    return len(missing_vars) == 0

def check_mysql_connection():
    """Check if MySQL connection can be established"""
    try:
        import pymysql
        from dotenv import load_dotenv
        load_dotenv()
        
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            charset='utf8mb4'
        )
        
        print("✓ MySQL Connection - OK")
        
        # Check if database exists
        cursor = connection.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{os.getenv('DB_NAME', 'pulseai_db')}'")
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Database '{os.getenv('DB_NAME')}' - EXISTS")
        else:
            print(f"⚠ Database '{os.getenv('DB_NAME')}' - NOT FOUND")
            print(f"  Run: CREATE DATABASE {os.getenv('DB_NAME')};")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MySQL Connection - FAILED")
        print(f"  Error: {str(e)}")
        return False

def check_groq_api():
    """Check if Groq API key is valid"""
    try:
        from groq import Groq
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key or api_key.startswith('your-'):
            print("⚠ Groq API Key - NOT CONFIGURED")
            print("  Get your key from https://console.groq.com")
            return False
        
        # Try to initialize client
        client = Groq(api_key=api_key)
        print("✓ Groq API Key - CONFIGURED")
        
        # Optional: Test API call (commented out to avoid unnecessary API usage)
        # print("  Testing API connection...")
        # response = client.chat.completions.create(
        #     messages=[{"role": "user", "content": "Hello"}],
        #     model="mixtral-8x7b-32768",
        #     max_tokens=10
        # )
        # print("✓ Groq API - WORKING")
        
        return True
        
    except Exception as e:
        print(f"✗ Groq API - ERROR")
        print(f"  Error: {str(e)}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("PulseAI Setup Verification")
    print("=" * 60)
    print()
    
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies()[0],
        'Environment File': check_env_file(),
        'MySQL Connection': check_mysql_connection(),
        'Groq API': check_groq_api()
    }
    
    print()
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check:.<40} {status}")
    
    print()
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run PulseAI.")
        print()
        print("Next steps:")
        print("  1. Initialize database: python init_db.py")
        print("  2. Run application: python app.py")
        print("  3. Visit: http://localhost:5000")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        print()
        print("Common solutions:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Configure .env: cp .env.example .env")
        print("  - Start MySQL server")
        print("  - Create database: CREATE DATABASE pulseai_db;")
        print("  - Get Groq API key: https://console.groq.com")
    
    print()
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
