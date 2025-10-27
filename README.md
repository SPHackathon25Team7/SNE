https://sphackathon25team7.atlassian.net/

https://teams.live.com/meet/9399517845520?p=cjZ9g6Tz9QNmx8hdif

SPHackathon25Team7@outlook.com

# Smart Notification Engine

A Flask-based web application that analyses energy supplier customer data from multiple sources and generates AI-powered, targeted notifications focusing on Value Seekers customers.

## Features

- **AI-Powered Customer Analysis**: Uses AWS Bedrock to analyze customer behavior and generate priority recommendations
- **Multi-Table Data Integration**: Combines data from 5 different sources for comprehensive customer profiles
- **Value Seekers Focus**: Optimized for your target customer segment to save processing costs
- **Smart Notifications**: AI-generated, personalized notifications with editable messages in British English
- **Streamlined Dashboard**: Clean, single-page interface with collapsible sections for better focus
- **Risk-Based Prioritization**: AI assigns risk scores (1-10) and priority levels for targeted engagement
- **Trigger Factor Analysis**: AI identifies specific data points that warrant customer contact
- **SQLite Database**: Efficient local database with proper relationships and indexing

## Database Structure

The system uses 5 tables created from CSV files:
- **customer_profiles**: Basic customer information and AI-classified segments
- **account_activity**: Account status, engagement scores, churn risk
- **interaction_history**: Customer service interactions and sentiment
- **notification_history**: Past notification performance and engagement
- **recommended_actions**: System-generated action recommendations

## Installation & Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Prepare Data**: Ensure you have the `user_data` folder with these CSV files:
   - Customer Profiles.csv
   - Account Activity Logs.csv
   - Interaction History.csv
   - Notification History.csv
   - Recommended Actions.csv

3. **Setup Database** (First time only):
```bash
python setup_database.py
```
This will:
- Create SQLite database from CSV files
- Use AI to classify customers into segments
- Focus on identifying Value Seekers

4. **Configure AWS Bedrock** (Optional but recommended):
   - Set up AWS credentials
   - Enable Claude 3 Sonnet model access
   - See `bedrock_setup.md` for detailed instructions

5. **Run Application**:
```bash
python app.py
```

6. **Access Dashboard**: `http://localhost:5000`

## AI-Powered Features

### Customer Priority Analysis
- Analyzes customer behavior across all data sources using AWS Bedrock (Claude 3 Sonnet)
- Assigns priority levels (High/Medium/Low) and urgency ratings
- Generates risk scores (1-10 scale) for targeted intervention
- Identifies specific trigger factors from customer data

### Smart Notifications with Editable Messages
- AI-generated messages in British English that agents can edit before sending
- Never invents names, dates, or contact details
- Personalized based on complete customer profile
- Priority-based ordering (Critical → Important → Routine)

### Comprehensive Customer Insights
- **Contact Reason**: Why this customer needs attention
- **Trigger Factors**: Specific data points that led to the recommendation
- **Potential Impact**: What happens if customer isn't contacted
- **Customer Insights**: Personality traits and communication preferences
- **Communication Style**: Recommended tone and approach
- **Conversation Starters**: Opening lines for customer service agents

### Value Seekers Focus
- Only processes Value Seekers customers (your target segment)
- Saves ~75% on AI processing costs
- Targeted insights for maximum ROI

## API Endpoints

- `GET /api/customers` - Value Seekers customer data with comprehensive profiles
- `GET /api/segments` - Value Seekers segment statistics and breakdowns
- `GET /api/notifications` - AI-generated priority notifications with risk scores
- `GET /api/billing-issues` - Customers with billing-related interactions
- `GET /api/value-seekers` - Detailed Value Seekers analysis and insights
- `POST /api/send-notification` - Send edited notification to customer
- `POST /api/refresh-data` - Reload database data (if implemented)

## Dashboard Features

### Streamlined Single-Page Interface
- **Clean Design**: Removed tabs and extra buttons for focused workflow
- **AI-Prioritized Customer Engagements**: Most critical customers appear first
- **Two-Column Layout**: Better viewing of multiple notifications
- **Priority Filtering**: Filter by Critical/Important/Routine notifications
- **Risk Scores**: Visual risk indicators (1-10 scale) for each customer

### Collapsible Information Sections
- **Customer Service Insights**: Expandable section with contact reason, trigger factors, and potential impact
- **Communication Strategy**: Collapsible guidance with customer insights, communication style, and conversation starters
- **Default Collapsed**: Sections start collapsed for cleaner interface, expand on demand

### Editable AI Messages
- **Text Area**: AI-generated messages appear in editable text boxes
- **Personalization**: Agents can modify messages before sending
- **Validation**: System ensures messages aren't empty before sending
- **Confirmation**: Shows exactly what message was sent to customer

### Real-Time Statistics
- **Total Notifications**: Count of generated notifications
- **Priority Breakdown**: Critical/Important/Routine counts
- **Average Risk Score**: Overall risk level across customers
- **Dynamic Updates**: Stats update as notifications are generated

## User Workflow

### Step 1: Generate Notifications
1. Click "🤖 Analyse & Generate Notifications" button
2. AI analyzes all Value Seekers customers and identifies who needs contact
3. System generates prioritized list with risk scores and detailed insights

### Step 2: Review & Filter
1. View notification statistics (Total, Critical, Important, Routine)
2. Use priority filter buttons to focus on specific urgency levels
3. Scan customer list ordered by priority and risk score

### Step 3: Expand Details (Optional)
1. Click "🎯 Customer Service Insights" to see why AI flagged this customer
2. Click "💬 Communication Strategy" for guidance on how to approach them
3. Review trigger factors, potential impact, and conversation starters

### Step 4: Edit & Send
1. Review AI-generated message in editable text area
2. Personalize message with specific details or adjustments
3. Click "📤 Send Notification" to deliver customized message
4. Receive confirmation of exactly what was sent

## Cost Optimization

- **Focused Processing**: Only analyzes Value Seekers (~25% of customers)
- **Efficient AI Usage**: ~£0.50-1.00 per 1000 notifications
- **Smart Caching**: Database-driven with minimal API calls
- **Fallback Systems**: Works without AI when needed
- **Targeted Engagement**: Higher ROI by focusing on priority segment

## British English Compliance

- All AI responses use British spelling and terminology
- Professional, appropriate tone for UK energy supplier
- No invented data or fictional references
- Compliant with UK business communication standards

## Troubleshooting

### Database Issues
```bash
# Recreate database
rm customer_data.db
python setup_database.py
```

### AI Classification Issues
- Check AWS Bedrock setup in `bedrock_setup.md`
- System will use rule-based fallback if AI unavailable
- Test with `python test_british_ai.py`

### No Value Seekers Found
- Check customer classification in database
- Review classification logic in `database_setup.py`
- Manually verify CSV data quality
