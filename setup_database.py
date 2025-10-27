#!/usr/bin/env python3
"""
Setup script to initialize the customer database
Run this before starting the Flask application
"""

import os
import sys

def main():
    print("🚀 Setting up Customer Database...")
    print("=" * 50)
    
    # Check if user_data folder exists
    if not os.path.exists('user_data'):
        print("❌ Error: 'user_data' folder not found!")
        print("Please ensure the user_data folder with CSV files exists.")
        return False
    
    # Check for required CSV files
    required_files = [
        'user_data/Customer Profiles.csv',
        'user_data/Account Activity Logs.csv',
        'user_data/Interaction History.csv',
        'user_data/Notification History.csv',
        'user_data/Recommended Actions.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Error: Missing required CSV files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ All required CSV files found")
    
    # Import and run database setup
    try:
        from database_setup import main as setup_main
        setup_main()
        print("\n🎉 Database setup completed successfully!")
        print("You can now run the Flask application with: python app.py")
        return True
    except ImportError as e:
        print(f"❌ Error importing database_setup: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)