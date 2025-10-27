#!/usr/bin/env python3
"""
Test the actual notification generation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import SmartNotificationEngine

def test_notification_generation():
    """Test the actual notification generation process"""
    
    print("🔍 TESTING NOTIFICATION GENERATION")
    print("=" * 50)
    
    engine = SmartNotificationEngine('customer_data.db')
    
    # Generate notifications
    print("🤖 Generating notifications...")
    notifications = engine.generate_unified_notifications()
    
    print(f"\n✅ Generated {len(notifications)} notifications:")
    
    for i, notification in enumerate(notifications):
        print(f"\n📧 Notification {i+1}:")
        print(f"  Customer ID: {notification.get('customer_id')}")
        print(f"  Customer Name: {notification.get('customer_name')}")
        print(f"  Opted In: {notification.get('opted_in')}")
        print(f"  Priority: {notification.get('priority')}")
        print(f"  Churn Risk: {notification.get('churn_risk')}%")
        print(f"  Channel: {notification.get('preferred_channel')}")
        print(f"  Message: {notification.get('message')[:100]}...")

if __name__ == "__main__":
    test_notification_generation()