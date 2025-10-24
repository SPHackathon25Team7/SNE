# AWS Bedrock Setup for Smart Notification Engine

## Prerequisites

1. **AWS Account**: You need an active AWS account
2. **AWS CLI**: Install and configure AWS CLI with your credentials
3. **Bedrock Access**: Request access to Claude 3 Sonnet model in AWS Bedrock

## Setup Steps

### 1. Install AWS CLI
```bash
# Windows
curl "https://awscli.amazonaws.com/AWSCLIV2.msi" -o "AWSCLIV2.msi"
msiexec /i AWSCLIV2.msi

# Or use pip
pip install awscli
```

### 2. Configure AWS Credentials
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., us-east-1)
- Default output format (json)

### 3. Request Bedrock Model Access

1. Go to AWS Console → Bedrock → Model Access
2. Request access to "Claude 3 Sonnet" model
3. Wait for approval (usually instant for Claude models)

### 4. Environment Variables (Optional)
Create a `.env` file in your project root:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### 5. Test Bedrock Connection
```python
import boto3

try:
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    print("✅ Bedrock client initialized successfully")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Features Added

### AI-Powered Notifications
- **Personalized Messages**: Each notification is tailored to customer segment and behavior
- **Context-Aware**: Uses customer energy usage, solar/EV ownership, and region data
- **Multiple Types**: Billing alerts, energy saving tips, engagement campaigns, Value Seeker offers

### Notification Types
1. **Billing Alerts**: Empathetic, professional messages for billing issues
2. **Energy Saving**: Personalized tips based on usage patterns and green tech ownership
3. **Engagement**: Re-engagement messages tailored to customer segment values
4. **Value Seeker Specials**: Cost-focused offers for your target segment

### Fallback System
- If Bedrock is unavailable, the system uses pre-written fallback messages
- Ensures notifications are always generated, even without AI

## Cost Considerations

- Claude 3 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Each notification uses ~100-200 tokens
- For 1000 notifications: approximately $0.50-$1.00

## Security Best Practices

1. Use IAM roles with minimal required permissions
2. Enable CloudTrail for API logging
3. Rotate access keys regularly
4. Use VPC endpoints for private connectivity (production)

## Troubleshooting

### Common Issues:
1. **Model Access Denied**: Request access in Bedrock console
2. **Region Issues**: Ensure Bedrock is available in your region
3. **Credentials**: Verify AWS credentials are properly configured
4. **Rate Limits**: Implement retry logic for production use

### Testing Without Bedrock:
The app will work without Bedrock setup - it will use fallback messages and show a warning in the console.