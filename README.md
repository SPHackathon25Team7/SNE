https://sphackathon25team7.atlassian.net/

https://teams.live.com/meet/9399517845520?p=cjZ9g6Tz9QNmx8hdif

SPHackathon25Team7@outlook.com

# Smart Notification Engine

A Flask-based web application that analyses energy supplier customer data from multiple sources and generates AI-powered, targeted notifications focusing on Value Seekers customers.

## Features

- **AI-Powered Customer Segmentation**: Uses AWS Bedrock to classify customers into segments (Value Seekers, Traditionalists, Digital Natives, Eco Savers)
- **Multi-Table Data Analysis**: Integrates data from 5 different sources for comprehensive customer profiles
- **Value Seekers Focus**: Optimised for your target customer segment to save processing costs
- **Smart Notifications**: AI-generated, personalised notifications in British English
- **Interactive Dashboard**: Clean, tabbed interface with priority-based notification display
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

### Customer Classification
- Analyses customer behaviour across all data sources
- Uses AWS Bedrock (Claude 3 Sonnet) for intelligent segmentation
- Fallback rule-based classification when AI unavailable

### Smart Notifications
- AI-generated messages in British English
- Never invents names, dates, or contact details
- Personalised based on complete customer profile
- Priority-based ordering (Critical → Important → Routine)

### Value Seekers Focus
- Only processes Value Seekers customers
- Saves ~75% on AI processing costs
- Targeted insights for your priority segment

## API Endpoints

- `GET /api/customers` - Value Seekers customer data
- `GET /api/segments` - Value Seekers segment statistics
- `GET /api/notifications` - AI-generated priority notifications
- `GET /api/billing-issues` - Customers with billing-related interactions
- `GET /api/customer-analysis` - AI priority analysis
- `POST /api/refresh-data` - Reload database data

## Dashboard Features

### Smart Notifications Tab (Default)
- AI-prioritised customer engagements
- Two-column layout for better viewing
- Priority filtering (Critical/Important/Routine)
- Risk scores and contact strategies

### Value Seekers Tab
- Dedicated insights for target segment
- Key metrics and behaviour patterns
- Solar/EV ownership analysis

### Customer Data Tab
- Simplified overview of customer base
- Segment statistics and billing issues

## Cost Optimisation

- **Focused Processing**: Only analyses Value Seekers (~25% of customers)
- **Efficient AI Usage**: ~£0.50-1.00 per 1000 notifications
- **Smart Caching**: Database-driven with minimal API calls
- **Fallback Systems**: Works without AI when needed

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
