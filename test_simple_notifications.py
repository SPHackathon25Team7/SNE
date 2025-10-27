#!/usr/bin/env python3
"""
Simple test for the new notification system
"""
from app import SmartNotificationEngine

def test_simple():
    """Test the simplified notification system"""
    
    print("🔍 TESTING SIMPLIFIED NOTIFICATION SYSTEM")
    print("=" * 50)
    
    try:
        # Initialize the engine
        engine = SmartNotificationEngine('customer_data.db')
        
        # Test the new method to get opted-in customers
        print("📊 Testing customer retrieval...")
        customers = engine._get_opted_in_value_seekers()
        
        print(f"✅ Found {len(customers)} customers")
        for customer in customers[:3]:  # Show first 3
            print(f"  - {customer['Name']} (ID: {customer['Customer_ID']}) - Churn Risk: {customer.get('Churn_Risk_Score', 0)}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()