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
        """Use AI to determine customer contact priority and strategy"""
        if not self.bedrock_client:
            return self._fallback_priority_analysis(customer_data)
        
        try:
            prompt = self._build_priority_prompt(customer_data)
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 400,
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

Provide your analysis in this EXACT format:

PRIORITY: [HIGH/MEDIUM/LOW]
URGENCY: [IMMEDIATE/WITHIN_24H/WITHIN_WEEK/ROUTINE]
RISK_SCORE: [1-10 scale where 10 is highest risk]
CONTACT_REASON: [Detailed explanation of why this customer needs contact - what specific issue or opportunity requires attention]
TRIGGER_FACTORS: [Specific data points that led to this recommendation - be very specific about what data triggered this]
POTENTIAL_IMPACT: [What could happen if this customer isn't contacted - business impact]

CUSTOMER_INSIGHTS: [Personality traits, motivations, and communication preferences based on Value Seekers profile and actual behavior data]
COMMUNICATION_STYLE: [Recommended tone and approach - direct/empathetic/technical/consultative]
CONVERSATION_STARTERS: [Specific opening lines or key points to mention when contacting]

RESOLUTION_STRATEGY: [Primary recommended approach with specific steps based on their interaction patterns]
ALTERNATIVE_APPROACH: [Backup strategy if primary approach doesn't work]
SUCCESS_INDICATORS: [How to measure if the interaction was successful]
FOLLOW_UP_TIMING: [When and how to follow up after initial contact]

COMPREHENSIVE TRIGGER FACTOR ANALYSIS:
Consider these specific data patterns for trigger identification:
- Churn Risk Factors: High churn risk (>70%), "At Risk" status, low satisfaction scores (<5)
- Engagement Issues: Low engagement (<30%), unopened notifications (>70%), no recent logins
- Service Issues: Unresolved complaints, billing problems, negative sentiment interactions
- Behavioral Changes: Reduced activity, unsubscribe requests, failed notification deliveries
- Opportunity Indicators: High-value customers with low engagement, tenure >2 years with issues
- Urgency Escalators: Multiple unresolved issues, high urgency recommended actions, recent complaints
- Value Seekers Specific: Income bracket vs subscription mismatch, payment-related interactions
- Retention Risks: Multiple negative interactions, unsubscribe requests, dormant accounts

Priority Guidelines:
- HIGH: Churn risk >70% OR multiple unresolved issues OR recent unsubscribe requests OR satisfaction <3
- MEDIUM: Churn risk 40-70% OR low engagement <30% OR billing issues OR high urgency actions
- LOW: Stable metrics with routine maintenance needs OR proactive relationship building

Use British English throughout (realise, organised, prioritise, centre, colour).
"""
        return prompt
    
    def _parse_priority_response(self, ai_response):
        """Parse comprehensive AI response into structured data"""
        try:
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
                'conversation_starters': 'Hello, we wanted to check how your energy service is working for you',
                'resolution_strategy': 'Standard engagement approach focusing on value',
                'alternative_approach': 'Follow up via preferred channel if initial contact unsuccessful',
                'success_indicators': 'Customer expresses satisfaction and engagement',
                'follow_up_timing': 'Follow up in 1-2 weeks if needed'
            }
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    # Core priority fields
                    if 'priority' in key:
                        result['priority'] = value.lower()
                    elif 'urgency' in key:
                        result['urgency'] = value.lower()
                    elif 'risk_score' in key:
                        try:
                            result['risk_score'] = int(value.split()[0])
                        except:
                            result['risk_score'] = 5
                    
                    # Context and reasoning
                    elif 'contact_reason' in key:
                        result['contact_reason'] = value
                    elif 'trigger_factors' in key:
                        result['trigger_factors'] = value
                    elif 'potential_impact' in key:
                        result['potential_impact'] = value
                    
                    # Customer insights and communication
                    elif 'customer_insights' in key:
                        result['customer_insights'] = value
                    elif 'communication_style' in key:
                        result['communication_style'] = value
                    elif 'conversation_starters' in key:
                        result['conversation_starters'] = value
                    
                    # Resolution strategies
                    elif 'resolution_strategy' in key:
                        result['resolution_strategy'] = value
                    elif 'alternative_approach' in key:
                        result['alternative_approach'] = value
                    elif 'success_indicators' in key:
                        result['success_indicators'] = value
                    elif 'follow_up_timing' in key:
                        result['follow_up_timing'] = value
            
            return result
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._fallback_priority_analysis({})
    
    def _fallback_priority_analysis(self, customer_data):
        """Comprehensive fallback priority analysis using all available data when AI is unavailable"""
        # Basic metrics
        churn_risk = customer_data.get('Churn_Risk_Score', 0)
        engagement = customer_data.get('Engagement_Score', 50)
        account_status = customer_data.get('Account_Status', 'Active')
        satisfaction = customer_data.get('Satisfaction_Score', 5)
        
        # Interaction analysis
        interactions = customer_data.get('interactions', [])
        recent_complaints = [i for i in interactions if i.get('Interaction_Type') == 'Complaint']
        negative_interactions = [i for i in interactions if i.get('Sentiment') == 'Negative']
        unresolved_issues = [i for i in interactions if i.get('Resolution_Status') in ['Pending', 'Escalated']]
        billing_issues = [i for i in interactions if 'billing' in i.get('Summary', '').lower()]
        unsubscribe_requests = [i for i in interactions if i.get('Interaction_Type') == 'Unsubscribe']
        
        # Notification analysis
        notifications = customer_data.get('notification_history', [])
        unopened_rate = len([n for n in notifications if n.get('Opened') == 'No']) / len(notifications) if notifications else 0
        
        # Recommended actions analysis
        actions = customer_data.get('recommended_actions', [])
        high_urgency_actions = [a for a in actions if a.get('Urgency_Level') == 'High']
        
        # Determine priority based on comprehensive factors
        trigger_factors = []
        
        if churn_risk > 80:
            trigger_factors.append(f'Very high churn risk: {churn_risk}%')
        if account_status == 'At Risk':
            trigger_factors.append(f'Account status: {account_status}')
        if satisfaction < 4:
            trigger_factors.append(f'Low satisfaction score: {satisfaction}/10')
        if len(unresolved_issues) > 0:
            trigger_factors.append(f'{len(unresolved_issues)} unresolved issues')
        if len(billing_issues) > 0:
            trigger_factors.append(f'{len(billing_issues)} billing-related problems')
        if len(unsubscribe_requests) > 0:
            trigger_factors.append(f'{len(unsubscribe_requests)} unsubscribe requests')
        if len(high_urgency_actions) > 0:
            trigger_factors.append(f'{len(high_urgency_actions)} high urgency recommended actions')
        if engagement < 30:
            trigger_factors.append(f'Low engagement score: {engagement}')
        if unopened_rate > 0.7:
            trigger_factors.append(f'High unopened notification rate: {int(unopened_rate*100)}%')
        
        # HIGH PRIORITY CONDITIONS
        if (churn_risk > 70 or account_status == 'At Risk' or satisfaction < 3 or 
            len(unresolved_issues) > 1 or len(unsubscribe_requests) > 0 or len(high_urgency_actions) > 0):
            
            return {
                'priority': 'high',
                'urgency': 'immediate',
                'risk_score': min(10, max(7, int(churn_risk/10))),
                'contact_reason': f'Multiple critical factors identified: {", ".join(trigger_factors[:3])}. Immediate intervention required to prevent churn.',
                'trigger_factors': '; '.join(trigger_factors),
                'potential_impact': 'High risk of customer churn, negative reviews, and potential revenue loss. May influence other customers in same location.',
                'customer_insights': f'Value Seekers customer showing signs of dissatisfaction. {len(negative_interactions)} negative interactions suggest frustration with service or pricing.',
                'communication_style': 'Empathetic and solution-focused. Acknowledge specific issues and provide immediate value proposition',
                'conversation_starters': f'We\'ve noticed some concerns with your service and want to address them immediately',
                'resolution_strategy': f'Address specific issues: {", ".join([i.get("Summary", "") for i in unresolved_issues[:2]])}. Offer immediate resolution and retention incentives.',
                'alternative_approach': 'If primary issues can\'t be resolved immediately, offer account credits and escalate to specialist team',
                'success_indicators': 'Customer expresses satisfaction with resolution, agrees to continue service, reduces complaint frequency',
                'follow_up_timing': 'Follow up within 24-48 hours to ensure resolution effectiveness and monitor satisfaction'
            }
        # MEDIUM PRIORITY CONDITIONS
        elif (churn_risk > 40 or engagement < 30 or len(billing_issues) > 0 or 
              len(recent_complaints) > 0 or unopened_rate > 0.5):
            
            return {
                'priority': 'medium',
                'urgency': 'within_week',
                'risk_score': min(7, max(4, int(churn_risk/15) + len(negative_interactions))),
                'contact_reason': f'Moderate risk factors identified: {", ".join(trigger_factors[:3])}. Proactive engagement needed to prevent escalation.',
                'trigger_factors': '; '.join(trigger_factors) if trigger_factors else f'Churn risk: {churn_risk}%, Engagement: {engagement}',
                'potential_impact': 'Customer may become disengaged and consider switching at contract renewal. Risk of negative word-of-mouth.',
                'customer_insights': f'Value Seekers customer showing early warning signs. {len(billing_issues)} billing issues and {len(recent_complaints)} complaints suggest need for attention.',
                'communication_style': 'Friendly and value-focused. Highlight benefits and address any concerns proactively',
                'conversation_starters': 'We want to ensure you\'re getting the best value from your energy service and address any concerns',
                'resolution_strategy': f'Address specific concerns: {", ".join([i.get("Summary", "") for i in (billing_issues + recent_complaints)[:2]])}. Offer value-focused solutions.',
                'alternative_approach': 'If specific issues resolved, focus on value demonstration and loyalty building',
                'success_indicators': 'Increased engagement, resolution of specific issues, improved satisfaction feedback',
                'follow_up_timing': 'Monitor engagement over 2-3 weeks, follow up if metrics don\'t improve'
            }
        
        # LOW PRIORITY CONDITIONS
        else:
            return {
                'priority': 'low',
                'urgency': 'routine',
                'risk_score': max(1, min(4, int(churn_risk/20))),
                'contact_reason': f'Stable Value Seekers customer with good metrics. Proactive relationship maintenance opportunity.',
                'trigger_factors': f'Stable metrics: Churn risk {churn_risk}%, Engagement {engagement}, Satisfaction {satisfaction}/10',
                'potential_impact': 'Minimal immediate risk, but opportunity to strengthen loyalty and prevent future churn',
                'customer_insights': f'Stable Value Seekers customer (satisfaction: {satisfaction}/10) who appreciates good value and reliable service',
                'communication_style': 'Friendly and informative. Focus on appreciation and ongoing value demonstration',
                'conversation_starters': 'We wanted to check in and see how your energy service is working for you',
                'resolution_strategy': 'Relationship maintenance with helpful tips, service updates, or loyalty recognition',
                'alternative_approach': 'Seasonal check-ins or relevant energy-saving advice based on usage patterns',
                'success_indicators': 'Positive response, continued satisfaction, stable account metrics',
                'follow_up_timing': 'Quarterly check-ins or as needed based on account activity changes'
            }
    
    def generate_engagement_message(self, customer_data, priority_analysis, message_type):
        """Generate personalized engagement message"""
        if not self.bedrock_client:
            return self._fallback_message(customer_data, message_type)
        
        try:
            prompt = self._build_message_prompt(customer_data, priority_analysis, message_type)
            
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
            print(f"Message generation error: {e}")
            return self._fallback_message(customer_data, message_type)
    
    def _build_message_prompt(self, customer_data, priority_analysis, message_type):
        """Build enhanced prompt for message generation with detailed customer context"""
        customer_name = customer_data.get('Name', 'Valued Customer')
        first_name = customer_name.split()[0] if customer_name != 'Valued Customer' else 'Valued Customer'
        preferred_channel = customer_data.get('Preferred_Channel', 'Email')
        
        # Get recent interaction context
        interactions = customer_data.get('interactions', [])
        recent_interaction_context = ""
        if interactions:
            latest = interactions[0]
            recent_interaction_context = f"Recent interaction: {latest.get('Interaction_Type', 'Unknown')} - {latest.get('Summary', 'No details')}"
        
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

=== MESSAGE REQUIREMENTS ===
- Use British English spelling throughout
- Address customer as {first_name}
- Tone: {"Empathetic and solution-focused" if priority_analysis.get('priority') == 'high' else "Friendly and value-focused" if priority_analysis.get('priority') == 'medium' else "Warm and appreciative"}
- Focus: {"Immediate problem resolution" if churn_risk > 70 else "Value demonstration and cost savings" if message_type == 'value_opportunity' else "Re-engagement with practical benefits"}
- Length: Under {"140 characters for SMS" if preferred_channel == "SMS" else "160 characters for email/app" if preferred_channel in ["Email", "App Push"] else "180 characters"}
- Reference ScottishPower if company name needed

=== VALUE SEEKERS APPROACH ===
- Emphasize practical benefits and cost savings
- Use straightforward, no-nonsense language
- Mention specific value propositions when relevant
- Avoid complex technical details or lengthy explanations

Generate ONLY the personalized message text, no explanations or additional content.
"""
        return prompt
    
    def _fallback_message(self, customer_data, message_type):
        """Fallback messages when AI unavailable"""
        customer_name = customer_data.get('Name', 'Valued Customer')
        first_name = customer_name.split()[0] if customer_name != 'Valued Customer' else 'Valued Customer'
        
        messages = {
            'retention_focus': f"Hi {first_name}, we value your custom and want to ensure you're getting the best from your energy service.",
            'engagement_boost': f"Hello {first_name}, we have some helpful energy tips that could benefit you.",
            'value_opportunity': f"Hi {first_name}, discover potential savings on your energy bills with our efficiency programme!"
        }
        
        return messages.get(message_type, f"Hello {first_name}, we wanted to check how your energy service is working for you.")

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
            
            # Resolution Strategies
            'resolution_strategy': priority_analysis.get('resolution_strategy', 'Standard approach'),
            'alternative_approach': priority_analysis.get('alternative_approach', 'Follow up via preferred channel'),
            'success_indicators': priority_analysis.get('success_indicators', 'Customer expresses satisfaction'),
            'follow_up_timing': priority_analysis.get('follow_up_timing', 'Follow up in 1-2 weeks if needed'),
            
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