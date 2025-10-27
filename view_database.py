#!/usr/bin/env python3
"""
Database viewer to inspect the contents of customer_data.db
"""
import sqlite3
import os
import sys

try:
    import pandas as pd
except ImportError:
    print("❌ pandas not available, using basic display")
    pd = None

def view_database():
    """View all tables and data in the database"""
    
    if not os.path.exists('customer_data.db'):
        print("❌ Database file 'customer_data.db' not found")
        print("Run: python setup_database.py")
        return
    
    conn = sqlite3.connect('customer_data.db')
    
    print("🗄️ DATABASE CONTENTS")
    print("=" * 60)
    
    # Get all table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📋 Tables found: {', '.join(tables)}")
    print()
    
    for table in tables:
        print(f"📊 TABLE: {table}")
        print("-" * 40)
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print("Columns:", [col[1] for col in columns])
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Rows: {count}")
        
        # Show first few rows
        if pd:
            df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
            print("\nFirst 5 rows:")
            print(df.to_string(index=False))
        else:
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            print(f"\nColumns: {column_names}")
            print("First 5 rows:")
            for row in rows:
                print(f"  {dict(zip(column_names, row))}")
        print("\n" + "=" * 60 + "\n")
    
    # Focus on Value Seekers
    print("🎯 VALUE SEEKERS ANALYSIS")
    print("-" * 40)
    
    try:
        query = """
        SELECT 
            cp.Customer_ID,
            cp.Name,
            cp.customer_segment,
            cp.Opted_In,
            cp.Preferred_Channel,
            cp.Location,
            cp.Age,
            aa.Churn_Risk_Score,
            aa.Engagement_Score,
            aa.Account_Status
        FROM customer_profiles cp
        LEFT JOIN account_activity aa ON cp.Customer_ID = aa.Customer_ID
        WHERE cp.customer_segment = 'Value Seekers'
        ORDER BY cp.Customer_ID
        """
        
        if pd:
            value_seekers = pd.read_sql_query(query, conn)
            if len(value_seekers) > 0:
                print(f"Found {len(value_seekers)} Value Seekers:")
                print(value_seekers.to_string(index=False))
            else:
                print("❌ No Value Seekers found!")
        else:
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            if rows:
                print(f"Found {len(rows)} Value Seekers:")
                print(f"Columns: {column_names}")
                for row in rows:
                    print(f"  {dict(zip(column_names, row))}")
            else:
                print("❌ No Value Seekers found!")
            
            # Check what segments exist
            cursor.execute("SELECT customer_segment, COUNT(*) FROM customer_profiles GROUP BY customer_segment")
            segments = cursor.fetchall()
            print("\nActual segments in database:")
            for segment, count in segments:
                print(f"  {segment}: {count} customers")
                
    except Exception as e:
        print(f"Error querying Value Seekers: {e}")
    
    # Check for customers without segments
    print("\n🔍 SEGMENTATION STATUS")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) FROM customer_profiles WHERE customer_segment IS NULL")
    unsegmented = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customer_profiles")
    total = cursor.fetchone()[0]
    
    print(f"Total customers: {total}")
    print(f"Unsegmented customers: {unsegmented}")
    print(f"Segmented customers: {total - unsegmented}")
    
    conn.close()

def view_specific_customer(customer_id):
    """View complete profile for a specific customer"""
    conn = sqlite3.connect('customer_data.db')
    
    print(f"👤 CUSTOMER {customer_id} COMPLETE PROFILE")
    print("=" * 50)
    
    # Basic profile
    print("📋 BASIC PROFILE:")
    df = pd.read_sql_query("SELECT * FROM customer_profiles WHERE Customer_ID = ?", conn, params=[customer_id])
    if len(df) > 0:
        for col in df.columns:
            print(f"  {col}: {df.iloc[0][col]}")
    else:
        print("  Customer not found!")
        return
    
    print("\n💼 ACCOUNT ACTIVITY:")
    df = pd.read_sql_query("SELECT * FROM account_activity WHERE Customer_ID = ?", conn, params=[customer_id])
    if len(df) > 0:
        for col in df.columns:
            print(f"  {col}: {df.iloc[0][col]}")
    
    print("\n💬 RECENT INTERACTIONS:")
    df = pd.read_sql_query("SELECT * FROM interaction_history WHERE Customer_ID = ? ORDER BY [Date & Time] DESC LIMIT 3", conn, params=[customer_id])
    if len(df) > 0:
        print(df.to_string(index=False))
    else:
        print("  No interactions found")
    
    print("\n📧 NOTIFICATION HISTORY:")
    df = pd.read_sql_query("SELECT * FROM notification_history WHERE Customer_ID = ? ORDER BY Sent_Date DESC LIMIT 3", conn, params=[customer_id])
    if len(df) > 0:
        print(df.to_string(index=False))
    else:
        print("  No notifications found")
    
    print("\n📝 RECOMMENDED ACTIONS:")
    df = pd.read_sql_query("SELECT * FROM recommended_actions WHERE Customer_ID = ?", conn, params=[customer_id])
    if len(df) > 0:
        print(df.to_string(index=False))
    else:
        print("  No recommended actions found")
    
    conn.close()

if __name__ == "__main__":
    import os
    import sys
    
    if len(sys.argv) > 1:
        # View specific customer
        customer_id = sys.argv[1]
        view_specific_customer(customer_id)
    else:
        # View entire database
        view_database()
        
        print("\n💡 USAGE:")
        print("  python view_database.py           - View all tables")
        print("  python view_database.py 3000     - View specific customer")