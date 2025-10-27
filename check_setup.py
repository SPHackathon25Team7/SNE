#!/usr/bin/env python3
"""
Quick check to see if database setup is needed
"""
import os
import sqlite3

def check_database_status():
    """Check if database exists and has data"""
    
    if not os.path.exists('customer_data.db'):
        print("❌ Database file 'customer_data.db' not found")
        print("🔧 Run: python setup_database.py")
        return False
    
    try:
        conn = sqlite3.connect('customer_data.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['customer_profiles', 'account_activity', 'interaction_history', 
                          'notification_history', 'recommended_actions']
        
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            print("🔧 Run: python setup_database.py")
            return False
        
        # Check if customer_segment column exists
        cursor.execute("PRAGMA table_info(customer_profiles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'customer_segment' not in columns:
            print("❌ Customer segmentation not completed")
            print("🔧 Run: python setup_database.py")
            return False
        
        # Check if we have Value Seekers
        cursor.execute("SELECT COUNT(*) FROM customer_profiles WHERE customer_segment = 'Value Seekers'")
        value_seekers_count = cursor.fetchone()[0]
        
        if value_seekers_count == 0:
            print("⚠️ No Value Seekers found in database")
            print("🔧 You may need to re-run: python setup_database.py")
            return False
        
        print(f"✅ Database ready with {value_seekers_count} Value Seekers customers")
        print("🚀 You can now run: python app.py")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("🔧 Run: python setup_database.py")
        return False

if __name__ == "__main__":
    check_database_status()