# Design Document

## Overview

The Simplified Smart Notification Engine uses a streamlined approach that combines database-driven customer identification with focused AI analysis for prioritization and personalized message generation. This design eliminates complex AI workflows while maintaining intelligent customer engagement capabilities.

## Architecture

### Core Components

1. **Customer Data Retrieval**: Query SQLite database for Value Seekers customers
2. **AI Priority Analyzer**: Focused AI analysis for contact priority and customer insights
3. **AI Message Generator**: Personalized message creation for engagement
4. **Notification Orchestrator**: Coordinates the workflow and handles errors
5. **API Endpoints**: Serve notifications to the dashboard

### Data Flow

```
Database Query → Customer Filtering → AI Priority Analysis → AI Message Generation → Notification Assembly → API Response
```

## Components and Interfaces

### 1. Customer Data Service
- **Purpose**: Retrieve and filter Value Seekers customers from database
- **Input**: Database connection
- **Output**: List of opted-in Value Seekers customers with complete profiles
- **Key Methods**:
  - `get_value_seekers_customers()`
  - `get_customer_complete_profile(customer_id)`
  - `check_opt_in_status(customer_id)`

### 2. AI Priority Analyzer
- **Purpose**: Analyze customer data to determine contact priority and strategy
- **Input**: Customer profile data
- **Output**: Structured priority analysis with customer service insights
- **Key Methods**:
  - `analyze_customer_priority(customer_data)`
  - `_build_priority_prompt(customer_data)`
  - `_parse_priority_response(ai_response)`

### 3. AI Message Generator
- **Purpose**: Generate personalized engagement messages
- **Input**: Customer data and priority analysis
- **Output**: Personalized message in British English
- **Key Methods**:
  - `generate_engagement_message(customer_data, priority_analysis)`
  - `_build_message_prompt(customer_data, context)`
  - `_fallback_message(customer_data, message_type)`

### 4. Notification Engine
- **Purpose**: Orchestrate the complete notification generation workflow
- **Input**: Database connection
- **Output**: Complete notifications with customer service insights
- **Key Methods**:
  - `generate_notifications()`
  - `_determine_message_type(customer_data, analysis)`
  - `_should_contact_customer(customer_data, analysis)`

## Data Models

### Customer Profile
```python
{
    'basic': {
        'Customer_ID': str,
        'Name': str,
        'Opted_In': str,
        'Preferred_Channel': str,
        'Location': str,
        'Age': int,
        'customer_segment': str
    },
    'activity': {
        'Churn_Risk_Score': int,
        'Account_Status': str,
        'Engagement_Score': int,
        'Subscription_Type': str
    },
    'interactions': [
        {
            'Interaction_Type': str,
            'Summary': str,
            'Sentiment': str,
            'Date & Time': str
        }
    ]
}
```

### Priority Analysis
```python
{
    'priority': str,  # 'high', 'medium', 'low'
    'urgency': str,   # 'immediate', 'within_24h', 'within_week', 'routine'
    'risk_score': int,  # 1-10
    'contact_reason': str,
    'message_type': str,
    'customer_insights': {
        'personality_type': str,
        'communication_style': str,
        'key_motivators': str,
        'potential_concerns': str
    },
    'resolution_strategy': {
        'primary_approach': str,
        'conversation_starters': str,
        'success_indicators': str,
        'follow_up_timing': str
    }
}
```

### Notification Output
```python
{
    'customer_id': str,
    'customer_name': str,
    'priority': str,
    'urgency': str,
    'risk_score': int,
    'churn_risk': int,
    'message': str,
    'channel': str,
    'preferred_channel': str,
    'message_type': str,
    'contact_reason': str,
    'customer_insights': dict,
    'resolution_strategy': dict,
    'opted_in': str
}
```

## AI Integration Strategy

### Priority Analysis Prompt Structure
```
Role: Customer engagement strategist for British energy supplier
Input: Customer profile with demographics, usage, engagement, and risk data
Output: Structured analysis with priority, urgency, insights, and strategy
Format: Specific key-value pairs for reliable parsing
Language: British English throughout
```

### Message Generation Prompt Structure
```
Role: Customer communication specialist
Input: Customer data and priority analysis context
Output: Personalized engagement message
Constraints: British English, Value Seekers tone, specific channel format
Length: Appropriate for channel (SMS/Email/App)
```

## Error Handling

### AI Service Failures
- **Fallback Logic**: Rule-based priority assignment using churn risk, billing issues, engagement scores
- **Fallback Messages**: Template-based messages with customer name personalization
- **Logging**: All AI failures logged with customer ID and error details

### Database Errors
- **Connection Issues**: Retry logic with exponential backoff
- **Missing Data**: Default values and graceful degradation
- **Query Failures**: Error logging and empty result handling

### Data Validation
- **Customer Data**: Validate required fields before AI processing
- **AI Responses**: Parse and validate AI output structure
- **Channel Mapping**: Ensure valid communication channels

## Testing Strategy

### Unit Tests
- Customer data retrieval and filtering
- AI prompt construction and response parsing
- Fallback logic for various failure scenarios
- Message generation for different customer types

### Integration Tests
- End-to-end notification generation workflow
- Database connectivity and query performance
- AI service integration and error handling
- API endpoint responses and data structure

### Performance Tests
- Notification generation time for typical customer volumes
- Database query optimization
- AI service response times and rate limiting
- Memory usage during batch processing

## Implementation Approach

### Phase 1: Core Infrastructure
1. Simplify existing customer data retrieval
2. Create focused AI prompt templates
3. Implement structured response parsing
4. Add comprehensive error handling

### Phase 2: AI Integration
1. Streamline priority analysis AI calls
2. Implement message generation AI calls
3. Add fallback logic for AI failures
4. Test AI response consistency

### Phase 3: Optimization
1. Performance tuning for database queries
2. AI prompt optimization for better responses
3. Enhanced error logging and monitoring
4. User interface improvements for customer service agents