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
                region_name='us-east-1'
            )
            self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        except Exception as e:
            print(f"Warning: Could not initialize Bedrock client: {e}")
            self.bedrock_client = None
    
    def analyse_customer_priority(self, customer_data):
        """Use AI to determine customer contact priority and strategy with proactive approach"""
        prompt = self._build_priority_prompt(customer_data)
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
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
    
    def _build_priority_prompt(self, customer_data):
        """Build comprehensive prompt for AI priority analysis using all available data"""
        # Basic customer info
        churn_risk = customer_data.get('Churn_Risk_Score', 0)
        engagement = customer_data.get('Engagement_Score', 50)
        account_status = customer_data.get('Account_Status', 'Active')
        age = customer_data.get('Age', 'Unknown')
        location = customer_data.get('Location', 'Unknown')
        subscription_type = customer_data.get('Subscription_Type', 'Unknown')
        satisfaction_score = customer_data.get('Satisfaction_Score', 'Unknown')
        income_bracket = customer_data.get('Income_Bracket', 'Unknown')
        customer_since = customer_data.get('Customer_Since', 'Unknown')
        account_tenure = customer_data.get('Account_Tenure_Years', 'Unknown')
        last_transaction = customer_data.get('Last_Transaction', 'Unknown')
        last_login = customer_data.get('Last_Login', 'Unknown')
        recent_activity = customer_data.get('Recent_Activity', 'Unknown')
        
        # Interaction history analysis
        interactions = customer_data.get('interactions', [])
        recent_complaints = [i for i in interactions if i.get('Interaction_Type') == 'Complaint']
        negative_interactions = [i for i in interactions if i.get('Sentiment') == 'Negative']
        unresolved_issues = [i for i in interactions if i.get('Resolution_Status') in ['Pending', 'Escalated']]
        billing_issues = [i for i in interactions if 'billing' in i.get('Summary', '').lower()]
        unsubscribe_requests = [i for i in interactions if i.get('Interaction_Type') == 'Unsubscribe']
        
        # Notification history analysis
        notifications = customer_data.get('notification_history', [])
        unopened_notifications = [n for n in notifications if n.get('Opened') == 'No']
        failed_deliveries = [n for n in notifications if n.get('Delivery_Status') == 'Failed']
        no_action_notifications = [n for n in notifications if n.get('Action_Taken') == 'None']
        
        # Recommended actions analysis
        actions = customer_data.get('recommended_actions', [])
        high_urgency_actions = [a for a in actions if a.get('Urgency_Level') == 'High']
        follow_up_required = [a for a in actions if a.get('Follow_Up_Required') == 'Yes']
        
        # Build detailed interaction summaries
        interaction_details = []
        for i, interaction in enumerate(interactions[:5], 1):
            detail = f"  {i}. {interaction.get('Interaction_Type', 'Unknown')} via {interaction.get('Channel', 'Unknown')} on {interaction.get('interaction_date', 'Unknown date')}"
            detail += f"\n     Summary: {interaction.get('Summary', 'No summary')}"
            detail += f"\n     Sentiment: {interaction.get('Sentiment', 'Unknown')} | Status: {interaction.get('Resolution_Status', 'Unknown')}"
            interaction_details.append(detail)
        
        # Build detailed notification summaries
        notification_details = []
        for i, notification in enumerate(notifications[:5], 1):
            detail = f"  {i}. {notification.get('Notification_Type', 'Unknown')} via {notification.get('Channel', 'Unknown')} sent {notification.get('sent_date', 'Unknown date')}"
            detail += f"\n     Opened: {notification.get('Opened', 'Unknown')} | Clicked: {notification.get('Clicked', 'Unknown')} | Action: {notification.get('Action_Taken', 'None')}"
            detail += f"\n     Delivery: {notification.get('Delivery_Status', 'Unknown')} | Priority: {notification.get('Notification_Priority', 'Unknown')}"
            notification_details.append(detail)
        
        # Build detailed action summaries
        action_details = []
        for i, action in enumerate(actions[:5], 1):
            detail = f"  {i}. Scenario: {action.get('Scenario', 'Unknown')}"
            detail += f"\n     Action: {action.get('Recommended_Action', 'Unknown')}"
            detail += f"\n     Urgency: {action.get('Urgency_Level', 'Unknown')} | Follow-up: {action.get('Follow_Up_Required', 'Unknown')} | Team: {action.get('Assigned_Team', 'Unknown')}"
            action_details.append(detail)
        
        prompt = f"""
You are an AI customer engagement strategist for ScottishPower. Analyze this Value Seekers customer using comprehensive data from all systems and provide detailed insights for customer service agents.

CRITICAL RULES:
- Use British English spelling and terminology throughout
- Focus on actionable insights for customer service teams
- Provide specific, practical guidance based on actual data patterns
- Consider Value Seekers characteristics (price-conscious, practical, value-focused)
- Identify specific trigger factors from the data provided
- Reference specific dates, interactions, and data points in your analysis

=== CUSTOMER PROFILE: {customer_data.get('Name', 'Unknown')} (ID: {customer_data.get('Customer_ID', 'Unknown')}) ===

BASIC INFORMATION:
- Customer Name: {customer_data.get('Name', 'Unknown')}
- Age: {age} years old | Location: {location}
- Income Bracket: {income_bracket} | Customer Since: {customer_since}
- Account Tenure: {account_tenure} years
- Preferred Communication Channel: {customer_data.get('Preferred_Channel', 'Unknown')}
- Current Satisfaction Score: {satisfaction_score}/10 ({"Very Low" if satisfaction_score < 3 else "Low" if satisfaction_score < 5 else "Moderate" if satisfaction_score < 7 else "Good" if satisfaction_score < 9 else "Excellent"})

ACCOUNT STATUS & RISK INDICATORS:
- Account Status: {account_status}
- Churn Risk Score: {churn_risk}% ({"CRITICAL" if churn_risk > 80 else "HIGH" if churn_risk > 60 else "MODERATE" if churn_risk > 40 else "LOW"})
- Engagement Score: {engagement}/100 ({"Very Low" if engagement < 20 else "Low" if engagement < 40 else "Moderate" if engagement < 60 else "Good" if engagement < 80 else "High"})
- Subscription Type: {subscription_type}
- Last Transaction: {last_transaction}
- Last Login: {last_login}
- Recent Activity: {recent_activity}

DETAILED INTERACTION HISTORY ({len(interactions)} recent interactions):
{chr(10).join(interaction_details) if interaction_details else "  No recent interactions found"}

DETAILED NOTIFICATION ENGAGEMENT ({len(notifications)} recent notifications):
{chr(10).join(notification_details) if notification_details else "  No recent notifications found"}

DETAILED RECOMMENDED ACTIONS ({len(actions)} active recommendations):
{chr(10).join(action_details) if action_details else "  No recommended actions found"}

CRITICAL ANALYSIS POINTS:
- Satisfaction vs Churn Risk: {satisfaction_score}/10 satisfaction with {churn_risk}% churn risk {"indicates serious dissatisfaction" if satisfaction_score < 4 and churn_risk > 60 else "shows concerning trend" if satisfaction_score < 6 and churn_risk > 40 else "appears stable"}
- Engagement Pattern: {engagement} engagement score with {"poor" if len(unopened_notifications) > len(notifications)/2 else "moderate" if len(unopened_notifications) > 0 else "good"} notification response rate
- Service Issues: {len(unresolved_issues)} unresolved issues, {len(billing_issues)} billing problems, {len(recent_complaints)} recent complaints
- Communication Preference: Prefers {customer_data.get('Preferred_Channel', 'Unknown')} channel, {"high" if income_bracket == "High" else "moderate" if income_bracket == "Medium" else "low"} income bracket affects communication style needs

VALUE SEEKERS SEGMENT CHARACTERISTICS:
- Price-conscious and practical decision makers
- Respond well to cost savings and clear value propositions
- Prefer straightforward, no-nonsense communication
- Income level ({income_bracket}) affects price sensitivity and switching likelihood
- Tenure ({account_tenure} years) indicates {"strong" if account_tenure > 3 else "moderate" if account_tenure > 1 else "new"} relationship with ScottishPower

Provide your analysis in this EXACT format (ALL FIELDS ARE REQUIRED):

PRIORITY: [HIGH/MEDIUM/LOW]
URGENCY: [IMMEDIATE/WITHIN_24H/WITHIN_WEEK/ROUTINE]
RISK_SCORE: [Single number from 1-10 where 10 is highest risk. Examples: 3, 7, 9]
CONTACT_REASON: [Detailed explanation of why this customer needs contact - what specific issue or opportunity requires attention]
TRIGGER_FACTORS: [MANDATORY FIELD - You MUST provide specific data points from the customer profile that triggered this recommendation. Be very specific with actual numbers and dates. Examples: "Churn risk 85% + satisfaction score 2/10 + last login 45 days ago", "3 unresolved billing complaints since January + engagement score 12%", "5 unopened payment reminders + previous late payment history", "Account tenure 4 years but satisfaction dropped from 8 to 3 in last quarter"]
POTENTIAL_IMPACT: [What could happen if this customer isn't contacted - business impact]

CUSTOMER_INSIGHTS: [Personality traits, motivations, and communication preferences based on Value Seekers profile and actual behavior data]
COMMUNICATION_STYLE: [Recommended tone and approach - direct/empathetic/technical/consultative]
CONVERSATION_STARTERS: [Specific opening lines or key points to mention when contacting]

CRITICAL REQUIREMENTS:
1. TRIGGER_FACTORS is MANDATORY - You MUST analyze the customer data and identify specific trigger factors
2. Use actual data points from the customer profile (churn risk %, satisfaction scores, interaction dates, etc.)
3. Be specific with numbers, percentages, and timeframes
4. If no obvious triggers exist, state "Routine review cycle - no immediate risk factors identified"
5. NEVER leave TRIGGER_FACTORS empty or use generic placeholder text

TRIGGER FACTOR EXAMPLES TO FOLLOW:
- "Churn risk 78% + satisfaction score 3/10 + 2 unresolved billing issues"
- "Engagement score 18% + 6 unopened notifications in last month + last login 21 days ago"
- "Previous payment difficulties in Q1 + upcoming billing cycle + income bracket: Low"
- "Account status: At Risk + 3 negative sentiment interactions + no recent activity"

PROACTIVE ENGAGEMENT STRATEGY:
Focus on preventing issues before they escalate, especially for Value Seekers who are price-sensitive:

PROACTIVE BILLING SUPPORT:
- Previous billing issues + upcoming billing cycle = proactive payment support
- Payment difficulties in past + current financial stress indicators = early intervention
- High usage patterns + Value Seekers segment = proactive cost management advice
- Seasonal usage changes + budget concerns = advance planning support

RETENTION PREVENTION:
- Early warning signs (satisfaction dropping, engagement declining) = proactive value demonstration
- Contract renewal approaching + any service issues = retention conversation
- Competitor activity in area + customer concerns = proactive competitive response
- Service quality issues + Value Seekers expectations = immediate resolution focus

COMPREHENSIVE TRIGGER FACTOR ANALYSIS:
- Churn Risk Factors: High churn risk (>70%), "At Risk" status, low satisfaction scores (<5)
- Engagement Issues: Low engagement (<30%), unopened notifications (>70%), no recent logins
- Service Issues: Unresolved complaints, billing problems, negative sentiment interactions
- Behavioral Changes: Reduced activity, unsubscribe requests, failed notification deliveries
- Proactive Opportunities: Previous payment struggles + upcoming bills, seasonal usage changes
- Value Demonstration: High-value customers with declining satisfaction, cost concerns
- Urgency Escalators: Multiple unresolved issues, high urgency recommended actions, recent complaints
- Value Seekers Specific: Income bracket vs subscription mismatch, payment-related interactions
- Retention Risks: Multiple negative interactions, unsubscribe requests, dormant accounts

PROACTIVE PRIORITY GUIDELINES:
- HIGH: Churn risk >70% OR previous billing struggles + upcoming cycle OR satisfaction <3 OR multiple unresolved issues
- MEDIUM: Churn risk 40-70% OR declining engagement trends OR seasonal usage concerns OR proactive value opportunities
- LOW: Stable metrics with proactive relationship building OR seasonal check-ins OR value reinforcement

PROACTIVE MESSAGING FOCUS:
- Reach out BEFORE problems occur (pre-bill support, seasonal advice, usage alerts)
- Address Value Seekers concerns about costs BEFORE they become complaints
- Provide solutions and support BEFORE customers ask for help
- Demonstrate ongoing value BEFORE satisfaction drops

Use British English throughout (realise, organised, prioritise, centre, colour).
"""
        #print(prompt)
        return prompt
    
    def _parse_priority_response(self, ai_response):
        """Parse AI response into structured data"""
        try:
            print(f"🔍 DEBUG: Raw AI Response:\n{ai_response}\n" + "="*50)
            
            lines = ai_response.strip().split('\n')
            result = {
                'priority': 'medium',
                'urgency': 'routine',
                'risk_score': 5,
                'contact_reason': 'Standard customer engagement',
                'trigger_factors': 'Routine customer review',
                'potential_impact': 'Minimal impact if not addressed',
                'customer_insights': 'Value-conscious customer who appreciates practical solutions',
                'communication_style': 'Professional and straightforward',
                'conversation_starters': 'Hello, we wanted to check how your energy service is working for you'
            }
            
            print(f"🔍 DEBUG: Processing {len(lines)} lines from AI response")
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    print(f"🔍 DEBUG: Found key='{key}', value='{value[:100]}...'")
                    
                    # Core priority fields
                    if 'priority' in key:
                        result['priority'] = value.lower()
                        print(f"✅ Set priority: {result['priority']}")
                    elif 'urgency' in key:
                        result['urgency'] = value.lower()
                        print(f"✅ Set urgency: {result['urgency']}")
                    elif 'risk_score' in key or 'risk' in key:
                        try:
                            # Try to extract number from various formats
                            import re
                            numbers = re.findall(r'\d+', value)
                            if numbers:
                                score = int(numbers[0])
                                # Ensure it's in valid range 1-10
                                result['risk_score'] = max(1, min(10, score))
                                print(f"✅ Set risk_score: {result['risk_score']} (from '{value}')")
                            else:
                                result['risk_score'] = 5
                                print(f"⚠️ No number found in risk_score value '{value}', using default: 5")
                        except Exception as e:
                            result['risk_score'] = 5
                            print(f"⚠️ Failed to parse risk_score '{value}': {e}, using default: 5")
                    
                    # Context and reasoning
                    elif 'contact_reason' in key:
                        result['contact_reason'] = value
                        print(f"✅ Set contact_reason: {value[:50]}...")
                    elif 'trigger_factors' in key or 'trigger' in key:
                        result['trigger_factors'] = value
                        print(f"✅ Set trigger_factors: {value[:50]}...")
                    elif 'potential_impact' in key:
                        result['potential_impact'] = value
                        print(f"✅ Set potential_impact: {value[:50]}...")
                    
                    # Customer insights and communication
                    elif 'customer_insights' in key:
                        result['customer_insights'] = value
                        print(f"✅ Set customer_insights: {value[:50]}...")
                    elif 'communication_style' in key:
                        result['communication_style'] = value
                        print(f"✅ Set communication_style: {value[:50]}...")
                    elif 'conversation_starters' in key:
                        result['conversation_starters'] = value
                        print(f"✅ Set conversation_starters: {value[:50]}...")
                    else:
                        print(f"❓ Unrecognized key: '{key}'")
            
            # Ensure risk_score is meaningful based on priority if it's still default
            if result['risk_score'] == 5:  # Default value
                if result['priority'] == 'high':
                    result['risk_score'] = 8
                    print(f"✅ Adjusted risk_score to {result['risk_score']} based on high priority")
                elif result['priority'] == 'low':
                    result['risk_score'] = 3
                    print(f"✅ Adjusted risk_score to {result['risk_score']} based on low priority")
            
            # Ensure trigger_factors is meaningful
            if result['trigger_factors'] == 'Routine customer review' or not result['trigger_factors']:
                print("⚠️ Trigger factors missing or default, generating from other fields...")
                trigger_parts = []
                if result['priority'] == 'high':
                    trigger_parts.append("High priority classification")
                if result['risk_score'] > 6:
                    trigger_parts.append(f"Risk score: {result['risk_score']}/10")
                if 'churn' in result.get('contact_reason', '').lower():
                    trigger_parts.append("Churn risk detected")
                if 'billing' in result.get('contact_reason', '').lower():
                    trigger_parts.append("Billing concerns")
                
                if trigger_parts:
                    result['trigger_factors'] = ' + '.join(trigger_parts)
                    print(f"✅ Generated trigger_factors: {result['trigger_factors']}")
            
            print(f"🎯 FINAL RESULT - risk_score: {result['risk_score']}, trigger_factors: '{result['trigger_factors']}'")
            return result
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            # Return minimal structure if parsing fails
            return {
                'priority': 'medium',
                'urgency': 'routine',
                'risk_score': 5,
                'contact_reason': 'AI analysis error - manual review needed',
                'trigger_factors': 'AI parsing failed',
                'potential_impact': 'Unknown impact',
                'customer_insights': 'Manual analysis required',
                'communication_style': 'Professional and helpful',
                'conversation_starters': 'Hello, we wanted to check how your service is going'
            }
    
    def generate_engagement_message(self, customer_data, priority_analysis, message_type):
        """Generate personalized engagement message using AI"""
        prompt = self._build_message_prompt(customer_data, priority_analysis, message_type)
        
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
    
    def _build_message_prompt(self, customer_data, priority_analysis, message_type):
        """Build enhanced prompt for message generation with detailed customer context"""
        customer_name = customer_data.get('Name', 'Valued Customer')
        first_name = customer_name.split()[0] if customer_name != 'Valued Customer' else 'Valued Customer'
        preferred_channel = customer_data.get('Preferred_Channel', 'Email')
        
        # Get recent interaction context and proactive indicators
        interactions = customer_data.get('interactions', [])
        recent_interaction_context = ""
        proactive_indicators = []
        
        if interactions:
            latest = interactions[0]
            recent_interaction_context = f"Recent interaction: {latest.get('Interaction_Type', 'Unknown')} - {latest.get('Summary', 'No details')}"
            
            # Check for proactive opportunities
            payment_issues = [i for i in interactions if 'payment' in i.get('Summary', '').lower() or 'billing' in i.get('Summary', '').lower()]
            if payment_issues:
                proactive_indicators.append("Previous payment/billing concerns - proactive support needed")
        
        # Check notification history for engagement patterns
        notifications = customer_data.get('notification_history', [])
        if notifications:
            payment_reminders = [n for n in notifications if n.get('Notification_Type') == 'Payment Reminder']
            if payment_reminders and any(n.get('Action_Taken') == 'Contacted support' for n in payment_reminders):
                proactive_indicators.append("Previous payment reminder led to support contact - proactive billing assistance needed")
        
        # Check recommended actions for proactive opportunities
        actions = customer_data.get('recommended_actions', [])
        if actions:
            energy_actions = [a for a in actions if 'energy' in a.get('Recommended_Action', '').lower()]
            if energy_actions:
                proactive_indicators.append("Energy-saving recommendations available - proactive cost management opportunity")
        
        # Get satisfaction and risk context
        satisfaction = customer_data.get('Satisfaction_Score', 5)
        churn_risk = customer_data.get('Churn_Risk_Score', 0)
        account_status = customer_data.get('Account_Status', 'Active')
        
        prompt = f"""
Create a personalized engagement message for a ScottishPower Value Seekers customer based on their specific situation.

=== CUSTOMER CONTEXT ===
Customer: {first_name} (Age: {customer_data.get('Age', 'Unknown')}, Location: {customer_data.get('Location', 'Unknown')})
Channel: {preferred_channel}
Income Bracket: {customer_data.get('Income_Bracket', 'Unknown')}
Satisfaction Score: {satisfaction}/10
Account Status: {account_status}
Churn Risk: {churn_risk}%
Tenure: {customer_data.get('Account_Tenure_Years', 'Unknown')} years

=== SITUATION ANALYSIS ===
Message Type: {message_type}
Priority Level: {priority_analysis.get('priority', 'medium')}
Contact Reason: {priority_analysis.get('contact_reason', 'Standard engagement')}
{recent_interaction_context}

=== PROACTIVE OPPORTUNITIES ===
{chr(10).join(proactive_indicators) if proactive_indicators else "Standard proactive engagement opportunity"}

=== PROACTIVE MESSAGE REQUIREMENTS ===
- Use British English spelling throughout
- Address customer as {first_name}
- Tone: {"Empathetic and solution-focused" if priority_analysis.get('priority') == 'high' else "Friendly and value-focused" if priority_analysis.get('priority') == 'medium' else "Warm and appreciative"}
- Approach: PROACTIVE - reach out before problems escalate
- Focus: {"Prevent issues and provide immediate support" if churn_risk > 70 else "Proactive value demonstration and cost management" if message_type == 'value_opportunity' else "Proactive engagement with practical benefits"}
- Length: Under {"140 characters for SMS" if preferred_channel == "SMS" else "160 characters for email/app" if preferred_channel in ["Email", "App Push"] else "180 characters"}
- Reference ScottishPower if company name needed

=== PROACTIVE VALUE SEEKERS APPROACH ===
- ANTICIPATE needs before customers ask (billing support, seasonal advice, cost alerts)
- PREVENT problems rather than react to them (pre-bill assistance, usage warnings)
- DEMONSTRATE ongoing value proactively (savings opportunities, efficiency tips)
- SUPPORT financial concerns before they become complaints
- Use straightforward, no-nonsense language that shows you understand their priorities
- Mention specific cost-saving opportunities and practical benefits
- Show that ScottishPower is looking out for their financial interests

=== PROACTIVE MESSAGING EXAMPLES ===
- "Hi {first_name}, your next bill is due soon. Based on your usage, here are some tips to keep costs down..."
- "Hello {first_name}, we've noticed seasonal changes in your area. Here's how to manage your energy costs..."
- "Hi {first_name}, as a valued customer, we wanted to share some cost-saving opportunities before your next billing cycle..."

Generate ONLY the personalized message text, no explanations or additional content.
"""
        return prompt
    

class SmartNotificationEngine:
    def __init__(self, db_path='customer_data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def get_opted_in_value_seekers(self):
        """Get Value Seekers customers with comprehensive data from all tables"""
        query = """
        SELECT 
            cp.Customer_ID,
            cp.Name,
            cp.Opted_In,
            cp.Preferred_Channel,
            cp.Location,
            cp.Age,
            cp.customer_segment,
            cp.Income_Bracket,
            cp.Customer_Since,
            cp.Satisfaction_Score,
            aa.Churn_Risk_Score,
            aa.Account_Status,
            aa.Engagement_Score,
            aa.Subscription_Type,
            aa.Last_Transaction,
            aa.Last_Login,
            aa.Recent_Activity,
            aa.Account_Tenure_Years
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
            
            # Enrich with interaction history
            customer['interactions'] = self._get_recent_interactions(customer['Customer_ID'])
            
            # Enrich with notification history
            customer['notification_history'] = self._get_notification_history(customer['Customer_ID'])
            
            # Enrich with recommended actions
            customer['recommended_actions'] = self._get_recommended_actions(customer['Customer_ID'])
            
            customers.append(customer)
        
        return customers
    
    def _get_recent_interactions(self, customer_id, limit=5):
        """Get recent interactions for a customer"""
        query = """
        SELECT Interaction_Type, Sentiment, Summary, Resolution_Status, Channel,
               datetime([Date & Time]) as interaction_date
        FROM interaction_history 
        WHERE Customer_ID = ? 
        ORDER BY datetime([Date & Time]) DESC 
        LIMIT ?
        """
        
        cursor = self.conn.execute(query, (customer_id, limit))
        interactions = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            interactions.append(dict(zip(columns, row)))
        
        return interactions
    
    def _get_notification_history(self, customer_id, limit=5):
        """Get recent notification history for a customer"""
        query = """
        SELECT Notification_Type, Opened, Clicked, Action_Taken, 
               Delivery_Status, Notification_Priority, Response_Time_Hours,
               datetime(Sent_Date) as sent_date
        FROM notification_history 
        WHERE Customer_ID = ? 
        ORDER BY datetime(Sent_Date) DESC 
        LIMIT ?
        """
        
        cursor = self.conn.execute(query, (customer_id, limit))
        notifications = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            notifications.append(dict(zip(columns, row)))
        
        return notifications
    
    def _get_recommended_actions(self, customer_id):
        """Get recommended actions for a customer"""
        query = """
        SELECT Scenario, Recommended_Action, Urgency_Level, 
               Follow_Up_Required, Assigned_Team
        FROM recommended_actions 
        WHERE Customer_ID = ?
        """
        
        cursor = self.conn.execute(query, (customer_id,))
        actions = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            actions.append(dict(zip(columns, row)))
        
        return actions
    
    def should_contact_customer(self, customer, priority_analysis):
        """Decide if customer should be contacted"""
        priority = priority_analysis.get('priority', 'low')
        churn_risk = customer.get('Churn_Risk_Score', 0)
        
        # Always contact high priority
        if priority == 'high':
            return True
        
        # Contact medium priority with high churn risk
        if priority == 'medium' and churn_risk > 60:
            return True
        
        # Skip low priority to avoid fatigue
        return False
    
    def determine_message_type(self, customer, priority_analysis):
        """Determine message type based on customer situation"""
        churn_risk = customer.get('Churn_Risk_Score', 0)
        engagement = customer.get('Engagement_Score', 50)
        
        if churn_risk > 80:
            return 'retention_focus'
        elif engagement < 30:
            return 'engagement_boost'
        else:
            return 'value_opportunity'
    
    def assemble_notification(self, customer, priority_analysis, message, message_type):
        """Create complete notification object with comprehensive customer service insights"""
        channel_mapping = {
            'Email': 'email',
            'SMS': 'sms',
            'App Push': 'app_notification',
            'Phone': 'phone_call'
        }
        
        preferred_channel = customer.get('Preferred_Channel', 'Email')
        notification_channel = channel_mapping.get(preferred_channel, 'email')
        
        return {
            # Basic customer information
            'customer_id': customer['Customer_ID'],
            'customer_name': customer['Name'],
            'segment': 'Value Seekers',
            'message_type': message_type,
            'churn_risk': customer.get('Churn_Risk_Score', 0),
            'opted_in': customer.get('Opted_In', 'Yes'),
            
            # Priority and urgency
            'priority': priority_analysis.get('priority', 'medium'),
            'urgency': priority_analysis.get('urgency', 'routine'),
            'risk_score': priority_analysis.get('risk_score', 5),
            
            # Communication details
            'message': message,
            'channel': notification_channel,
            'preferred_channel': preferred_channel,
            
            # Customer Service Insights - Why and Context
            'contact_reason': priority_analysis.get('contact_reason', 'Standard engagement'),
            'trigger_factors': priority_analysis.get('trigger_factors', 'Routine review'),
            'potential_impact': priority_analysis.get('potential_impact', 'Minimal impact if not addressed'),
            
            # Customer Understanding
            'customer_insights': priority_analysis.get('customer_insights', 'Value-conscious customer'),
            'communication_style': priority_analysis.get('communication_style', 'Professional and helpful'),
            'conversation_starters': priority_analysis.get('conversation_starters', 'Hello, we wanted to check how your service is going'),
            

            
            # System metadata
            'ai_generated': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_notifications(self):
        """Main method to generate all notifications"""
        notifications = []
        bedrock_generator = BedrockNotificationGenerator()
        
        print("🤖 Starting simplified notification workflow...")
        
        # Get opted-in Value Seekers customers
        customers = self.get_opted_in_value_seekers()
        print(f"🎯 Found {len(customers)} opted-in Value Seekers customers")
        
        # Process each customer
        for customer in customers:
            try:
                customer_id = customer['Customer_ID']
                customer_name = customer['Name']
                print(f"🔍 Processing {customer_name} (ID: {customer_id})")
                
                # AI Priority Analysis
                priority_analysis = bedrock_generator.analyse_customer_priority(customer)
                
                # Decide if we should contact
                if not self.should_contact_customer(customer, priority_analysis):
                    print(f"  ⏭️ Skipping {customer_name} - no urgent need for contact")
                    continue
                
                # Determine message type
                message_type = self.determine_message_type(customer, priority_analysis)
                
                # Generate message
                message = bedrock_generator.generate_engagement_message(customer, priority_analysis, message_type)
                
                # Assemble notification
                notification = self.assemble_notification(customer, priority_analysis, message, message_type)
                notifications.append(notification)
                
                print(f"  ✅ Created {priority_analysis['priority']} priority notification for {customer_name}")
                
            except Exception as e:
                print(f"  ❌ Error processing customer {customer.get('Customer_ID', 'Unknown')}: {e}")
                continue
        
        # Sort by priority and risk
        notifications.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 1),
            x['risk_score']
        ), reverse=True)
        
        print(f"✅ Generated {len(notifications)} targeted notifications")
        return notifications

# Initialize the notification engine
if not os.path.exists('customer_data.db'):
    print("❌ Database not found! Please run: python database_setup.py")
    exit(1)

notification_engine = SmartNotificationEngine('customer_data.db')

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/notifications')
def get_notifications():
    """Generate notifications using the clean, simplified system"""
    try:
        notifications = notification_engine.generate_notifications()
        return jsonify(notifications)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers')
def get_customers():
    """Get Value Seekers customers"""
    try:
        customers = notification_engine.get_opted_in_value_seekers()
        return jsonify(customers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-notification', methods=['POST'])
def send_notification():
    """Simulate sending a notification"""
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/segments')
def get_segments():
    """Get customer segments (Value Seekers only)"""
    try:
        customers = notification_engine.get_opted_in_value_seekers()
        
        # Since we only have Value Seekers, create a simple summary
        segments = {
            'Value Seekers': {
                'Customer_ID': len(customers),
                'Daily_Energy_Usage_kWh': sum(c.get('Churn_Risk_Score', 0) for c in customers) / len(customers) if customers else 0
            }
        }
        
        return jsonify(segments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/billing-issues')
def get_billing_issues():
    """Get customers with billing issues"""
    try:
        # For now, return empty list since we don't have billing anomaly data in our clean system
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/value-seekers')
def get_value_seekers():
    """Get Value Seekers analysis"""
    try:
        customers = notification_engine.get_opted_in_value_seekers()
        
        if not customers:
            return jsonify({
                'total_count': 0,
                'avg_age': 0,
                'avg_engagement_score': 0,
                'avg_churn_risk': 0,
                'subscription_breakdown': {},
                'location_breakdown': {}
            })
        
        # Calculate statistics
        total_count = len(customers)
        avg_age = sum(c.get('Age', 0) for c in customers) / total_count
        avg_engagement = sum(c.get('Engagement_Score', 0) for c in customers) / total_count
        avg_churn_risk = sum(c.get('Churn_Risk_Score', 0) for c in customers) / total_count
        
        # Breakdown by subscription type
        subscription_breakdown = {}
        location_breakdown = {}
        
        for customer in customers:
            sub_type = customer.get('Subscription_Type', 'Unknown')
            location = customer.get('Location', 'Unknown')
            
            subscription_breakdown[sub_type] = subscription_breakdown.get(sub_type, 0) + 1
            location_breakdown[location] = location_breakdown.get(location, 0) + 1
        
        return jsonify({
            'total_count': total_count,
            'avg_age': round(avg_age, 1),
            'avg_engagement_score': round(avg_engagement, 1),
            'avg_churn_risk': round(avg_churn_risk, 1),
            'subscription_breakdown': subscription_breakdown,
            'location_breakdown': location_breakdown
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)