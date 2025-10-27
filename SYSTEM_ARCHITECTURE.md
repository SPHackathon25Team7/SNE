# Smart Notification Engine - System Architecture

## 🏗️ High-Level System Overview

The Smart Notification Engine is an AI-powered customer engagement platform that analyzes multi-source customer data to generate targeted, personalized notifications for Value Seekers customers.

---

## 🔄 System Flow Diagram

```
📊 DATA SOURCES                🗄️ DATABASE LAYER              🤖 AI PROCESSING
┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
│  CSV Files (5)  │   Import   │   SQLite DB     │  Extract   │  AWS Bedrock    │
│                 │ ────────►  │                 │ ────────►  │                 │
│ • Customer      │            │ • 5 Tables      │            │ • Claude 3      │
│   Profiles      │            │ • Relationships │            │   Sonnet        │
│ • Account       │            │ • Indexes       │            │ • Classification│
│   Activity      │            │ • Constraints   │            │ • Analysis      │
│ • Interactions  │            │                 │            │ • Prioritization│
│ • Notifications │            └─────────────────┘            └─────────────────┘
│ • Actions       │                      │                             │
└─────────────────┘                      │                             │
                                         ▼                             ▼
                                ┌─────────────────┐            ┌─────────────────┐
                                │  Data Assembly  │            │ AI Enhancement  │
                                │                 │            │                 │
                                │ • 360° Customer │            │ • Segment       │
                                │   Profiles      │            │   Classification│
                                │ • Multi-table   │            │ • Risk Scoring  │
                                │   Joins         │            │ • Priority      │
                                │ • Complete      │            │   Analysis      │
                                │   Context       │            │ • Message       │
                                └─────────────────┘            │   Generation    │
                                         │                     └─────────────────┘
                                         │                             │
                                         └──────────┬──────────────────┘
                                                    ▼
🎯 FILTERING & TARGETING           ┌─────────────────────────────────┐
┌─────────────────┐               │        SMART PROCESSING         │
│ Value Seekers   │               │                                 │
│ Focus Filter    │               │ • Focus on Value Seekers Only   │
│                 │               │ • AI Priority Classification    │
│ • Target Segment│               │ • Risk Score Assignment (1-10)  │
│ • Cost Savings  │               │ • Trigger Factor Identification │
│ • 75% Reduction │               │ • Personalized Message Gen     │
│   in Processing │               │ • British English Compliance   │
└─────────────────┘               └─────────────────────────────────┘
         │                                         │
         └─────────────────────────────────────────┘
                                  ▼
💻 USER INTERFACE                ┌─────────────────────────────────┐
┌─────────────────┐              │         WEB DASHBOARD           │
│ Flask Web App   │              │                                 │
│                 │              │ • Single Page Interface        │
│ • Dashboard     │              │ • Priority-Ordered Customers   │
│ • Real-time     │              │ • Collapsible Detail Sections  │
│ • Interactive   │              │ • Editable AI Messages         │
│ • Responsive    │              │ • Risk Score Visualization     │
└─────────────────┘              │ • Filter by Priority Level     │
                                 └─────────────────────────────────┘
                                                  │
📤 OUTPUT & ACTIONS                              ▼
┌─────────────────┐              ┌─────────────────────────────────┐
│ Customer        │              │        AGENT WORKFLOW           │
│ Engagement      │              │                                 │
│                 │              │ 1. Generate AI Notifications   │
│ • Personalized  │              │ 2. Review Priority Rankings    │
│   Messages      │              │ 3. Expand Customer Insights    │
│ • Targeted      │              │ 4. Edit AI-Generated Messages  │
│   Outreach      │              │ 5. Send Customized Notifications│
│ • Proactive     │              │ 6. Track Engagement Results    │
│   Intervention  │              └─────────────────────────────────┘
└─────────────────┘
```

---

## 🔧 Component Architecture

### **1. Data Ingestion Layer**
```
CSV Sources → SQLite Database → Indexed Tables
     ↓              ↓               ↓
5 Files      Relationships    Performance
```

### **2. AI Processing Layer**
```
Customer Data → AWS Bedrock → Enhanced Insights
     ↓              ↓              ↓
Complete      Claude 3 Sonnet   Classifications
Profiles      AI Analysis       & Priorities
```

### **3. Business Logic Layer**
```
AI Insights → Value Seekers Filter → Targeted Notifications
     ↓              ↓                      ↓
Enhanced      Cost Optimization      Personalized
Data          75% Reduction          Messages
```

### **4. Presentation Layer**
```
Flask App → Web Dashboard → Agent Interface
     ↓           ↓              ↓
REST APIs   Interactive UI   Workflow Tools
```

---

## 🎯 Key System Features

### **🤖 AI-Powered Intelligence**
- **Customer Segmentation**: Automatic classification into 4 segments
- **Priority Analysis**: Risk scoring and urgency assessment
- **Message Generation**: Personalized British English communications
- **Trigger Identification**: Specific data points requiring action

### **💰 Cost Optimization**
- **Targeted Processing**: Focus on Value Seekers only (~25% of customers)
- **Efficient AI Usage**: ~£0.50-1.00 per 1000 notifications
- **Smart Filtering**: Reduces processing by 75%
- **ROI Maximization**: Higher conversion rates through targeting

### **🎨 User Experience**
- **Single Page Dashboard**: Streamlined interface
- **Collapsible Sections**: Information on demand
- **Editable Messages**: Agent customization capability
- **Real-time Updates**: Dynamic statistics and filtering

### **⚡ Performance Features**
- **Database Optimization**: Indexed foreign keys
- **Efficient Queries**: Multi-table joins optimized
- **Scalable Architecture**: Handles thousands of customers
- **Fast Response Times**: Sub-second query performance

---

## 📊 Data Flow Process

### **Phase 1: Data Preparation**
1. **CSV Import** → 5 source files loaded into SQLite
2. **Schema Creation** → Tables with relationships and indexes
3. **Data Validation** → Integrity checks and constraints

### **Phase 2: AI Enhancement**
1. **Profile Assembly** → Multi-table customer profiles
2. **AI Classification** → AWS Bedrock customer segmentation
3. **Segment Storage** → Enhanced data back to database

### **Phase 3: Smart Analysis**
1. **Value Seekers Filter** → Target segment identification
2. **AI Priority Analysis** → Risk scoring and prioritization
3. **Message Generation** → Personalized communications

### **Phase 4: User Interaction**
1. **Dashboard Display** → Priority-ordered customer list
2. **Agent Review** → Expandable insights and details
3. **Message Editing** → Customization of AI-generated content
4. **Notification Sending** → Targeted customer engagement

---

## 🔄 System Integration Points

### **External Services**
- **AWS Bedrock**: AI analysis and message generation
- **SQLite**: Local database for fast queries
- **Flask**: Web framework for dashboard
- **CSV Files**: Data source integration

### **Internal Components**
- **Database Manager**: Data access and relationships
- **AI Classifier**: Customer segmentation logic
- **Notification Generator**: Message creation and prioritization
- **Web Dashboard**: User interface and interaction

---

## 🚀 Deployment Architecture

```
Development Environment:
┌─────────────────────────────────────────────────────────┐
│  Local Machine                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Flask     │  │   SQLite    │  │ AWS Bedrock │     │
│  │   Server    │  │  Database   │  │   (Cloud)   │     │
│  │ Port: 5000  │  │    Local    │  │   AI API    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘

Production Scaling Options:
┌─────────────────────────────────────────────────────────┐
│  Cloud Deployment                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Web App   │  │  Database   │  │ AWS Bedrock │     │
│  │  (Scalable) │  │ (PostgreSQL)│  │  (Managed)  │     │
│  │ Load Balanced│  │  Clustered  │  │   Service   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 System Benefits

### **For Business**
- **Targeted Engagement**: Focus on high-value Value Seekers segment
- **Cost Efficiency**: 75% reduction in AI processing costs
- **Proactive Service**: Identify issues before they escalate
- **Data-Driven Decisions**: AI-powered customer insights

### **For Agents**
- **Prioritized Workflow**: Most critical customers first
- **Complete Context**: 360° customer view from all data sources
- **Guided Communication**: AI-suggested messages and approaches
- **Efficient Interface**: Streamlined, single-page dashboard

### **For Customers**
- **Personalized Service**: Tailored communications and offers
- **Proactive Support**: Issues addressed before they become problems
- **Relevant Messaging**: British English, appropriate tone
- **Timely Intervention**: Right message at the right time

This architecture enables ScottishPower to deliver targeted, AI-powered customer engagement while optimizing costs and maximizing agent efficiency.