# CodeOnboard AI - Architecture

## Phase 1: Data Pipeline

### Storage Components

#### 1. S3 Bucket
- **Name**: `codeonboard-repos-cansumericli`
- **Purpose**: Store raw code files from GitHub repositories
- **Region**: us-east-1

#### 2. DynamoDB Table
- **Name**: `CodeFiles`
- **Purpose**: Store code metadata and embeddings for fast search
- **Billing**: Pay-per-request (free tier)

**Schema:**
```
Primary Key:
- repoId (Partition Key): "owner_reponame"
- filePath (Sort Key): "src/index.js"

Attributes:
- fileContent: Actual code text
- embedding: [1536 decimal numbers from Bedrock Titan]
- language: "javascript", "python", etc.
- fileSize: Bytes
```

#### 3. AWS Bedrock
- **Titan Embeddings**: Convert code/text → 1536-dimensional vectors
- **Claude 3.5 Sonnet**: Generate answers (Phase 2)
- **Region**: us-east-1

### Data Flow (Phase 1 - Current)
```
GitHub Repo
    ↓
Lambda: fetch-repo (Day 3-4) ← TODO
    ↓
S3 Bucket (raw code files)
    ↓ (S3 trigger)
Lambda: generate-embeddings (Day 5-6) ← TODO
    ↓
Bedrock Titan (create vectors)
    ↓
DynamoDB (store embeddings)
```

### Tests Completed
- ✅ S3 upload/download
- ✅ DynamoDB put/get/delete
- ✅ Bedrock Titan embeddings generation

### Cost So Far
- S3: $0 (free tier)
- DynamoDB: $0 (free tier)
- Bedrock: ~$0.01 (test embeddings)
- **Total**: < $0.01
