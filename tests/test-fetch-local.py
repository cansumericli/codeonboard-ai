import json
import sys
import os

# Add the lambda function folder to the Python path so we can import it
sys.path.insert(0, 'lambda-functions/fetch-repo')

# Set the environment variable (S3 bucket name)
os.environ['BUCKET_NAME'] = 'codeonboard-ai-repos'

# Import the Lambda handler
from lambda_function import lambda_handler

# Load the test input event
with open('tests/test-fetch-input.json', 'r') as f:
    event = json.load(f)

print("🧪 Testing fetch-repo lambda locally...")
print(f"Input: {event}")
print()

# Run the Lambda function locally
result = lambda_handler(event, None)

print()
print("Result:")
print(json.dumps(result, indent=2))

# If the Lambda ran successfully, check S3 for uploaded files
if result['statusCode'] == 200:
    import boto3
    s3 = boto3.client('s3')
    
    body = json.loads(result['body'])
    repo_id = body['repoId']
    
    print(f"\nChecking S3 for files from {repo_id}...")
    
    try:
        response = s3.list_objects_v2(
            Bucket='codeonboard-ai-repos',
            Prefix=repo_id,
            MaxKeys=5
        )
        
        if 'Contents' in response:
            print(f"Found {response['KeyCount']} files (showing first 5):")
            for obj in response['Contents'][:5]:
                print(f"   - {obj['Key']}")
        else:
            print("No files found in S3")
    except Exception as e:
        print(f"Error checking S3: {e}")
else:
    print("Lambda returned an error")
