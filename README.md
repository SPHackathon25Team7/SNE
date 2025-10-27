https://sphackathon25team7.atlassian.net/

SPHackathon25Team7@outlook.com

# Smart Notification Engine

A Flask-based web application that analyses energy supplier customer data and generates targeted notifications based on customer segments, billing issues, and engagement patterns.

## Features

- **Customer Segmentation Analysis**: Analyses different customer types (Digital Natives, Eco Savers, Value Seekers, Traditionalists)
- **Billing Issue Detection**: Identifies customers with overcharges, missed payments, and disputes
- **Smart Notifications**: Generates targeted notifications based on customer behaviour and issues
- **Interactive Dashboard**: Web-based interface to view customer data and manage notifications
- **Multiple Notification Channels**: Supports email, SMS, push notifications, and in-app notifications

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python run.py
```

3. Open your browser and go to: `http://localhost:5000`

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/customers` - Get all customer data
- `GET /api/segments` - Get customer segment summary
- `GET /api/notifications` - Generate notifications
- `GET /api/billing-issues` - Get customers with billing anomalies
- `POST /api/send-notification` - Send notification to customer

## Notification Types

1. **Billing Alerts** (High Priority)
   - Overcharge notifications
   - Payment reminders
   - Dispute updates

2. **Energy Saving Tips** (Low Priority)
   - For high-usage Eco Savers customers

3. **Engagement Campaigns** (Low Priority)
   - Re-engagement for low-activity Digital Natives

## Customer Data Structure

The application expects CSV data with the following columns:
- Customer_ID
- Segment (Digital Natives, Eco Savers, Value Seekers, Traditionalists)
- Region
- Daily_Energy_Usage_kWh
- Seasonal_Energy_Usage_kWh
- Solar_EV_Ownership
- Campaign_Clicks
- Campaign_Opens
- Campaign_Conversions
- Support_Ticket_Issue
- Billing_Anomaly

## Usage

1. The dashboard automatically loads customer data from the CSV file
2. Click "Generate Notifications" to create targeted notifications
3. View customer segments and billing issues in the dashboard
4. Send individual notifications using the "Send" buttons
5. Monitor notification statistics in real-time
