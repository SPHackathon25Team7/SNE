#!/usr/bin/env python3
"""
Test script to call the notifications API and see debug output
"""
import requests
import json

def test_notifications():
    """Test the notifications API endpoint"""
    
    try:
        print("🔍 Testing notifications API...")
        
        # Make request to notifications endpoint
        response = requests.get('http://localhost:5000/api/notifications')
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Got {len(notifications)} notifications")
            
            for i, notification in enumerate(notifications):
                print(f"\n📧 Notification {i+1}:")
                print(f"  Customer ID: {notification.get('customer_id')}")
                print(f"  Customer Name: {notification.get('customer_name')}")
                print(f"  Opted In: {notification.get('opted_in')}")
                print(f"  Priority: {notification.get('priority')}")
                print(f"  Channel: {notification.get('preferred_channel')}")
                print(f"  Message: {notification.get('message')}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_notifications()