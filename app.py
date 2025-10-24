from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

class SmartNotificationEngine:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        
    def load_data(self):
        """Reload data from CSV"""
        self.df = pd.read_csv(self.csv_path)
        
    def get_customer_segments(self):
        """Get unique customer segments"""
        return self.df['Segment'].unique().tolist()
    
    def get_billing_anomalies(self):
        """Get customers with billing anomalies"""
        return self.df[self.df['Billing_Anomaly'] != 'None']
    
    def get_high_energy_users(self, threshold=25):
        """Get customers with high daily energy usage"""
        return self.df[self.df['Daily_Energy_Usage_kWh'] > threshold]
    
    def get_low_engagement_customers(self, click_threshold=3, open_threshold=10):
        """Get customers with low campaign engagement"""
        return self.df[
            (self.df['Campaign_Clicks'] <= click_threshold) & 
            (self.df['Campaign_Opens'] <= open_threshold)
        ]
    
    def generate_notifications(self):
        """Generate targeted notifications for different customer scenarios"""
        notifications = []
        
        # Billing anomaly notifications
        billing_issues = self.get_billing_anomalies()
        for _, customer in billing_issues.iterrows():
            if customer['Billing_Anomaly'] == 'Overcharge':
                notifications.append({
                    'customer_id': customer['Customer_ID'],
                    'segment': customer['Segment'],
                    'type': 'billing_alert',
                    'priority': 'high',
                    'message': f"We've detected a potential overcharge on your account. Our team is reviewing your bill.",
                    'channel': 'email_sms'
                })
            elif customer['Billing_Anomaly'] == 'Missed Payment':
                notifications.append({
                    'customer_id': customer['Customer_ID'],
                    'segment': customer['Segment'],
                    'type': 'payment_reminder',
                    'priority': 'high',
                    'message': f"Payment reminder: Your recent payment appears to be missing. Please check your account.",
                    'channel': 'email_sms'
                })
            elif customer['Billing_Anomaly'] == 'Dispute':
                notifications.append({
                    'customer_id': customer['Customer_ID'],
                    'segment': customer['Segment'],
                    'type': 'dispute_update',
                    'priority': 'medium',
                    'message': f"Update on your billing dispute: Our team is working to resolve your concern.",
                    'channel': 'email'
                })
        
        # High energy usage notifications
        high_users = self.get_high_energy_users()
        for _, customer in high_users.iterrows():
            if customer['Segment'] == 'Eco Savers':
                notifications.append({
                    'customer_id': customer['Customer_ID'],
                    'segment': customer['Segment'],
                    'type': 'energy_saving_tip',
                    'priority': 'low',
                    'message': f"Your energy usage is higher than average. Here are some eco-friendly tips to reduce consumption.",
                    'channel': 'app_notification'
                })
        
        # Low engagement re-engagement
        low_engagement = self.get_low_engagement_customers()
        for _, customer in low_engagement.iterrows():
            if customer['Segment'] == 'Digital Natives':
                notifications.append({
                    'customer_id': customer['Customer_ID'],
                    'segment': customer['Segment'],
                    'type': 'engagement',
                    'priority': 'low',
                    'message': f"Check out our new digital features and exclusive offers just for you!",
                    'channel': 'push_notification'
                })
        
        return notifications

# Initialize the notification engine
csv_file_path = r"Extra Data Challenge 4#.csv"
notification_engine = SmartNotificationEngine(csv_file_path)

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/customers')
def get_customers():
    """Get all customers data"""
    customers = notification_engine.df.to_dict('records')
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
    """Get customer segments summary"""
    segments = notification_engine.df.groupby('Segment').agg({
        'Customer_ID': 'count',
        'Daily_Energy_Usage_kWh': 'mean',
        'Campaign_Clicks': 'mean',
        'Campaign_Opens': 'mean'
    }).round(2).to_dict('index')
    return jsonify(segments)

@app.route('/api/notifications')
def get_notifications():
    """Generate and return notifications"""
    notifications = notification_engine.generate_notifications()
    return jsonify(notifications)

@app.route('/api/billing-issues')
def get_billing_issues():
    """Get customers with billing anomalies"""
    billing_issues = notification_engine.get_billing_anomalies()
    return jsonify(billing_issues.to_dict('records'))

@app.route('/api/value-seekers')
def get_value_seekers():
    """Get detailed Value Seekers analysis"""
    value_seekers = notification_engine.df[notification_engine.df['Segment'] == 'Value Seekers']
    
    analysis = {
        'total_count': len(value_seekers),
        'avg_daily_energy': round(value_seekers['Daily_Energy_Usage_kWh'].mean(), 2),
        'avg_seasonal_energy': round(value_seekers['Seasonal_Energy_Usage_kWh'].mean(), 2),
        'solar_ev_breakdown': value_seekers['Solar_EV_Ownership'].value_counts().to_dict(),
        'billing_issues': value_seekers['Billing_Anomaly'].value_counts().to_dict(),
        'avg_campaign_clicks': round(value_seekers['Campaign_Clicks'].mean(), 2),
        'avg_campaign_opens': round(value_seekers['Campaign_Opens'].mean(), 2),
        'regions': value_seekers['Region'].value_counts().to_dict(),
        'support_issues': value_seekers['Support_Ticket_Issue'].value_counts().to_dict()
    }
    
    return jsonify(analysis)

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