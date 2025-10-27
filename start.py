#!/usr/bin/env python3
"""
Smart startup script for the Smart Notification Engine
Checks database status and starts the application
"""
import os
import sys
import subprocess

def check_database():
    """Check if database is ready"""
    if not os.path.exists('customer_data.db'):
        print("❌ Database not found!")
        print("🔧 Setting up database from CSV files...")
        
        # Run database setup
        result = subprocess.run([sys.executable, 'setup_database.py'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Database setup failed!")
            print(result.stderr)
            return False
        
        print("✅ Database setup completed!")
    
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Smart Notification Engine...")
    print("=" * 50)
    
    # Check database
    if not check_database():
        print("❌ Cannot start application - database setup failed")
        return False
    
    # Check if user_data folder exists
    if not os.path.exists('user_data'):
        print("⚠️ Warning: user_data folder not found")
        print("The application will use existing database data")
    
    print("✅ All checks passed!")
    print("🌐 Starting Flask application...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🎯 Focus: Value Seekers customers only")
    print("=" * 50)
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)