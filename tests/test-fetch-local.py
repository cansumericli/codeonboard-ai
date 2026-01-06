import json
import sys
import os

# Lambda fonksiyonunu import edebilmek için path'e ekle
sys.path.insert(0, 'lambda-functions/fetch-repo')

# Environment variable ayarla (S3 bucket adı)
os.environ['BUCKET_NAME'] = 'codeonboard-ai-repos'

# Lambda fonksiyonunu import et
from lambda_function import lambda_handler

# Test input'unu yükle
with open('tests/test-fetch-input.json', 'r') as f:
    event = json.load(f)

print("🧪 Testing fetch-repo lambda locally...")
print(f"Input: {event}")
print()

# Lambda'yı çalıştır
result = lambda_handler(event, None)

print()
print("Result:")
print(json.dumps(result, indent=2))

# Eğer başarılıysa S3'ü kontrol et
if result['statusCode'] == 200:
    import boto3
    s3 = boto3.client('s3')
    
    body = json.loads(result['body'])
    repo_id = body['repoId']
    
    print(f"\n📂 Checking S3 for files from {repo_id}...")
    
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
    print("Lambda returned error")
