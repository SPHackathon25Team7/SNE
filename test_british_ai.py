"""
Test script to verify AI responses use British English and don't make up data
"""
import boto3
import json
from app import BedrockNotificationGenerator

def test_british_english_notifications():
    """Test that AI generates British English notifications without made-up data"""
    
    # Sample customer data
    test_customer = {
        'Customer_ID': 2001,
        'Segment': 'Value Seekers',
        'Region': 'London',
        'Daily_Energy_Usage_kWh': 35.5,
        'Solar_EV_Ownership': 'Solar',
        'Billing_Anomaly': 'Overcharge'
    }
    
    generator = BedrockNotificationGenerator()
    
    print("🧪 Testing British English AI Notifications")
    print("=" * 50)
    
    # Test different notification types
    test_cases = [
        ('billing_alert', 'Billing issue detected'),
        ('energy_saving', 'High energy usage'),
        ('value_seeker_special', 'Special offer opportunity'),
        ('engagement', 'Low engagement detected')
    ]
    
    for notification_type, context in test_cases:
        print(f"\n📧 Testing {notification_type}:")
        print(f"Context: {context}")
        
        try:
            message = generator.generate_notification(
                test_customer, 
                notification_type, 
                context
            )
            
            print(f"✅ Generated: {message}")
            
            # Check for British English indicators
            british_indicators = ['realise', 'organised', 'centre', 'colour', 'recognised', 'programme']
            american_indicators = ['realize', 'organized', 'center', 'color', 'recognized', 'program']
            
            has_british = any(word in message.lower() for word in british_indicators)
            has_american = any(word in message.lower() for word in american_indicators)
            
            if has_american:
                print("⚠️  WARNING: Contains American spelling")
            elif has_british:
                print("🇬🇧 GOOD: Uses British English")
            
            # Check for made-up data (common patterns)
            suspicious_patterns = [
                'john', 'sarah', 'mike', 'emma',  # Common names
                'ref:', 'reference:', '#',  # Reference numbers
                'call 0800', 'contact sarah',  # Specific contacts
                'monday', 'tuesday', 'january',  # Specific dates
                '£', '$', '%'  # Specific amounts (should be general)
            ]
            
            made_up_data = [pattern for pattern in suspicious_patterns if pattern in message.lower()]
            
            if made_up_data:
                print(f"❌ WARNING: Possible made-up data detected: {made_up_data}")
            else:
                print("✅ GOOD: No suspicious made-up data detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 This is expected if Bedrock isn't configured yet")
    
    print("\n" + "=" * 50)
    print("🔍 Test completed. Check warnings above.")
    print("💡 If you see 'Error' messages, configure AWS Bedrock first.")

if __name__ == "__main__":
    test_british_english_notifications()