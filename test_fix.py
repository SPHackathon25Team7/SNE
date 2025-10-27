#!/usr/bin/env python3
"""
Test the customer name fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import SmartNotificationEngine

def test_customer_names():
    """Test that customer names are correctly retrieved"""
    
    print("🔍 TESTING CUSTOMER NAME FIX")
    print("=" * 50)
    
    engine = SmartNotificationEngine('customer_data.db')
    
    # Test specific customers we know should exist
    test_customers = [3000, 3003, 3010]
    
    for customer_id in test_customers:
        print(f"\n👤 Testing Customer {customer_id}:")
        
        # Get complete profile
        profile = engine.get_customer_complete_profile(customer_id)
        
        basic = profile.get('basic', {})
        name = basic.get('Name', 'NOT_FOUND')
        opted_in = basic.get('Opted_In', 'NOT_FOUND')
        
        print(f"  Name: {name}")
        print(f"  Opted_In: {opted_in}")
        
        if name == 'NOT_FOUND':
            print(f"  ❌ FAILED - No name found")
        else:
            print(f"  ✅ SUCCESS - Name retrieved")

if __name__ == "__main__":
    test_customer_names()