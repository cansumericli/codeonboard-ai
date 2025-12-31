import boto3
import json
import sys

# Connect to Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

print("Testing Bedrock Titan Embeddings...")

# TEST: Generate embeddings
try:
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({
            "inputText": "Hello world, this is a test!"
        })
    )
    
    # Parse response
    result = json.loads(response['body'].read())
    embedding = result['embedding']
    
    print(f"✅ Embedding generated successfully!")
    print(f"   Dimensions: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Verify it's correct
    if len(embedding) == 1536:
        print("✅ Embedding has correct dimensions (1536)")
    else:
        print(f"❌ Wrong dimensions: {len(embedding)}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Bedrock test failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if you enabled 'Amazon Titan Embeddings' in Bedrock console")
    print("2. Wait 5 minutes after enabling and try again")
    print("3. Make sure you're using region us-east-1")
    sys.exit(1)

print("\n🎉 Bedrock test passed!")