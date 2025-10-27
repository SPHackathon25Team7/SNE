import boto3
import json

def test_bedrock_connection():
    try:
        # Initialize Bedrock client
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with a simple prompt
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello in a friendly way"
                }
            ]
        })
        
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        message = response_body['content'][0]['text']
        
        print("✅ SUCCESS! Bedrock is working!")
        print(f"Claude says: {message}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_bedrock_connection()
