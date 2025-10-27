#!/usr/bin/env python3
"""
Simple debug script to check database data
"""
import sqlite3

def debug_value_seekers():
    """Debug Value Seekers data directly from database"""
    
    print("🔍 DEBUGGING VALUE SEEKERS DATA")
    print("=" * 60)
    
    conn = sqlite3.connect('customer_data.db')
    cursor = conn.cursor()
    
    # Get Value Seekers with all details
    query = """
    SELECT 
        cp.Customer_ID,
        cp.Name,
        cp.Opted_In,
        cp.Preferred_Channel,
        cp.customer_segment,
        aa.Churn_Risk_Score,
        aa.Account_Status,
        aa.Engagement_Score
    FROM customer_profiles cp
    LEFT JOIN account_activity aa ON cp.Customer_ID = aa.Customer_ID
    WHERE cp.customer_segment = 'Value Seekers'
    ORDER BY cp.Customer_ID
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    
    print(f"Found {len(rows)} Value Seekers:")
    print(f"Columns: {column_names}")
    print()
    
    for row in rows:
        data = dict(zip(column_names, row))
        print(f"ID: {data['Customer_ID']}")
        print(f"  Name: {data['Name']}")
        print(f"  Opted_In: {data['Opted_In']}")
        print(f"  Preferred_Channel: {data['Preferred_Channel']}")
        print(f"  Churn_Risk_Score: {data['Churn_Risk_Score']}")
        print(f"  Account_Status: {data['Account_Status']}")
        print()
    
    conn.close()

if __name__ == "__main__":
    debug_value_seekers()