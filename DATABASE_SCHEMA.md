# Smart Notification Engine - Database Schema

## 📊 Database Overview

The Smart Notification Engine uses a **SQLite database** with **5 interconnected tables** that provide a comprehensive 360° view of each customer. The database integrates data from multiple CSV sources and is enhanced with AI-powered customer segmentation.

---

## 🗄️ Table Structure

### 1. **customer_profiles** 
*Core customer information and AI-classified segments*

| Column | Type | Description |
|--------|------|-------------|
| `Customer_ID` | INTEGER | **Primary Key** - Unique customer identifier |
| `Name` | TEXT | Customer full name |
| `Age` | INTEGER | Customer age in years |
| `Location` | TEXT | Geographic location |
| `Preferred_Channel` | TEXT | Preferred communication method (Email, SMS, Phone, App Push) |
| `Segment` | TEXT | Original segment classification |
| `Opted_In` | TEXT | Marketing consent status (Yes/No) |
| `Income_Bracket` | TEXT | Income level (Low, Medium, High) |
| `Customer_Since` | TEXT | Customer acquisition date |
| `Satisfaction_Score` | INTEGER | Customer satisfaction rating (1-10) |
| `customer_segment` | TEXT | **AI-Enhanced** - AWS Bedrock classification |

**AI Segments**: Value Seekers, Traditionalists, Digital Natives, Eco Savers

---

### 2. **account_activity**
*Account status, engagement, and churn risk data*

| Column | Type | Description |
|--------|------|-------------|
| `Customer_ID` | INTEGER | **Foreign Key** → customer_profiles |
| `Account_Status` | TEXT | Current account state (Active, Suspended, At Risk) |
| `Last_Transaction` | TEXT | Most recent transaction date |
| `Last_Login` | TEXT | Last system login timestamp |
| `Recent_Activity` | TEXT | Summary of recent account activity |
| `Engagement_Score` | INTEGER | Customer engagement level (0-100) |
| `Account_Tenure_Years` | INTEGER | Years as customer |
| `Subscription_Type` | TEXT | Service plan (Basic, Premium, Green) |
| `Churn_Risk_Score` | INTEGER | **AI Risk Assessment** (0-100%) |

---

### 3. **interaction_history**
*Customer service interactions and sentiment analysis*

| Column | Type | Description |
|--------|------|-------------|
| `Customer_ID` | INTEGER | **Foreign Key** → customer_profiles |
| `Channel` | TEXT | Interaction channel (Phone, Email, Chat, In-Person) |
| `Date & Time` | TEXT | Interaction timestamp |
| `Interaction_Type` | TEXT | Type of interaction (Complaint, Inquiry, Support) |
| `Sentiment` | TEXT | **AI Sentiment** (Positive, Negative, Neutral) |
| `Summary` | TEXT | Interaction description |
| `Response_Time_Minutes` | INTEGER | Time to first response |
| `Resolution_Status` | TEXT | Current status (Resolved, Pending, Escalated) |
| `Agent_ID` | TEXT | Handling agent identifier |

---

### 4. **notification_history**
*Past notification performance and engagement tracking*

| Column | Type | Description |
|--------|------|-------------|
| `Notification_ID` | TEXT | Unique notification identifier |
| `Customer_ID` | INTEGER | **Foreign Key** → customer_profiles |
| `Channel` | TEXT | Delivery channel used |
| `Sent_Date` | TEXT | Notification send timestamp |
| `Notification_Type` | TEXT | Message category |
| `Opened` | TEXT | Whether notification was opened (Yes/No) |
| `Clicked` | TEXT | Whether customer clicked through (Yes/No) |
| `Action_Taken` | TEXT | Customer response action |
| `Delivery_Status` | TEXT | Delivery confirmation (Delivered, Failed, Bounced) |
| `Notification_Priority` | TEXT | Message priority level |
| `Response_Time_Hours` | INTEGER | Time to customer response |

---

### 5. **recommended_actions**
*System-generated action recommendations*

| Column | Type | Description |
|--------|------|-------------|
| `Customer_ID` | INTEGER | **Foreign Key** → customer_profiles |
| `Scenario` | TEXT | Situation requiring action |
| `Recommended_Action` | TEXT | Suggested intervention |
| `Urgency_Level` | TEXT | Action priority (High, Medium, Low) |
| `Follow_Up_Required` | TEXT | Whether follow-up needed (Yes/No) |
| `Assigned_Team` | TEXT | Responsible team/department |

---

## 🔗 Database Relationships

```
customer_profiles (1) ──┬── (∞) account_activity
                        ├── (∞) interaction_history  
                        ├── (∞) notification_history
                        └── (∞) recommended_actions
```

### **Relationship Details**
- **One-to-Many**: Each customer can have multiple records in activity, interaction, notification, and action tables
- **Foreign Key Constraints**: Enabled for data integrity
- **Indexed Columns**: All Customer_ID foreign keys indexed for performance

---

## 🚀 Performance Optimizations

### **Database Indexes**
```sql
CREATE INDEX idx_account_customer_id ON account_activity(Customer_ID);
CREATE INDEX idx_interaction_customer_id ON interaction_history(Customer_ID);
CREATE INDEX idx_notification_customer_id ON notification_history(Customer_ID);
CREATE INDEX idx_actions_customer_id ON recommended_actions(Customer_ID);
```

### **Query Performance**
- **Fast Lookups**: Indexed foreign keys enable rapid customer profile assembly
- **Efficient Joins**: Optimized for multi-table customer analysis
- **Scalable Design**: Handles thousands of customers with sub-second response times

---

## 🤖 AI Integration Points

### **Customer Segmentation**
- **Input**: Complete customer profile from all 5 tables
- **AI Model**: AWS Bedrock (Claude 3 Sonnet)
- **Output**: customer_segment classification
- **Segments**: Value Seekers, Traditionalists, Digital Natives, Eco Savers

### **Priority Analysis**
- **Data Sources**: All tables combined for 360° customer view
- **AI Processing**: Risk assessment, priority scoring, trigger factor identification
- **Output**: Targeted notifications with personalized messaging

---

## 📈 Data Flow

1. **CSV Import** → SQLite tables created from 5 source files
2. **AI Enhancement** → Customer segmentation via AWS Bedrock
3. **Profile Assembly** → Multi-table joins create complete customer profiles
4. **AI Analysis** → Priority scoring and notification generation
5. **Dashboard Display** → Real-time customer insights and actions

---

## 💾 Technical Specifications

- **Database Engine**: SQLite 3
- **Total Tables**: 5 interconnected tables
- **Primary Keys**: Customer_ID based relationships
- **Foreign Key Constraints**: Enabled for data integrity
- **Indexes**: 4 performance indexes on foreign keys
- **AI Integration**: AWS Bedrock for customer classification and analysis
- **Data Sources**: 5 CSV files integrated into unified schema

This schema provides the foundation for comprehensive customer analysis and AI-powered notification generation, enabling targeted engagement with Value Seekers customers.