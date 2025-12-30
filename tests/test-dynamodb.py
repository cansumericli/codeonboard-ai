import boto3
import sys

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('CodeFiles')

print("Testing DynamoDB operations...")

# TEST 1: PUT (Write an item)
try:
    table.put_item(
        Item={
            'repoId': 'test_repo',
            'filePath': 'test/sample.js',
            'fileContent': 'console.log("Hello from DynamoDB test!");',
            'language': 'javascript',
            'fileSize': 45
        }
    )
    print("✅ PUT operation successful")
except Exception as e:
    print(f"❌ PUT failed: {e}")
    sys.exit(1)

# TEST 2: GET (Read the item)
try:
    response = table.get_item(
        Key={
            'repoId': 'test_repo',
            'filePath': 'test/sample.js'
        }
    )
    
    if 'Item' in response:
        item = response['Item']
        print(f"✅ GET operation successful")
        print(f"   Retrieved: {item['fileContent']}")
    else:
        print("❌ GET failed: Item not found")
        sys.exit(1)
except Exception as e:
    print(f"❌ GET failed: {e}")
    sys.exit(1)

# TEST 3: DELETE (Remove the item)
try:
    table.delete_item(
        Key={
            'repoId': 'test_repo',
            'filePath': 'test/sample.js'
        }
    )
    print("✅ DELETE operation successful")
except Exception as e:
    print(f"❌ DELETE failed: {e}")
    sys.exit(1)

print("\n🎉 All DynamoDB tests passed!")
