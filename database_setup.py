"""
Database setup script to create SQLite database from CSV files
and classify customers into segments using AI analysis
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime
import json
import boto3
from botocore.exceptions import ClientError

class DatabaseManager:
    def __init__(self, db_path='customer_data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def create_tables_from_csvs(self):
        """Create database tables from CSV files in user_data folder"""
        csv_files = {
            'customer_profiles': 'user_data/Customer Profiles.csv',
            'account_activity': 'user_data/Account Activity Logs.csv',
            'interaction_history': 'user_data/Interaction History.csv',
            'notification_history': 'user_data/Notification History.csv',
            'recommended_actions': 'user_data/Recommended Actions.csv'
        }
        
        print("🗄️ Creating database tables from CSV files...")
        
        for table_name, csv_path in csv_files.items():
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                print(f"✅ Created table '{table_name}' with {len(df)} records")
            else:
                print(f"❌ CSV file not found: {csv_path}")
        
        # Create indexes for better performance
        self.create_indexes()
        
    def create_indexes(self):
        """Create indexes on foreign key columns"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_account_customer_id ON account_activity(Customer_ID)",
            "CREATE INDEX IF NOT EXISTS idx_interaction_customer_id ON interaction_history(Customer_ID)",
            "CREATE INDEX IF NOT EXISTS idx_notification_customer_id ON notification_history(Customer_ID)",
            "CREATE INDEX IF NOT EXISTS idx_actions_customer_id ON recommended_actions(Customer_ID)"
        ]
        
        for index_sql in indexes:
            self.conn.execute(index_sql)
        
        self.conn.commit()
        print("✅ Created database indexes")
    
    def get_customer_complete_profile(self, customer_id):
        """Get complete customer profile from all tables"""
        profile = {}
        
        # Customer basic info
        cursor = self.conn.execute(
            "SELECT * FROM customer_profiles WHERE Customer_ID = ?", 
            (customer_id,)
        )
        customer_data = cursor.fetchone()
        if customer_data:
            columns = [desc[0] for desc in cursor.description]
            profile['basic'] = dict(zip(columns, customer_data))
        
        # Account activity
        cursor = self.conn.execute(
            "SELECT * FROM account_activity WHERE Customer_ID = ?", 
            (customer_id,)
        )
        activity_data = cursor.fetchone()
        if activity_data:
            columns = [desc[0] for desc in cursor.description]
            profile['activity'] = dict(zip(columns, activity_data))
        
        # Recent interactions (last 5)
        cursor = self.conn.execute(
            """SELECT * FROM interaction_history 
               WHERE Customer_ID = ? 
               ORDER BY datetime([Date & Time]) DESC 
               LIMIT 5""", 
            (customer_id,)
        )
        interactions = cursor.fetchall()
        if interactions:
            columns = [desc[0] for desc in cursor.description]
            profile['interactions'] = [dict(zip(columns, row)) for row in interactions]
        
        # Notification history (last 10)
        cursor = self.conn.execute(
            """SELECT * FROM notification_history 
               WHERE Customer_ID = ? 
               ORDER BY datetime(Sent_Date) DESC 
               LIMIT 10""", 
            (customer_id,)
        )
        notifications = cursor.fetchall()
        if notifications:
            columns = [desc[0] for desc in cursor.description]
            profile['notifications'] = [dict(zip(columns, row)) for row in notifications]
        
        # Recommended actions
        cursor = self.conn.execute(
            "SELECT * FROM recommended_actions WHERE Customer_ID = ?", 
            (customer_id,)
        )
        actions = cursor.fetchall()
        if actions:
            columns = [desc[0] for desc in cursor.description]
            profile['actions'] = [dict(zip(columns, row)) for row in actions]
        
        return profile
    
    def get_all_customer_ids(self):
        """Get all customer IDs from the database"""
        cursor = self.conn.execute("SELECT Customer_ID FROM customer_profiles")
        return [row[0] for row in cursor.fetchall()]
    
    def add_segment_column(self):
        """Add customer_segment column to customer_profiles table"""
        try:
            self.conn.execute("ALTER TABLE customer_profiles ADD COLUMN customer_segment TEXT")
            self.conn.commit()
            print("✅ Added customer_segment column")
        except sqlite3.OperationalError:
            print("ℹ️ customer_segment column already exists")
    
    def update_customer_segment(self, customer_id, segment):
        """Update customer segment classification"""
        self.conn.execute(
            "UPDATE customer_profiles SET customer_segment = ? WHERE Customer_ID = ?",
            (segment, customer_id)
        )
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()

class CustomerSegmentClassifier:
    def __init__(self):
        """Initialize Bedrock client for AI classification"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            print("✅ Bedrock client initialized")
        except Exception as e:
            print(f"⚠️ Bedrock client not available: {e}")
            self.bedrock_client = None
    
    def classify_customer_segment(self, customer_profile):
        """Use AI to classify customer into one of four segments"""
        if not self.bedrock_client:
            return self._fallback_classification(customer_profile)
        
        try:
            prompt = self._build_classification_prompt(customer_profile)
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text'].strip()
            
            # Extract segment from AI response
            segment = self._parse_segment_response(ai_response)
            return segment
            
        except Exception as e:
            print(f"AI classification error: {e}")
            return self._fallback_classification(customer_profile)
    
    def _build_classification_prompt(self, profile):
        """Build prompt for AI customer segment classification"""
        basic = profile.get('basic', {})
        activity = profile.get('activity', {})
        interactions = profile.get('interactions', [])
        notifications = profile.get('notifications', [])
        actions = profile.get('actions', [])
        
        prompt = f"""
You are a customer segmentation expert for ScottishPower. Classify this customer into ONE of these four segments:

1. VALUE SEEKERS - Price-conscious, look for deals, basic service needs, cost-focused decisions
2. TRADITIONALISTS - Prefer traditional channels, loyal, conservative, phone/letter communication
3. DIGITAL NATIVES - Tech-savvy, use apps, online services, quick digital interactions
4. ECO SAVERS - Environmentally conscious, green tariffs, sustainability-focused, energy efficiency

Customer Data:
BASIC INFO:
- Age: {basic.get('Age', 'Unknown')}
- Location: {basic.get('Location', 'Unknown')}
- Preferred Channel: {basic.get('Preferred_Channel', 'Unknown')}
- Income Bracket: {basic.get('Income_Bracket', 'Unknown')}
- Customer Since: {basic.get('Customer_Since', 'Unknown')}
- Satisfaction Score: {basic.get('Satisfaction_Score', 'Unknown')}/10

ACCOUNT ACTIVITY:
- Account Status: {activity.get('Account_Status', 'Unknown')}
- Subscription Type: {activity.get('Subscription_Type', 'Unknown')}
- Recent Activity: {activity.get('Recent_Activity', 'Unknown')}
- Engagement Score: {activity.get('Engagement_Score', 'Unknown')}
- Churn Risk: {activity.get('Churn_Risk_Score', 'Unknown')}

INTERACTION PATTERNS:
"""
        
        if interactions:
            for interaction in interactions[:3]:  # Last 3 interactions
                prompt += f"- {interaction.get('Channel', 'Unknown')} {interaction.get('Interaction_Type', 'Unknown')}: {interaction.get('Summary', 'Unknown')}\n"
        
        prompt += f"\nNOTIFICATION BEHAVIOUR:\n"
        if notifications:
            opened_count = sum(1 for n in notifications if n.get('Opened') == 'Yes')
            clicked_count = sum(1 for n in notifications if n.get('Clicked') == 'Yes')
            prompt += f"- Opens notifications: {opened_count}/{len(notifications)}\n"
            prompt += f"- Clicks notifications: {clicked_count}/{len(notifications)}\n"
        
        prompt += f"""
RECOMMENDED ACTIONS:
"""
        if actions:
            for action in actions:
                prompt += f"- {action.get('Scenario', 'Unknown')}: {action.get('Recommended_Action', 'Unknown')}\n"
        
        prompt += """

Based on this data, classify as ONE segment only. Consider:
- VALUE SEEKERS: Low income, basic subscription, price-sensitive behaviour
- TRADITIONALISTS: Older age, phone/email preference, conservative patterns
- DIGITAL NATIVES: App usage, high engagement, tech-savvy behaviour  
- ECO SAVERS: Green subscription, environmental concerns, efficiency focus

Respond with ONLY the segment name: VALUE SEEKERS, TRADITIONALISTS, DIGITAL NATIVES, or ECO SAVERS
"""
        
        return prompt
    
    def _parse_segment_response(self, ai_response):
        """Parse AI response to extract segment"""
        response_upper = ai_response.upper()
        
        if "VALUE SEEKERS" in response_upper:
            return "Value Seekers"
        elif "TRADITIONALISTS" in response_upper:
            return "Traditionalists"
        elif "DIGITAL NATIVES" in response_upper:
            return "Digital Natives"
        elif "ECO SAVERS" in response_upper:
            return "Eco Savers"
        else:
            # Fallback based on keywords
            if any(word in response_upper for word in ["PRICE", "COST", "DEAL", "CHEAP"]):
                return "Value Seekers"
            elif any(word in response_upper for word in ["TRADITIONAL", "PHONE", "CONSERVATIVE"]):
                return "Traditionalists"
            elif any(word in response_upper for word in ["DIGITAL", "APP", "TECH", "ONLINE"]):
                return "Digital Natives"
            elif any(word in response_upper for word in ["GREEN", "ECO", "ENVIRONMENT"]):
                return "Eco Savers"
            else:
                return "Value Seekers"  # Default fallback
    
    def _fallback_classification(self, profile):
        """Fallback classification when AI is not available"""
        basic = profile.get('basic', {})
        activity = profile.get('activity', {})
        
        age = basic.get('Age', 50)
        income = basic.get('Income_Bracket', 'Medium')
        channel = basic.get('Preferred_Channel', 'Email')
        subscription = activity.get('Subscription_Type', 'Basic')
        
        # Simple rule-based classification
        if subscription == 'Green':
            return "Eco Savers"
        elif age >= 60 or channel == 'Phone':
            return "Traditionalists"
        elif channel == 'App Push' or subscription == 'Premium':
            return "Digital Natives"
        elif income == 'Low' or subscription == 'Basic':
            return "Value Seekers"
        else:
            return "Value Seekers"  # Default

def main():
    """Main function to set up database and classify customers"""
    print("🚀 Starting database setup and customer classification...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Create tables from CSV files
    db.create_tables_from_csvs()
    
    # Add segment column
    db.add_segment_column()
    
    # Initialize classifier
    classifier = CustomerSegmentClassifier()
    
    # Get all customers
    customer_ids = db.get_all_customer_ids()
    print(f"📊 Found {len(customer_ids)} customers to classify")
    
    # Classify each customer
    segment_counts = {"Value Seekers": 0, "Traditionalists": 0, "Digital Natives": 0, "Eco Savers": 0}
    
    for customer_id in customer_ids:
        print(f"🔍 Analysing Customer {customer_id}...")
        
        # Get complete profile
        profile = db.get_customer_complete_profile(customer_id)
        
        # Classify using AI
        segment = classifier.classify_customer_segment(profile)
        
        # Update database
        db.update_customer_segment(customer_id, segment)
        
        segment_counts[segment] += 1
        print(f"✅ Customer {customer_id} classified as: {segment}")
    
    print("\n📈 Classification Summary:")
    for segment, count in segment_counts.items():
        print(f"  {segment}: {count} customers")
    
    print(f"\n🎯 Value Seekers identified: {segment_counts['Value Seekers']} customers")
    
    # Close database
    db.close()
    print("✅ Database setup complete!")

if __name__ == "__main__":
    main()