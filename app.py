from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import os
from datetime import datetime
import json
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

class BedrockNotificationGenerator:
    def __init__(self):
        """Initialize Bedrock client"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'  # Change to your preferred region
            )
            self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Using Claude 3 Sonnet
        except Exception as e:
            print(f"Warning: Could not initialize Bedrock client: {e}")
            self.bedrock_client = None
    
    def analyse_customer_priority(self, customer_data, context_data=None):
        """Use AI to determine customer contact priority and strategy"""
        if not self.bedrock_client:
            return self._fallback_priority_analysis(customer_data)
        
        try:
            prompt = self._build_priority_prompt(customer_data, context_data)
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
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
            
            return self._parse_priority_response(ai_response)
            
        except Exception as e:
            print(f"Priority analysis error: {e}")
            return self._fallback_priority_analysis(customer_data)
    
    def _build_priority_prompt(self, customer_data, context_data):
        """Build prompt for AI priority analysis"""
        segment = customer_data.get('Segment', 'Unknown')
        energy_usage = customer_data.get('Daily_Energy_Usage_kWh', 0)
        seasonal_usage = customer_data.get('Seasonal_Energy_Usage_kWh', 0)
        solar_ev = customer_data.get('Solar_EV_Ownership', 'None')
        billing_anomaly = customer_data.get('Billing_Anomaly', 'None')
        campaign_clicks = customer_data.get('Campaign_Clicks', 0)
        campaign_opens = customer_data.get('Campaign_Opens', 0)
        support_issue = customer_data.get('Support_Ticket_Issue', 'None')
        region = customer_data.get('Region', 'Unknown')
        
        prompt = f"""
You are an AI customer engagement strategist for a British energy supplier. Analyse this customer profile and determine the optimal contact strategy.

CRITICAL RULES:
- Use British English spelling and terminology throughout
- NEVER invent or mention specific names of customers, staff, or departments
- NEVER make up specific dates, times, reference numbers, or contact details
- Base recommendations only on the actual customer data provided
- Use general terms like "our team", "customer services", "billing department"

Customer Profile:
- Segment: {segment}
- Daily Energy Usage: {energy_usage} kWh
- Seasonal Energy Usage: {seasonal_usage} kWh
- Solar/EV Ownership: {solar_ev}
- Billing Anomaly: {billing_anomaly}
- Campaign Engagement: {campaign_clicks} clicks, {campaign_opens} opens
- Recent Support Issue: {support_issue}
- Region: {region}

Context: {context_data or 'General customer analysis'}

Analyse this customer and provide your recommendation in this EXACT format:

PRIORITY: [HIGH/MEDIUM/LOW]
URGENCY: [IMMEDIATE/WITHIN_24H/WITHIN_WEEK/ROUTINE]
CHANNEL: [email_sms/email/sms/app_notification/phone_call]
REASON: [Brief explanation of why this priority/urgency]
CONTACT_STRATEGY: [Specific approach recommendation]
RISK_SCORE: [1-10 scale where 10 is highest risk of churn/dissatisfaction]

Consider factors like:
- Billing issues require immediate attention
- High energy users may need efficiency advice
- Low engagement customers need re-engagement
- Value Seekers respond to cost-saving opportunities
- Support issues indicate potential dissatisfaction

IMPORTANT: Use British English in your analysis (e.g., "recognised", "organised", "prioritise", "realise")
"""
        
        return prompt
    
    def _parse_priority_response(self, ai_response):
        """Parse AI response into structured data"""
        try:
            lines = ai_response.strip().split('\n')
            result = {
                'priority': 'medium',
                'urgency': 'routine',
                'channel': 'email',
                'reason': 'AI analysis completed',
                'contact_strategy': 'Standard engagement approach',
                'risk_score': 5
            }
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'priority' in key:
                        result['priority'] = value.lower()
                    elif 'urgency' in key:
                        result['urgency'] = value.lower()
                    elif 'channel' in key:
                        result['channel'] = value.lower()
                    elif 'reason' in key:
                        result['reason'] = value
                    elif 'contact_strategy' in key:
                        result['contact_strategy'] = value
                    elif 'risk_score' in key:
                        try:
                            result['risk_score'] = int(value.split()[0])
                        except:
                            result['risk_score'] = 5
            
            return result
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._fallback_priority_analysis({})
    
    def _fallback_priority_analysis(self, customer_data):
        """Fallback priority analysis when AI is unavailable"""
        billing_anomaly = customer_data.get('Billing_Anomaly', 'None')
        energy_usage = customer_data.get('Daily_Energy_Usage_kWh', 0)
        campaign_clicks = customer_data.get('Campaign_Clicks', 0)
        
        if billing_anomaly != 'None':
            return {
                'priority': 'high',
                'urgency': 'immediate',
                'channel': 'email_sms',
                'reason': f'Billing issue: {billing_anomaly}',
                'contact_strategy': 'Address billing concern immediately',
                'risk_score': 8
            }
        elif energy_usage > 30:
            return {
                'priority': 'medium',
                'urgency': 'within_week',
                'channel': 'email',
                'reason': 'High energy usage detected',
                'contact_strategy': 'Provide energy efficiency recommendations',
                'risk_score': 4
            }
        elif campaign_clicks < 2:
            return {
                'priority': 'low',
                'urgency': 'routine',
                'channel': 'app_notification',
                'reason': 'Low engagement detected',
                'contact_strategy': 'Re-engagement campaign',
                'risk_score': 6
            }
        else:
            return {
                'priority': 'low',
                'urgency': 'routine',
                'channel': 'email',
                'reason': 'Standard customer profile',
                'contact_strategy': 'Regular communication',
                'risk_score': 3
            }
    
    def generate_notification(self, customer_data, notification_type, context=None):
        """Generate personalized notification using Bedrock"""
        if not self.bedrock_client:
            return self._fallback_notification(customer_data, notification_type)
        
        try:
            prompt = self._build_prompt(customer_data, notification_type, context)
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
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
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"Bedrock error: {e}")
            return self._fallback_notification(customer_data, notification_type)
    
    def _build_prompt(self, customer_data, notification_type, context):
        """Build prompt for Bedrock based on customer data and notification type"""
        segment = customer_data.get('Segment', 'Unknown')
        energy_usage = customer_data.get('Daily_Energy_Usage_kWh', 0)
        solar_ev = customer_data.get('Solar_EV_Ownership', 'None')
        region = customer_data.get('Region', 'Unknown')
        
        base_prompt = f"""
You are a smart notification system for a British energy supplier. Create a personalised, engaging notification message.

CRITICAL RULES:
- Use British English spelling and terminology throughout
- NEVER invent or mention specific names of customers, staff members, or people
- NEVER make up specific dates, times, or reference numbers
- NEVER create fictional contact details or department names
- Only use the actual data provided about this customer
- Keep messages professional but friendly
- Use "we" to refer to the energy supplier

Customer Profile:
- Segment: {segment}
- Daily Energy Usage: {energy_usage} kWh
- Solar/EV Ownership: {solar_ev}
- Region: {region}
- Notification Type: {notification_type}
"""
        
        if notification_type == "billing_alert":
            prompt = base_prompt + f"""
Context: {context or 'Billing anomaly detected'}

Create a professional, reassuring message about a billing issue. Requirements:
- Empathetic and understanding tone
- Clear about next steps without being specific about dates/times
- Appropriate for {segment} customers
- Use British English (e.g., "recognised", "organised", "centre")
- Do NOT mention specific staff names, departments, or reference numbers
- Use generic terms like "our team", "customer services", "billing department"
- Under 150 characters for SMS/email subject
- End with a general instruction like "Please contact us" rather than specific numbers
"""
        
        elif notification_type == "energy_saving":
            prompt = base_prompt + f"""
Context: High energy usage detected ({energy_usage} kWh/day)

Create an engaging energy-saving tip message that:
- Acknowledges their {segment} mindset
- Provides actionable, general advice (no specific product names or brands)
- Mentions their {solar_ev} setup if relevant
- Is encouraging, not judgmental
- Uses British English terminology
- Do NOT mention specific programmes, schemes, or staff names
- Use general terms like "energy-saving tips", "efficiency measures"
- Under 200 characters
"""
        
        elif notification_type == "engagement":
            prompt = base_prompt + f"""
Context: Low campaign engagement detected

Create a re-engagement message that:
- Appeals to {segment} values
- Offers relevant but general benefits (no specific offer amounts or dates)
- Feels personal but doesn't use made-up names
- Encourages action with general terms
- Uses British English
- Do NOT mention specific offers, percentages, or time-limited deals
- Use phrases like "exclusive updates", "tailored information", "relevant offers"
- Under 160 characters
"""
        
        elif notification_type == "value_seeker_special":
            prompt = base_prompt + f"""
Context: Special offer for Value Seekers segment

Create a compelling offer message that:
- Emphasises cost savings and value in general terms
- Mentions energy efficiency benefits
- Includes gentle urgency without specific dates or deadlines
- Appeals to practical mindset
- Uses British English
- Do NOT mention specific discount percentages, prices, or end dates
- Use general terms like "potential savings", "efficiency opportunities", "value-focused options"
- Under 180 characters
"""
        
        elif notification_type == "value_seeker_energy_savings":
            prompt = base_prompt + f"""
Context: Value Seeker with high energy usage ({energy_usage} kWh/day) - cost-saving opportunity

Create a compelling energy-saving message that:
- Emphasises potential cost savings from reducing usage (in general terms)
- Provides actionable tips without mentioning specific products or brands
- Mentions their current usage level ({energy_usage} kWh/day)
- Appeals to their value-conscious mindset
- Uses British English
- Do NOT mention specific savings amounts, percentages, or monetary figures
- Use terms like "potential savings", "reduced bills", "efficiency improvements"
- Under 180 characters
"""
        
        prompt += """

FINAL REQUIREMENTS:
- Generate ONLY the notification message, no explanations or additional text
- Use British English spelling throughout (e.g., realise, organised, centre, colour)
- Do NOT include any made-up names, specific dates, reference numbers, or contact details
- Keep the message professional, helpful, and appropriate for a British energy supplier
"""
        
        prompt += "\n\nGenerate ONLY the notification message, no explanations or additional text."
        return prompt
    
    def _fallback_notification(self, customer_data, notification_type):
        """Fallback notifications when Bedrock is unavailable"""
        segment = customer_data.get('Segment', 'Unknown')
        
        fallback_messages = {
            "billing_alert": f"We've recognised a billing issue on your account. Our team is reviewing it and will contact you shortly.",
            "energy_saving": f"Your energy usage is higher than average. Check out our energy-saving tips in your account dashboard.",
            "engagement": f"Don't miss out on exclusive offers and updates tailored for {segment} customers like you!",
            "value_seeker_special": f"Discover potential savings on your energy bills with our efficiency programme!",
            "value_seeker_energy_savings": f"Your current usage of {customer_data.get('Daily_Energy_Usage_kWh', 0)} kWh/day could be reduced. Explore our energy-saving tips for potential bill reductions."
        }
        
        return fallback_messages.get(notification_type, "Important update about your energy account.")

class SmartNotificationEngine:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        # Remove any completely empty columns that might be created by trailing commas
        self.df = self.df.dropna(axis=1, how='all')
        # Clean the data on initialization
        self.df = self.df.fillna({
            'Daily_Energy_Usage_kWh': 0,
            'Seasonal_Energy_Usage_kWh': 0,
            'Campaign_Clicks': 0,
            'Campaign_Opens': 0,
            'Campaign_Conversions': 0,
            'Solar_EV_Ownership': 'None',
            'Billing_Anomaly': 'None',
            'Support_Ticket_Issue': 'None'
        })
        
    def load_data(self):
        """Reload data from CSV"""
        self.df = pd.read_csv(self.csv_path)
        # Remove any completely empty columns that might be created by trailing commas
        self.df = self.df.dropna(axis=1, how='all')
        # Clean the data - replace NaN values with appropriate defaults
        self.df = self.df.fillna({
            'Daily_Energy_Usage_kWh': 0,
            'Seasonal_Energy_Usage_kWh': 0,
            'Campaign_Clicks': 0,
            'Campaign_Opens': 0,
            'Campaign_Conversions': 0,
            'Solar_EV_Ownership': 'None',
            'Billing_Anomaly': 'None',
            'Support_Ticket_Issue': 'None'
        })
        
    def get_customer_segments(self):
        """Get unique customer segments"""
        return self.df['Segment'].unique().tolist()
    
    def get_billing_anomalies(self):
        """Get Value Seekers customers with billing anomalies only"""
        value_seekers = self.df[self.df['Segment'] == 'Value Seekers']
        return value_seekers[value_seekers['Billing_Anomaly'] != 'None']
    
    def get_high_energy_users(self, threshold=25):
        """Get Value Seekers customers with high daily energy usage only"""
        value_seekers = self.df[self.df['Segment'] == 'Value Seekers']
        return value_seekers[value_seekers['Daily_Energy_Usage_kWh'] > threshold]
    
    def get_low_engagement_customers(self, click_threshold=3, open_threshold=10):
        """Get Value Seekers customers with low campaign engagement only"""
        value_seekers = self.df[self.df['Segment'] == 'Value Seekers']
        return value_seekers[
            (value_seekers['Campaign_Clicks'] <= click_threshold) & 
            (value_seekers['Campaign_Opens'] <= open_threshold)
        ]
    
    def generate_unified_notifications(self):
        """Unified AI workflow: Analyze Value Seekers only → Prioritize → Generate targeted notifications"""
        notifications = []
        bedrock_generator = BedrockNotificationGenerator()
        
        print("🤖 Starting unified AI notification workflow...")
        
        # Step 1: Filter to ONLY Value Seekers customers to save processing time
        value_seekers_only = self.df[self.df['Segment'] == 'Value Seekers'].copy()
        customer_analyses = []
        
        print(f"🎯 Focusing on Value Seekers segment only")
        print(f"📊 Analysing {len(value_seekers_only)} Value Seekers customers for contact priority...")
        
        for _, customer in value_seekers_only.iterrows():
            customer_data = customer.to_dict()
            
            # Determine context based on customer situation
            context = self._determine_customer_context(customer_data)
            
            # Get AI analysis for this customer
            analysis = bedrock_generator.analyse_customer_priority(customer_data, context)
            analysis['customer_data'] = customer_data
            customer_analyses.append(analysis)
        
        # Step 2: Sort by AI-determined priority and risk
        customer_analyses.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 1),
            x['risk_score']
        ), reverse=True)
        
        print(f"🎯 AI identified {len([a for a in customer_analyses if a['priority'] in ['high', 'medium']])} high/medium priority customers")
        
        # Step 3: Generate notifications ONLY for customers who need contact
        for analysis in customer_analyses:
            customer_data = analysis['customer_data']
            
            # AI-driven filtering: Only contact customers who truly need it
            should_contact = self._should_contact_customer(analysis)
            
            if not should_contact:
                continue
            
            # Step 4: Determine the BEST notification type for this specific customer
            notification_type = self._determine_optimal_notification_type(customer_data, analysis)
            
            # Step 5: Generate the PERFECT message for this customer's situation
            message = bedrock_generator.generate_notification(
                customer_data, 
                notification_type, 
                f"{analysis['reason']} | Strategy: {analysis['contact_strategy']}"
            )
            
            notifications.append({
                'customer_id': customer_data['Customer_ID'],
                'segment': customer_data['Segment'],
                'type': notification_type,
                'priority': analysis['priority'],
                'urgency': analysis['urgency'],
                'message': message,
                'channel': analysis['channel'],
                'reason': analysis['reason'],
                'contact_strategy': analysis['contact_strategy'],
                'risk_score': analysis['risk_score'],
                'ai_generated': True,
                'ai_prioritized': True,
                'should_contact_reason': self._get_contact_reason(analysis)
            })
        
        print(f"✅ Generated {len(notifications)} targeted notifications")
        return notifications
    
    def _should_contact_customer(self, analysis):
        """AI-driven decision on whether to contact this customer"""
        customer_data = analysis['customer_data']
        
        # Always contact high priority customers
        if analysis['priority'] == 'high':
            return True
        
        # Contact medium priority if risk score is significant
        if analysis['priority'] == 'medium' and analysis['risk_score'] >= 5:
            return True
        
        # Contact low priority only if they have specific actionable issues
        if analysis['priority'] == 'low':
            billing_issue = customer_data.get('Billing_Anomaly', 'None') != 'None'
            high_energy = customer_data.get('Daily_Energy_Usage_kWh', 0) > 30
            very_low_engagement = customer_data.get('Campaign_Clicks', 0) == 0
            is_value_seeker = customer_data.get('Segment') == 'Value Seekers'
            
            # Contact if they have actionable issues or are in target segment
            return billing_issue or (high_energy and is_value_seeker) or (very_low_engagement and analysis['risk_score'] >= 6)
        
        return False
    
    def _determine_optimal_notification_type(self, customer_data, analysis):
        """Determine the BEST notification type based on AI analysis and customer data"""
        billing_anomaly = customer_data.get('Billing_Anomaly', 'None')
        segment = customer_data.get('Segment', 'Unknown')
        energy_usage = customer_data.get('Daily_Energy_Usage_kWh', 0)
        campaign_engagement = customer_data.get('Campaign_Clicks', 0)
        
        # Priority 1: Billing issues (immediate action needed)
        if billing_anomaly != 'None':
            return 'billing_alert'
        
        # Priority 2: Value Seekers with high energy usage (cost-saving opportunity)
        if segment == 'Value Seekers' and energy_usage > 25:
            return 'value_seeker_energy_savings'
        
        # Priority 3: High energy usage (efficiency opportunity)
        if energy_usage > 30:
            return 'energy_saving'
        
        # Priority 4: Low engagement (re-engagement needed)
        if campaign_engagement < 3:
            return 'engagement'
        
        # Priority 5: Value Seekers (special offers)
        if segment == 'Value Seekers':
            return 'value_seeker_special'
        
        # Default: General engagement
        return 'engagement'
    
    def _get_contact_reason(self, analysis):
        """Get human-readable reason for contacting this customer"""
        priority = analysis['priority']
        risk_score = analysis['risk_score']
        reason = analysis['reason']
        
        if priority == 'high':
            return f"High priority: {reason}"
        elif priority == 'medium' and risk_score >= 5:
            return f"Medium priority with risk score {risk_score}: {reason}"
        else:
            return f"Actionable opportunity: {reason}"
    
    def _determine_customer_context(self, customer_data):
        """Determine context for AI analysis based on customer situation"""
        contexts = []
        
        billing_anomaly = customer_data.get('Billing_Anomaly', 'None')
        if billing_anomaly != 'None':
            contexts.append(f"Billing issue: {billing_anomaly}")
        
        energy_usage = customer_data.get('Daily_Energy_Usage_kWh', 0)
        if energy_usage > 30:
            contexts.append("High energy consumption")
        elif energy_usage < 12:
            contexts.append("Low energy consumption")
        
        campaign_clicks = customer_data.get('Campaign_Clicks', 0)
        campaign_opens = customer_data.get('Campaign_Opens', 0)
        if campaign_clicks < 3 and campaign_opens < 10:
            contexts.append("Low engagement with campaigns")
        
        support_issue = customer_data.get('Support_Ticket_Issue', 'None')
        if support_issue != 'None':
            contexts.append(f"Recent support issue: {support_issue}")
        
        solar_ev = customer_data.get('Solar_EV_Ownership', 'None')
        if solar_ev != 'None':
            contexts.append(f"Green technology owner: {solar_ev}")
        
        segment = customer_data.get('Segment', 'Unknown')
        if segment == 'Value Seekers':
            contexts.append("Target segment: Value Seekers - focus on cost savings")
        
        return "; ".join(contexts) if contexts else "Standard customer analysis"
    
    def _determine_notification_type(self, customer_data, analysis):
        """Determine the best notification type based on customer data and AI analysis"""
        billing_anomaly = customer_data.get('Billing_Anomaly', 'None')
        
        if billing_anomaly != 'None':
            return 'billing_alert'
        elif customer_data.get('Daily_Energy_Usage_kWh', 0) > 25:
            return 'energy_saving'
        elif customer_data.get('Campaign_Clicks', 0) < 3:
            return 'engagement'
        elif customer_data.get('Segment') == 'Value Seekers':
            return 'value_seeker_special'
        else:
            return 'engagement'

# Initialize the notification engine
csv_file_path = r"Extra Data Challenge 4#.csv"
notification_engine = SmartNotificationEngine(csv_file_path)

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/customers')
def get_customers():
    """Get Value Seekers customers data only"""
    # Filter to only Value Seekers and convert to dict
    value_seekers = notification_engine.df[notification_engine.df['Segment'] == 'Value Seekers']
    customers = value_seekers.replace({np.nan: None}).to_dict('records')
    return jsonify(customers)

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """Reload data from CSV file"""
    try:
        notification_engine.load_data()
        return jsonify({
            'status': 'success',
            'message': 'Data refreshed successfully',
            'total_customers': len(notification_engine.df),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error refreshing data: {str(e)}'
        }), 500

@app.route('/api/segments')
def get_segments():
    """Get Value Seekers segment summary only"""
    # Only return Value Seekers data
    value_seekers = notification_engine.df[notification_engine.df['Segment'] == 'Value Seekers']
    
    if len(value_seekers) > 0:
        segments = {
            'Value Seekers': {
                'Customer_ID': len(value_seekers),
                'Daily_Energy_Usage_kWh': round(value_seekers['Daily_Energy_Usage_kWh'].mean(), 2),
                'Campaign_Clicks': round(value_seekers['Campaign_Clicks'].mean(), 2),
                'Campaign_Opens': round(value_seekers['Campaign_Opens'].mean(), 2)
            }
        }
    else:
        segments = {'Value Seekers': {'Customer_ID': 0, 'Daily_Energy_Usage_kWh': 0, 'Campaign_Clicks': 0, 'Campaign_Opens': 0}}
    
    return jsonify(segments)

@app.route('/api/notifications')
def get_notifications():
    """Generate unified AI-driven notifications"""
    notifications = notification_engine.generate_unified_notifications()
    return jsonify(notifications)

@app.route('/api/billing-issues')
def get_billing_issues():
    """Get customers with billing anomalies"""
    billing_issues = notification_engine.get_billing_anomalies()
    # Replace NaN values and convert to dict
    billing_data = billing_issues.replace({np.nan: None}).to_dict('records')
    return jsonify(billing_data)

@app.route('/api/value-seekers')
def get_value_seekers():
    """Get detailed Value Seekers analysis"""
    value_seekers = notification_engine.df[notification_engine.df['Segment'] == 'Value Seekers']
    
    # Handle potential NaN values in calculations
    avg_daily = value_seekers['Daily_Energy_Usage_kWh'].mean()
    avg_seasonal = value_seekers['Seasonal_Energy_Usage_kWh'].mean()
    avg_clicks = value_seekers['Campaign_Clicks'].mean()
    avg_opens = value_seekers['Campaign_Opens'].mean()
    
    analysis = {
        'total_count': len(value_seekers),
        'avg_daily_energy': round(avg_daily if not pd.isna(avg_daily) else 0, 2),
        'avg_seasonal_energy': round(avg_seasonal if not pd.isna(avg_seasonal) else 0, 2),
        'solar_ev_breakdown': value_seekers['Solar_EV_Ownership'].value_counts().to_dict(),
        'billing_issues': value_seekers['Billing_Anomaly'].value_counts().to_dict(),
        'avg_campaign_clicks': round(avg_clicks if not pd.isna(avg_clicks) else 0, 2),
        'avg_campaign_opens': round(avg_opens if not pd.isna(avg_opens) else 0, 2),
        'regions': value_seekers['Region'].value_counts().to_dict(),
        'support_issues': value_seekers['Support_Ticket_Issue'].value_counts().to_dict()
    }
    
    return jsonify(analysis)

@app.route('/api/customer-analysis')
def get_customer_analysis():
    """Get AI-powered customer analysis and prioritisation for Value Seekers only"""
    try:
        bedrock_generator = BedrockNotificationGenerator()
        analyses = []
        
        # Analyze only Value Seekers customers
        value_seekers_customers = notification_engine.df[notification_engine.df['Segment'] == 'Value Seekers']
        print(f"🎯 Analysing {len(value_seekers_customers)} Value Seekers customers only")
        
        for _, customer in value_seekers_customers.iterrows():
            customer_data = customer.to_dict()
            context = notification_engine._determine_customer_context(customer_data)
            analysis = bedrock_generator.analyse_customer_priority(customer_data, context)
            
            analyses.append({
                'customer_id': customer_data['Customer_ID'],
                'segment': customer_data['Segment'],
                'priority': analysis['priority'],
                'urgency': analysis['urgency'],
                'risk_score': analysis['risk_score'],
                'reason': analysis['reason'],
                'contact_strategy': analysis['contact_strategy'],
                'recommended_channel': analysis['channel']
            })
        
        # Sort by priority and risk score
        analyses.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 1),
            x['risk_score']
        ), reverse=True)
        
        return jsonify(analyses)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-notification', methods=['POST'])
def send_notification():
    """Simulate sending a notification"""
    data = request.json
    customer_id = data.get('customer_id')
    message = data.get('message')
    channel = data.get('channel', 'email')
    
    # In a real implementation, this would integrate with email/SMS services
    response = {
        'status': 'sent',
        'customer_id': customer_id,
        'channel': channel,
        'timestamp': datetime.now().isoformat(),
        'message': f"Notification sent to customer {customer_id} via {channel}"
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)