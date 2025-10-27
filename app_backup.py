from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import os
import sqlite3
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
You are an AI customer engagement strategist for a British energy supplier. Analyse this customer profile and provide comprehensive insights for customer service agents.

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

Provide a comprehensive analysis in this EXACT format:

PRIORITY: [HIGH/MEDIUM/LOW]
URGENCY: [IMMEDIATE/WITHIN_24H/WITHIN_WEEK/ROUTINE]
CHANNEL: [email_sms/email/sms/app_notification/phone_call]
RISK_SCORE: [1-10 scale where 10 is highest risk of churn/dissatisfaction]

WHY_CONTACT: [Detailed explanation of the underlying issue or opportunity that requires attention]
TRIGGER_FACTORS: [Specific data points that led to this recommendation]
POTENTIAL_IMPACT: [What could happen if this issue isn't addressed]

RESOLUTION_STRATEGY_1: [Primary recommended approach with specific steps]
RESOLUTION_STRATEGY_2: [Alternative approach if primary fails]
RESOLUTION_STRATEGY_3: [Backup strategy or escalation path]

CUSTOMER_PERSONALITY: [Analysis of likely personality traits based on segment and behaviour]
COMMUNICATION_STYLE: [Recommended tone and approach - direct/empathetic/technical/etc]
CONVERSATION_STARTERS: [Suggested opening lines or key points to mention]
AVOID_TOPICS: [Potential sensitivities or topics to handle carefully]

SUCCESS_INDICATORS: [How to measure if the interaction was successful]
FOLLOW_UP_TIMING: [When and how to follow up after initial contact]

Consider factors like:
- Value Seekers are price-conscious and respond to cost savings
- Billing issues create immediate frustration and churn risk
- Low engagement may indicate dissatisfaction or confusion
- High energy usage presents efficiency opportunities
- Support issues suggest ongoing problems needing resolution

IMPORTANT: Use British English throughout (e.g., "recognised", "organised", "prioritise", "realise")
"""
        
        return prompt
    
    def _parse_priority_response(self, ai_response):
        """Parse AI response into structured data with comprehensive customer service insights"""
        try:
            lines = ai_response.strip().split('\n')
            result = {
                'priority': 'medium',
                'urgency': 'routine',
                'channel': 'email',
                'risk_score': 5,
                # Core analysis
                'why_contact': 'Standard customer analysis',
                'trigger_factors': 'Routine review',
                'potential_impact': 'Minimal impact if not addressed',
                # Resolution strategies
                'resolution_strategy_1': 'Standard engagement approach',
                'resolution_strategy_2': 'Follow up via preferred channel',
                'resolution_strategy_3': 'Escalate to supervisor if needed',
                # Communication guidance
                'customer_personality': 'Value-conscious, practical customer',
                'communication_style': 'Professional and helpful',
                'conversation_starters': 'Hello, we wanted to check how your service is going',
                'avoid_topics': 'Avoid pushy sales tactics',
                # Success metrics
                'success_indicators': 'Customer expresses satisfaction',
                'follow_up_timing': 'Follow up in 1-2 weeks if needed'
            }
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    # Core fields
                    if 'priority' in key:
                        result['priority'] = value.lower()
                    elif 'urgency' in key:
                        result['urgency'] = value.lower()
                    elif 'channel' in key:
                        result['channel'] = value.lower()
                    elif 'risk_score' in key:
                        try:
                            result['risk_score'] = int(value.split()[0])
                        except:
                            result['risk_score'] = 5
                    
                    # New insight fields
                    elif 'why_contact' in key:
                        result['why_contact'] = value
                    elif 'trigger_factors' in key:
                        result['trigger_factors'] = value
                    elif 'potential_impact' in key:
                        result['potential_impact'] = value
                    elif 'resolution_strategy_1' in key:
                        result['resolution_strategy_1'] = value
                    elif 'resolution_strategy_2' in key:
                        result['resolution_strategy_2'] = value
                    elif 'resolution_strategy_3' in key:
                        result['resolution_strategy_3'] = value
                    elif 'customer_personality' in key:
                        result['customer_personality'] = value
                    elif 'communication_style' in key:
                        result['communication_style'] = value
                    elif 'conversation_starters' in key:
                        result['conversation_starters'] = value
                    elif 'avoid_topics' in key:
                        result['avoid_topics'] = value
                    elif 'success_indicators' in key:
                        result['success_indicators'] = value
                    elif 'follow_up_timing' in key:
                        result['follow_up_timing'] = value
            
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
                'risk_score': 8,
                'why_contact': f'Customer has a billing anomaly: {billing_anomaly}. This creates immediate frustration and high churn risk.',
                'trigger_factors': f'Billing anomaly detected: {billing_anomaly}',
                'potential_impact': 'Customer may switch suppliers if billing issue not resolved quickly. High risk of negative reviews.',
                'resolution_strategy_1': 'Contact immediately to acknowledge issue and explain next steps for resolution',
                'resolution_strategy_2': 'Offer account credit or compensation if appropriate while investigating',
                'resolution_strategy_3': 'Escalate to billing specialist team for complex issues',
                'customer_personality': 'Likely frustrated and seeking quick resolution. Value Seekers are price-conscious.',
                'communication_style': 'Empathetic and solution-focused. Acknowledge frustration and provide clear timeline.',
                'conversation_starters': 'We\'ve noticed an issue with your recent bill and want to help resolve it immediately.',
                'avoid_topics': 'Avoid defensive language or complex technical explanations initially.',
                'success_indicators': 'Customer understands the issue and feels confident in resolution process.',
                'follow_up_timing': 'Follow up within 24-48 hours with resolution update.'
            }
        elif energy_usage > 30:
            return {
                'priority': 'medium',
                'urgency': 'within_week',
                'channel': 'email',
                'risk_score': 4,
                'why_contact': f'High energy usage ({energy_usage} kWh/day) presents opportunity to help customer reduce costs.',
                'trigger_factors': f'Daily energy usage above 30 kWh threshold at {energy_usage} kWh',
                'potential_impact': 'Customer may face high bills and seek alternative supplier if not helped with efficiency.',
                'resolution_strategy_1': 'Offer free energy efficiency assessment and practical tips',
                'resolution_strategy_2': 'Suggest smart meter installation or energy monitoring tools',
                'resolution_strategy_3': 'Recommend tariff review to ensure best rate for usage pattern',
                'customer_personality': 'Value Seekers appreciate cost-saving advice and practical solutions.',
                'communication_style': 'Helpful and advisory. Focus on potential savings and practical benefits.',
                'conversation_starters': 'We\'ve noticed your energy usage and have some tips that could help reduce your bills.',
                'avoid_topics': 'Avoid suggesting expensive upgrades or complex technology initially.',
                'success_indicators': 'Customer engages with efficiency advice and shows interest in savings.',
                'follow_up_timing': 'Follow up in 2-3 weeks to check on implementation of suggestions.'
            }
        elif campaign_clicks < 2:
            return {
                'priority': 'low',
                'urgency': 'routine',
                'channel': 'app_notification',
                'risk_score': 6,
                'why_contact': f'Low engagement ({campaign_clicks} clicks) suggests customer may be disengaged or dissatisfied.',
                'trigger_factors': f'Campaign engagement below threshold: {campaign_clicks} clicks',
                'potential_impact': 'Disengaged customers are more likely to churn when contracts end.',
                'resolution_strategy_1': 'Send personalised content relevant to their interests and needs',
                'resolution_strategy_2': 'Offer exclusive Value Seekers benefits or cost-saving opportunities',
                'resolution_strategy_3': 'Conduct satisfaction survey to identify any underlying issues',
                'customer_personality': 'May be busy, overwhelmed, or not finding current communications relevant.',
                'communication_style': 'Gentle and value-focused. Make communications clearly beneficial.',
                'conversation_starters': 'We want to make sure you\'re getting the most value from your energy service.',
                'avoid_topics': 'Avoid frequent communications or pushy sales messages.',
                'success_indicators': 'Increased engagement with future communications or positive survey feedback.',
                'follow_up_timing': 'Monitor engagement over next month, follow up if still low.'
            }
        else:
            return {
                'priority': 'low',
                'urgency': 'routine',
                'channel': 'email',
                'risk_score': 3,
                'why_contact': 'Standard Value Seekers customer with normal profile - routine engagement opportunity.',
                'trigger_factors': 'Regular customer review cycle',
                'potential_impact': 'Minimal risk, but opportunity to strengthen relationship and prevent future issues.',
                'resolution_strategy_1': 'Share relevant cost-saving tips or service updates',
                'resolution_strategy_2': 'Check satisfaction and gather feedback on service improvements',
                'resolution_strategy_3': 'Offer loyalty benefits or refer-a-friend programmes',
                'customer_personality': 'Stable Value Seekers customer who appreciates good value and service.',
                'communication_style': 'Friendly and informative. Focus on value and appreciation.',
                'conversation_starters': 'We wanted to check in and see how your energy service is working for you.',
                'avoid_topics': 'Avoid unnecessary upselling or frequent contact.',
                'success_indicators': 'Positive response and continued satisfaction with service.',
                'follow_up_timing': 'Quarterly check-ins or as needed based on account activity.'
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
        """Build prompt for Bedrock based on complete customer profile"""
        # Extract customer information from the complete profile
        if isinstance(customer_data, dict) and 'basic' in customer_data:
            # This is a complete profile
            basic = customer_data.get('basic', {})
            activity = customer_data.get('activity', {})
            customer_name = basic.get('Name', 'Valued Customer')
            customer_id = basic.get('Customer_ID', 'Unknown')
            preferred_channel = basic.get('Preferred_Channel', 'Email')
            location = basic.get('Location', 'Unknown')
            age = basic.get('Age', 'Unknown')
            subscription_type = activity.get('Subscription_Type', 'Unknown')
            churn_risk = activity.get('Churn_Risk_Score', 0)
            
            print(f"🤖 AI generating message for {customer_name} (ID: {customer_id}) via {preferred_channel}")
        else:
            # Fallback for basic customer data
            customer_name = customer_data.get('Name', 'Valued Customer')
            customer_id = customer_data.get('Customer_ID', 'Unknown')
            preferred_channel = customer_data.get('Preferred_Channel', 'Email')
            location = customer_data.get('Location', 'Unknown')
            age = customer_data.get('Age', 'Unknown')
            subscription_type = customer_data.get('Subscription_Type', 'Unknown')
            churn_risk = customer_data.get('Churn_Risk_Score', 0)
            
            print(f"🤖 AI generating message for {customer_name} (ID: {customer_id}) via {preferred_channel} [fallback]")
        
        base_prompt = f"""
You are a smart notification system for a British energy supplier. Create a personalised, helpful notification message.

CRITICAL RULES:
- Use British English spelling and terminology throughout
- You MAY use the customer's first name: {customer_name.split()[0] if customer_name != 'Valued Customer' else 'Valued Customer'}
- NEVER invent staff names, dates, reference numbers, or contact details
- Only contact this customer because we have something genuinely helpful to offer
- Keep messages professional but warm and friendly
- Use "we" to refer to the energy supplier
- This message will be sent via {preferred_channel}

Customer Profile:
- Name: {customer_name}
- Location: {location}
- Age: {age}
- Subscription: {subscription_type}
- Preferred Channel: {preferred_channel}
- Churn Risk: {churn_risk}%
- Notification Type: {notification_type}
- Context: {context}
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
        
        elif notification_type == "billing_support":
            prompt = base_prompt + f"""
Context: Customer has recent billing complaints or issues

Create a helpful, empathetic message that:
- Acknowledges their concern without admitting fault
- Offers genuine assistance and support
- Uses their name appropriately for {preferred_channel}
- Shows we value their custom
- Provides clear next steps without specific contact details
- Under 160 characters
"""
        
        elif notification_type == "retention_offer":
            prompt = base_prompt + f"""
Context: Customer has requested to unsubscribe or stop notifications

Create a respectful retention message that:
- Respects their choice but offers alternatives
- Highlights value they might be missing
- Appropriate for someone with {churn_risk}% churn risk
- Not pushy or desperate
- Offers genuine value or options
- Under 150 characters
"""
        
        elif notification_type == "churn_prevention":
            prompt = base_prompt + f"""
Context: High churn risk ({churn_risk}%) customer at risk of leaving

Create a proactive retention message that:
- Shows we value their loyalty
- Offers genuine help or value
- Addresses potential concerns without being presumptuous
- Appropriate for {subscription_type} customer
- Warm but professional tone
- Under 170 characters
"""
        
        elif notification_type == "reactivation":
            prompt = base_prompt + f"""
Context: Long-term customer account has become dormant

Create a welcoming reactivation message that:
- Acknowledges their history with us
- Offers genuine value to re-engage
- Not pushy about their inactivity
- Shows appreciation for their past custom
- Encourages gentle re-engagement
- Under 160 characters
"""
        
        elif notification_type == "gentle_reengagement":
            prompt = base_prompt + f"""
Context: Low engagement customer who might benefit from our services

Create a soft re-engagement message that:
- Offers genuine value or helpful information
- Not pushy about their low engagement
- Appropriate for their {subscription_type} service level
- Focuses on how we can help them
- Warm and helpful tone
- Under 150 characters
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
    
    def generate_engagement_message(self, customer_data, priority_analysis, message_type):
        """Generate focused engagement message using AI"""
        if not self.bedrock_client:
            return self._fallback_engagement_message(customer_data, message_type)
        
        try:
            prompt = self._build_engagement_prompt(customer_data, priority_analysis, message_type)
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 150,
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
            print(f"AI message generation error: {e}")
            return self._fallback_engagement_message(customer_data, message_type)
    
    def _build_engagement_prompt(self, customer_data, priority_analysis, message_type):
        """Build focused prompt for engagement message generation"""
        customer_name = customer_data.get('Name', 'Valued Customer')
        first_name = customer_name.split()[0] if customer_name != 'Valued Customer' else 'Valued Customer'
        churn_risk = customer_data.get('Churn_Risk_Score', 0)
        engagement_score = customer_data.get('Engagement_Score', 50)
        preferred_channel = customer_data.get('Preferred_Channel', 'Email')
        
        prompt = f"""
You are a customer communication specialist for a British energy supplier. Create a personalized engagement message for a Value Seekers customer.

CRITICAL RULES:
- Use British English spelling and terminology throughout
- You MAY use the customer's first name: {first_name}
- Focus on value, savings, and practical benefits
- Keep tone friendly but professional
- Message will be sent via {preferred_channel}

Customer Profile:
- Name: {customer_name}
- Churn Risk: {churn_risk}%
- Engagement Score: {engagement_score}
- Preferred Channel: {preferred_channel}
- Segment: Value Seekers (price-conscious, practical)

Message Type: {message_type}
Priority: {priority_analysis.get('priority', 'medium')}
Contact Reason: {priority_analysis.get('contact_reason', 'Standard engagement')}

Message Requirements:
"""
        
        if message_type == 'retention_focus':
            prompt += f"""
- Acknowledge their loyalty and value to us
- Offer genuine help or value proposition
- Address potential concerns without being presumptuous
- Show we want to keep them as a customer
- Under 160 characters for {preferred_channel}
"""
        elif message_type == 'engagement_boost':
            prompt += f"""
- Re-engage with relevant, valuable content
- Offer something genuinely useful (tips, savings, updates)
- Not pushy about their low engagement
- Focus on how we can help them
- Under 150 characters for {preferred_channel}
"""
        elif message_type == 'value_opportunity':
            prompt += f"""
- Highlight cost-saving opportunities or value
- Mention energy efficiency or bill reduction potential
- Appeal to their practical, value-conscious mindset
- Include gentle call to action
- Under 170 characters for {preferred_channel}
"""
        
        prompt += """

IMPORTANT: 
- Use British English (realise, organised, centre, colour)
- Generate ONLY the message text, no explanations
- Do NOT mention specific staff names, dates, or reference numbers
- Use general terms like "our team", "customer services"
"""
        
        return prompt
    
    def _fallback_engagement_message(self, customer_data, message_type):
        """Fallback engagement messages when AI is unavailable"""
        customer_name = customer_data.get('Name', 'Valued Customer')
        first_name = customer_name.split()[0] if customer_name != 'Valued Customer' else 'Valued Customer'
        
        fallback_messages = {
            'retention_focus': f"Hi {first_name}, we value your custom and want to ensure you're getting the best from your energy service. How can we help?",
            'engagement_boost': f"Hello {first_name}, we have some helpful energy tips that could benefit you. Would you like to learn more?",
            'value_opportunity': f"Hi {first_name}, discover potential savings on your energy bills with our efficiency programme!"
        }
        
        return fallback_messages.get(message_type, f"Hello {first_name}, we wanted to check how your energy service is working for you.")
    
    def _fallback_notification(self, customer_data, notification_type):
        """Fallback notifications when Bedrock is unavailable"""
        segment = customer_data.get('Segment', 'Unknown')
        
        # Extract customer name for personalisation
        customer_name = "Valued Customer"
        if isinstance(customer_data, dict):
            if 'basic' in customer_data:
                customer_name = customer_data.get('basic', {}).get('Name', 'Valued Customer')
            else:
                customer_name = customer_data.get('Name', 'Valued Customer')
        
        first_name = customer_name.split()[0] if customer_name != 'Valued Customer' else 'Valued Customer'
        
        fallback_messages = {
            "billing_support": f"Hello {first_name}, we've noticed your recent enquiry about billing. Our customer services team is here to help resolve any concerns.",
            "retention_offer": f"Hi {first_name}, we understand you may wish to reduce communications. We'd like to offer you more control over what you receive from us.",
            "churn_prevention": f"Dear {first_name}, we value your custom and want to ensure you're getting the best from your energy service. How can we help?",
            "reactivation": f"Hello {first_name}, we've missed you! We have some updates that might interest you about your energy service.",
            "gentle_reengagement": f"Hi {first_name}, we have some helpful energy tips that could benefit you. Would you like to learn more?",
            "billing_alert": f"Hello {first_name}, we've recognised a billing matter on your account. Our team is reviewing it.",
            "energy_saving": f"Hi {first_name}, we have some energy-saving tips that could help reduce your bills.",
            "engagement": f"Hello {first_name}, we have some updates tailored for customers like you.",
            "value_seeker_special": f"Hi {first_name}, discover potential savings on your energy bills with our efficiency programme!"
        }
        
        return fallback_messages.get(notification_type, "Important update about your energy account.")

class SmartNotificationEngine:
    def __init__(self, db_path='customer_data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def get_value_seekers_data(self):
        """Get comprehensive data for Value Seekers customers only"""
        query = """
        SELECT 
            cp.*,
            aa.Account_Status,
            aa.Last_Transaction,
            aa.Last_Login,
            aa.Recent_Activity,
            aa.Engagement_Score,
            aa.Account_Tenure_Years,
            aa.Subscription_Type,
            aa.Churn_Risk_Score
        FROM customer_profiles cp
        LEFT JOIN account_activity aa ON cp.Customer_ID = aa.Customer_ID
        WHERE cp.customer_segment = 'Value Seekers'
        """
        
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def get_customer_complete_profile(self, customer_id):
        """Get complete customer profile from all tables"""
        profile = {}
        
        print(f"🔍 Getting complete profile for customer {customer_id}")
        
        # Customer basic info
        cursor = self.conn.execute(
            "SELECT * FROM customer_profiles WHERE Customer_ID = ?", 
            (customer_id,)
        )
        customer_data = cursor.fetchone()
        if customer_data:
            columns = [desc[0] for desc in cursor.description]
            profile['basic'] = dict(zip(columns, customer_data))
            print(f"  📋 Basic: Name={profile['basic'].get('Name')}, OptedIn={profile['basic'].get('Opted_In')}")
        else:
            print(f"  ❌ No basic profile found for customer {customer_id}")
        
        # Account activity
        cursor = self.conn.execute(
            "SELECT * FROM account_activity WHERE Customer_ID = ?", 
            (customer_id,)
        )
        activity_data = cursor.fetchone()
        if activity_data:
            columns = [desc[0] for desc in cursor.description]
            profile['activity'] = dict(zip(columns, activity_data))
            print(f"  💼 Activity: ChurnRisk={profile['activity'].get('Churn_Risk_Score')}, Status={profile['activity'].get('Account_Status')}")
        else:
            print(f"  ❌ No activity profile found for customer {customer_id}")
        
        # Recent interactions (last 3)
        cursor = self.conn.execute(
            """SELECT * FROM interaction_history 
               WHERE Customer_ID = ? 
               ORDER BY datetime([Date & Time]) DESC 
               LIMIT 3""", 
            (customer_id,)
        )
        interactions = cursor.fetchall()
        if interactions:
            columns = [desc[0] for desc in cursor.description]
            profile['interactions'] = [dict(zip(columns, row)) for row in interactions]
        
        # Recent notifications (last 5)
        cursor = self.conn.execute(
            """SELECT * FROM notification_history 
               WHERE Customer_ID = ? 
               ORDER BY datetime(Sent_Date) DESC 
               LIMIT 5""", 
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
        
    def load_data(self):
        """Reload data from database"""
        # Reconnect to database to get fresh data
        self.conn.close()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def get_customer_segments(self):
        """Get unique customer segments"""
        return self.df['Segment'].unique().tolist()
    
    def get_billing_anomalies(self):
        """Get Value Seekers customers with billing issues from interactions"""
        query = """
        SELECT DISTINCT cp.Customer_ID, cp.Name, cp.Location, cp.customer_segment
        FROM customer_profiles cp
        JOIN interaction_history ih ON cp.Customer_ID = ih.Customer_ID
        WHERE cp.customer_segment = 'Value Seekers' 
        AND (ih.Summary LIKE '%billing%' OR ih.Interaction_Type = 'Complaint')
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_high_risk_customers(self, threshold=70):
        """Get Value Seekers customers with high churn risk"""
        query = """
        SELECT cp.*, aa.Churn_Risk_Score
        FROM customer_profiles cp
        JOIN account_activity aa ON cp.Customer_ID = aa.Customer_ID
        WHERE cp.customer_segment = 'Value Seekers' 
        AND aa.Churn_Risk_Score > ?
        """
        return pd.read_sql_query(query, self.conn, params=[threshold])
    
    def get_low_engagement_customers(self, engagement_threshold=30):
        """Get Value Seekers customers with low engagement scores"""
        query = """
        SELECT cp.*, aa.Engagement_Score
        FROM customer_profiles cp
        JOIN account_activity aa ON cp.Customer_ID = aa.Customer_ID
        WHERE cp.customer_segment = 'Value Seekers' 
        AND aa.Engagement_Score < ?
        """
        return pd.read_sql_query(query, self.conn, params=[engagement_threshold])
    
    def _get_opted_in_value_seekers(self):
        """Get Value Seekers customers who have opted in to notifications"""
        query = """
        SELECT 
            cp.Customer_ID,
            cp.Name,
            cp.Opted_In,
            cp.Preferred_Channel,
            cp.Location,
            cp.Age,
            cp.customer_segment,
            aa.Churn_Risk_Score,
            aa.Account_Status,
            aa.Engagement_Score,
            aa.Subscription_Type
        FROM customer_profiles cp
        LEFT JOIN account_activity aa ON cp.Customer_ID = aa.Customer_ID
        WHERE cp.customer_segment = 'Value Seekers' 
        AND cp.Opted_In = 'Yes'
        """
        
        cursor = self.conn.execute(query)
        customers = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            customer = dict(zip(columns, row))
            customers.append(customer)
        
        print(f"📊 Found {len(customers)} opted-in Value Seekers customers")
        return customers
    
    def _should_contact_customer_simple(self, customer, priority_analysis):
        """Simple decision logic for whether to contact a customer"""
        # Always contact high priority customers
        if priority_analysis.get('priority') == 'high':
            return True
        
        # Contact medium priority if they have high churn risk
        if priority_analysis.get('priority') == 'medium' and customer.get('Churn_Risk_Score', 0) > 60:
            return True
        
        # Contact if they have billing issues (would be detected in priority analysis)
        if 'billing' in priority_analysis.get('contact_reason', '').lower():
            return True
        
        # Skip low priority customers to avoid notification fatigue
        return False
    
    def _determine_message_type_simple(self, customer, priority_analysis):
        """Determine message type based on customer situation"""
        churn_risk = customer.get('Churn_Risk_Score', 0)
        engagement = customer.get('Engagement_Score', 50)
        
        # High churn risk customers need retention messaging
        if churn_risk > 80:
            return 'retention_focus'
        
        # Low engagement customers need re-engagement
        if engagement < 30:
            return 'engagement_boost'
        
        # Value Seekers always appreciate cost-saving opportunities
        return 'value_opportunity'
    
    def _assemble_notification(self, customer, priority_analysis, message, message_type):
        """Assemble complete notification with all customer service insights"""
        # Map database channels to system channels
        channel_mapping = {
            'Email': 'email',
            'SMS': 'sms',
            'App Push': 'app_notification',
            'Phone': 'phone_call'
        }
        
        preferred_channel = customer.get('Preferred_Channel', 'Email')
        notification_channel = channel_mapping.get(preferred_channel, 'email')
        
        return {
            'customer_id': customer['Customer_ID'],
            'customer_name': customer['Name'],
            'segment': 'Value Seekers',
            'message_type': message_type,
            'priority': priority_analysis.get('priority', 'medium'),
            'urgency': priority_analysis.get('urgency', 'routine'),
            'risk_score': priority_analysis.get('risk_score', 5),
            'churn_risk': customer.get('Churn_Risk_Score', 0),
            'message': message,
            'channel': notification_channel,
            'preferred_channel': preferred_channel,
            'opted_in': customer.get('Opted_In', 'Yes'),
            # Customer Service Insights
            'contact_reason': priority_analysis.get('contact_reason', 'Standard engagement'),
            'customer_insights': priority_analysis.get('customer_insights', {}),
            'resolution_strategy': priority_analysis.get('resolution_strategy', {}),
            'ai_generated': True
        }
    
    def generate_unified_notifications(self):
        """Simplified notification workflow: Get Value Seekers → AI Priority Analysis → AI Message Generation → Assemble Notifications"""
        notifications = []
        bedrock_generator = BedrockNotificationGenerator()
        
        print("🤖 Starting simplified notification workflow...")
        
        # Step 1: Get Value Seekers customers who have opted in
        value_seekers_customers = self._get_opted_in_value_seekers()
        print(f"🎯 Found {len(value_seekers_customers)} opted-in Value Seekers customers")
        
        # Step 2: Process each customer through AI analysis and message generation
        for customer in value_seekers_customers:
            try:
                customer_id = customer['Customer_ID']
                customer_name = customer['Name']
                print(f"🔍 Processing {customer_name} (ID: {customer_id})")
                
                # Step 3: AI Priority Analysis
                priority_analysis = bedrock_generator.analyse_customer_priority(customer)
                
                # Step 4: Decide if we should contact this customer
                if not self._should_contact_customer_simple(customer, priority_analysis):
                    print(f"  ⏭️ Skipping {customer_name} - no urgent need for contact")
                    continue
                
                # Step 5: Determine message type based on customer situation
                message_type = self._determine_message_type_simple(customer, priority_analysis)
                
                # Step 6: AI Message Generation
                message = bedrock_generator.generate_engagement_message(customer, priority_analysis, message_type)
                
                # Step 7: Assemble complete notification
                notification = self._assemble_notification(customer, priority_analysis, message, message_type)
                notifications.append(notification)
                
                print(f"  ✅ Created {priority_analysis['priority']} priority notification for {customer_name}")
                
            except Exception as e:
                print(f"  ❌ Error processing customer {customer.get('Customer_ID', 'Unknown')}: {e}")
                continue
        
        # Step 8: Sort by priority and risk score
        notifications.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 1),
            x['risk_score']
        ), reverse=True)
        
        print(f"✅ Generated {len(notifications)} targeted notifications")
        return notifications
    
    def _should_contact_customer(self, analysis):
        """Strategic decision on whether to contact this customer - only if it will genuinely help"""
        customer_data = analysis['customer_data']
        complete_profile = analysis.get('complete_profile', {})
        basic = complete_profile.get('basic', {})
        activity = complete_profile.get('activity', {})
        interactions = complete_profile.get('interactions', [])
        
        # FIRST: Check if customer has opted in to receive notifications
        opted_in = basic.get('Opted_In', 'No')
        customer_id = customer_data.get('Customer_ID', 'Unknown')
        customer_name = basic.get('Name', f'Customer {customer_id}')
        
        print(f"🔍 Checking contact for: ID={customer_id}, Name={customer_name}, OptedIn={opted_in}")
        
        if opted_in != 'Yes':
            print(f"❌ {customer_name} (ID: {customer_id}) has not opted in - skipping")
            return False
        
        print(f"✅ {customer_name} (ID: {customer_id}) has opted in - checking if contact needed")
        
        # SECOND: Only contact if we have something genuinely helpful
        churn_risk = activity.get('Churn_Risk_Score', 0)
        account_status = activity.get('Account_Status', 'Active')
        engagement_score = activity.get('Engagement_Score', 50)
        
        # High churn risk customers who are at risk of leaving - we can help retain them
        if churn_risk > 80 and account_status == 'At Risk':
            print(f"🚨 {customer_name}: High churn risk ({churn_risk}%) + At Risk status - CONTACT NEEDED")
            return True
        
        # Customers with recent billing complaints - we can help resolve issues
        recent_billing_complaints = [i for i in interactions 
                                   if 'billing' in i.get('Summary', '').lower() 
                                   and i.get('Sentiment') == 'Negative']
        if recent_billing_complaints:
            print(f"💳 {customer_name}: Recent billing complaints - CONTACT NEEDED")
            return True
        
        # Customers who requested to unsubscribe - we can offer alternatives
        unsubscribe_requests = [i for i in interactions 
                              if i.get('Interaction_Type') == 'Unsubscribe']
        if unsubscribe_requests and churn_risk > 60:
            print(f"📤 {customer_name}: Unsubscribe request + high churn risk - CONTACT NEEDED")
            return True
        
        # Very low engagement but high churn risk - targeted re-engagement can help
        if engagement_score < 20 and churn_risk > 70:
            print(f"📉 {customer_name}: Low engagement ({engagement_score}) + high churn risk ({churn_risk}%) - CONTACT NEEDED")
            return True
        
        # Account dormant but customer was previously engaged - we can re-activate
        if account_status == 'Dormant' and activity.get('Account_Tenure_Years', 0) > 2:
            print(f"😴 {customer_name}: Dormant long-term customer - CONTACT NEEDED")
            return True
        
        # High churn risk alone (even if not "At Risk" status)
        if churn_risk > 80:
            print(f"⚠️ {customer_name}: Very high churn risk ({churn_risk}%) - CONTACT NEEDED")
            return True
        
        # Otherwise, don't contact - avoid notification fatigue
        print(f"ℹ️ {customer_name}: No urgent need for contact (Churn: {churn_risk}%, Engagement: {engagement_score}, Status: {account_status}) - avoiding fatigue")
        return False
    
    def _determine_optimal_notification_type(self, customer_data, analysis):
        """Determine the BEST notification type based on specific customer needs"""
        complete_profile = analysis.get('complete_profile', {})
        basic = complete_profile.get('basic', {})
        activity = complete_profile.get('activity', {})
        interactions = complete_profile.get('interactions', [])
        
        churn_risk = activity.get('Churn_Risk_Score', 0)
        account_status = activity.get('Account_Status', 'Active')
        engagement_score = activity.get('Engagement_Score', 50)
        
        # Priority 1: Recent billing complaints - help resolve issues
        recent_billing_complaints = [i for i in interactions 
                                   if 'billing' in i.get('Summary', '').lower() 
                                   and i.get('Sentiment') == 'Negative']
        if recent_billing_complaints:
            return 'billing_support'
        
        # Priority 2: Unsubscribe requests - offer alternatives
        unsubscribe_requests = [i for i in interactions 
                              if i.get('Interaction_Type') == 'Unsubscribe']
        if unsubscribe_requests:
            return 'retention_offer'
        
        # Priority 3: High churn risk at-risk customers - targeted retention
        if churn_risk > 80 and account_status == 'At Risk':
            return 'churn_prevention'
        
        # Priority 4: Dormant long-term customers - reactivation
        if account_status == 'Dormant' and activity.get('Account_Tenure_Years', 0) > 2:
            return 'reactivation'
        
        # Priority 5: Low engagement high-risk - gentle re-engagement
        if engagement_score < 20 and churn_risk > 70:
            return 'gentle_reengagement'
        
        # Default: Should not reach here if _should_contact_customer works correctly
        return 'gentle_reengagement'
    
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
    
    def _determine_customer_context_from_profile(self, complete_profile):
        """Determine context for AI analysis based on complete customer profile"""
        contexts = []
        
        basic = complete_profile.get('basic', {})
        activity = complete_profile.get('activity', {})
        interactions = complete_profile.get('interactions', [])
        notifications = complete_profile.get('notifications', [])
        actions = complete_profile.get('actions', [])
        
        # Account status issues
        if activity.get('Account_Status') == 'At Risk':
            contexts.append("Account at risk of churn")
        
        # High churn risk
        churn_risk = activity.get('Churn_Risk_Score', 0)
        if churn_risk > 80:
            contexts.append(f"High churn risk: {churn_risk}%")
        elif churn_risk > 60:
            contexts.append(f"Medium churn risk: {churn_risk}%")
        
        # Low engagement
        engagement_score = activity.get('Engagement_Score', 0)
        if engagement_score < 30:
            contexts.append("Low engagement with services")
        
        # Recent negative interactions
        negative_interactions = [i for i in interactions if i.get('Sentiment') == 'Negative']
        if negative_interactions:
            contexts.append(f"Recent negative interactions: {len(negative_interactions)}")
        
        # Billing issues from interactions
        billing_interactions = [i for i in interactions if 'billing' in i.get('Summary', '').lower()]
        if billing_interactions:
            contexts.append("Recent billing-related interactions")
        
        # Poor notification engagement
        if notifications:
            opened_count = sum(1 for n in notifications if n.get('Opened') == 'Yes')
            if opened_count == 0:
                contexts.append("Never opens notifications")
            elif opened_count < len(notifications) * 0.3:
                contexts.append("Low notification engagement")
        
        # Recommended actions indicate issues
        urgent_actions = [a for a in actions if a.get('Urgency_Level') == 'High']
        if urgent_actions:
            contexts.append(f"Urgent actions required: {len(urgent_actions)}")
        
        # Value Seekers specific context
        if basic.get('customer_segment') == 'Value Seekers':
            contexts.append("Target segment: Value Seekers - focus on cost savings and value")
            
            # Income bracket context
            income = basic.get('Income_Bracket', 'Unknown')
            if income == 'Low':
                contexts.append("Low income bracket - price sensitive")
        
        return "; ".join(contexts) if contexts else "Standard Value Seekers customer analysis"
    
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
    
    def _f database exists before initializing

# Initialize the notification engine with SQLite database
notification_engine = SmartNotificationEngine('customer_data.db')

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/customers')
def get_customers():
    """Get Value Seekers customers data only"""
    try:
        value_seekers_df = notification_engine.get_value_seekers_data()
        customers = value_seekers_df.replace({np.nan: None}).to_dict('records')
        return jsonify(customers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    try:
        value_seekers_df = notification_engine.get_value_seekers_data()
        
        if len(value_seekers_df) > 0:
            segments = {
                'Value Seekers': {
                    'Customer_ID': len(value_seekers_df),
                    'Avg_Age': round(value_seekers_df['Age'].mean(), 1),
                    'Avg_Engagement_Score': round(value_seekers_df['Engagement_Score'].mean(), 1),
                    'Avg_Churn_Risk': round(value_seekers_df['Churn_Risk_Score'].mean(), 1)
                }
            }
        else:
            segments = {'Value Seekers': {'Customer_ID': 0, 'Avg_Age': 0, 'Avg_Engagement_Score': 0, 'Avg_Churn_Risk': 0}}
        
        return jsonify(segments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications')
def get_notifications():
    """Generate unified AI-driven notifications"""
    notifications = notification_engine.generate_unified_notifications()
    return jsonify(notifications)

@app.route('/api/billing-issues')
def get_billing_issues():
    """Get Value Seekers customers with billing issues"""
    try:
        billing_issues = notification_engine.get_billing_anomalies()
        billing_data = billing_issues.replace({np.nan: None}).to_dict('records')
        return jsonify(billing_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/value-seekers')
def get_value_seekers():
    """Get detailed Value Seekers analysis from database"""
    try:
        # Get Value Seekers data from database
        value_seekers_df = notification_engine.get_value_seekers_data()
        
        if len(value_seekers_df) == 0:
            return jsonify({
                'total_count': 0,
                'avg_age': 0,
                'avg_engagement_score': 0,
                'avg_churn_risk': 0,
                'subscription_breakdown': {},
                'location_breakdown': {},
                'income_breakdown': {},
                'satisfaction_breakdown': {}
            })
        
        # Calculate statistics from database fields
        analysis = {
            'total_count': len(value_seekers_df),
            'avg_age': round(value_seekers_df['Age'].mean(), 1),
            'avg_engagement_score': round(value_seekers_df['Engagement_Score'].mean(), 1),
            'avg_churn_risk': round(value_seekers_df['Churn_Risk_Score'].mean(), 1),
            'subscription_breakdown': value_seekers_df['Subscription_Type'].value_counts().to_dict(),
            'location_breakdown': value_seekers_df['Location'].value_counts().to_dict(),
            'income_breakdown': value_seekers_df['Income_Bracket'].value_counts().to_dict(),
            'satisfaction_breakdown': value_seekers_df['Satisfaction_Score'].value_counts().to_dict()
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': f'Database not initialized. Please run: python setup_database.py'}), 500

@app.route('/api/customer-analysis')
def get_customer_analysis():
    """Get AI-powered customer analysis and prioritisation for Value Seekers only"""
    try:
        bedrock_generator = BedrockNotificationGenerator()
        analyses = []
        
        # Analyze only Value Seekers customers
        value_seekers_df = notification_engine.get_value_seekers_data()
        print(f"🎯 Analysing {len(value_seekers_df)} Value Seekers customers only")
        
        for _, customer in value_seekers_df.iterrows():
            customer_basic = customer.to_dict()
            complete_profile = notification_engine.get_customer_complete_profile(customer_basic['Customer_ID'])
            context = notification_engine._determine_customer_context_from_profile(complete_profile)
            analysis = bedrock_generator.analyse_customer_priority(complete_profile, context)
            
            analyses.append({
                'customer_id': customer_basic['Customer_ID'],
                'segment': customer_basic['customer_segment'],
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