# Search-Score-Send Workflow Deployment Guide

**Workflow File:** `search-score-send-workflow.json`
**Created:** 2026-03-30
**Version:** 1.0

---

## 📋 Overview

This guide shows how to deploy the Search-Score-Send n8n workflow to your n8n instance.

### Workflow Summary

**Name:** Search-Score-Send Recruitment Automation

**Purpose:** Automate the complete recruitment pipeline from job description to personalized outreach messages

**Execution Time:** < 5 minutes end-to-end

**Components:**
1. Webhook Trigger (accepts job description)
2. JD Extraction (Claude API)
3. Parallel Search (LinkedIn + GitHub + Stack Overflow)
4. Merge & Deduplicate
5. Batch Scoring (Claude API + GDPR)
6. Filter 80%+ matches
7. Generate Messages (Claude API)
8. Respond to Webhook

---

## 🚀 Quick Deployment

### Option 1: Import via n8n UI (Recommended)

1. **Start n8n:**
   ```bash
   docker run -d \
     --name n8n \
     -p 5678:5678 \
     -e N8N_BASIC_AUTH_ACTIVE=false \
     -v n8n_data:/home/node/.n8n \
     n8nio/n8n:latest
   ```

2. **Open n8n UI:**
   - Navigate to http://localhost:5678
   - Click "Workflows" → "Import from File"
   - Select `search-score-send-workflow.json`
   - Click "Import"

3. **Configure Environment Variables:**
   - Click "Settings" → "Variables"
   - Add the following:
     - `API_URL`: Your backend API URL (e.g., `http://localhost:3000`)
     - `FRONTEND_URL`: Your frontend URL (e.g., `http://localhost:3001`)

4. **Activate Workflow:**
   - Click "Active" toggle in top right
   - Copy the Webhook URL (e.g., `http://localhost:5678/webhook/search-score-send`)

---

### Option 2: Import via n8n API

```bash
# Set environment variables
export N8N_URL="http://localhost:5678"
export N8N_API_KEY="your-api-key"  # Get from n8n Settings → API

# Import workflow
curl -X POST "${N8N_URL}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @search-score-send-workflow.json

# Activate workflow
WORKFLOW_ID=$(curl -s "${N8N_URL}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" | jq -r '.data[] | select(.name=="Search-Score-Send Recruitment Automation") | .id')

curl -X PATCH "${N8N_URL}/api/v1/workflows/${WORKFLOW_ID}" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"active": true}'
```

---

## ⚙️ Configuration

### Required Environment Variables

Set these in n8n Settings → Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_URL` | Backend API endpoint | `http://localhost:3000` |
| `FRONTEND_URL` | Frontend dashboard URL | `http://localhost:3001` |

### Optional Configuration

You can customize these by editing the workflow:

| Setting | Default | Location |
|---------|---------|----------|
| Webhook path | `/search-score-send` | Webhook Trigger node |
| Score threshold | 80 | Filter Qualified node |
| Max candidates | 50 | Input payload |
| Search timeout | 120s | Search nodes |
| Scoring timeout | 180s | Batch Scoring node |
| Message timeout | 60s | Message Generation node |

---

## 🧪 Testing the Workflow

### Test via curl

```bash
# Set webhook URL (get from n8n UI after import)
WEBHOOK_URL="http://localhost:5678/webhook/search-score-send"

# Send test request
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "jobDescription": "Senior Rust Engineer with 5+ years experience in distributed systems. Must have expertise in Tokio async runtime, PostgreSQL, and microservices architecture. Location: Amsterdam or Remote EU. Salary: €70-95K.",
    "maxCandidates": 10,
    "scoreThreshold": 80,
    "callbackUrl": "http://localhost:3000/api/webhooks/progress"
  }'
```

### Expected Response

```json
{
  "workflow_id": "workflow-uuid",
  "execution_id": "execution-uuid",
  "status": "completed",
  "candidates_found": 9,
  "candidates_scored": 9,
  "candidates_qualified": 3,
  "review_url": "http://localhost:3001/workflows/execution-uuid/review",
  "estimated_duration": "5 minutes",
  "timestamp": "2026-03-30T22:00:00.000Z"
}
```

---

## 🔗 Backend API Requirements

The workflow expects your backend API to have these endpoints:

### 1. JD Extraction

**Endpoint:** `POST /api/jd/extract`

**Request:**
```json
{
  "raw_text": "Job description text..."
}
```

**Response:**
```json
{
  "title": "Senior Rust Engineer",
  "seniority": "Senior",
  "must_have_skills": ["Rust", "Distributed Systems"],
  "search_boolean": {
    "linkedin": "(Rust OR Tokio) AND ...",
    "github": "language:rust stars:>10",
    "stackoverflow": "[rust] score:50"
  }
}
```

---

### 2. LinkedIn Search

**Endpoint:** `POST /api/search/linkedin`

**Request:**
```json
{
  "query": "(Rust OR Tokio) AND ...",
  "limit": 17
}
```

**Response:**
```json
[
  {
    "name": "Sarah van der Berg",
    "email": "sarah@example.com",
    "current_company": "Coolblue",
    "current_role": "Senior Backend Engineer",
    "location": "Amsterdam",
    "profile_url": "https://linkedin.com/in/...",
    "skills": ["Rust", "Distributed Systems"],
    "years_experience": 6
  }
]
```

---

### 3. GitHub Search

**Endpoint:** `POST /api/search/github`

**Request:**
```json
{
  "query": "language:rust stars:>10",
  "limit": 17
}
```

**Response:**
```json
[
  {
    "username": "sarah-rust",
    "email": "sarah@example.com",
    "repositories": [
      {
        "name": "tokio-cache",
        "stars": 125,
        "language": "Rust"
      }
    ],
    "contributions": 1250
  }
]
```

---

### 4. Stack Overflow Search

**Endpoint:** `POST /api/search/stackoverflow`

**Request:**
```json
{
  "query": "[rust] or [tokio] score:50",
  "limit": 16
}
```

**Response:**
```json
[
  {
    "username": "sarah-dev",
    "email": "sarah@example.com",
    "reputation": 8420,
    "answers": 127,
    "top_tags": ["rust", "tokio", "async"]
  }
]
```

---

### 5. Batch Scoring

**Endpoint:** `POST /api/scoring/batch`

**Request:**
```json
{
  "candidates": [...],  // Array of candidate profiles
  "job_requirements": {...},  // From JD extraction
  "threshold": 80
}
```

**Response:**
```json
{
  "total_candidates": 47,
  "scored": 47,
  "above_threshold": 12,
  "below_threshold": 35,
  "qualified_candidates": [
    {
      "candidate_id": "uuid",
      "overall_score": 87.5,
      "meets_threshold": true,
      "skill_breakdown": [
        {
          "skill": "Rust",
          "required": true,
          "score": 95,
          "evidence": "5 years, 1200 commits"
        }
      ]
    }
  ],
  "rejection_reasons": {
    "too_junior": 15,
    "missing_required_skill": 12,
    "location_mismatch": 8
  }
}
```

---

### 6. Message Generation

**Endpoint:** `POST /api/messages/generate-batch`

**Request:**
```json
{
  "qualified_candidates": [...],  // Candidates scoring 80%+
  "job": {...}  // Job description
}
```

**Response:**
```json
[
  {
    "candidate_id": "uuid",
    "candidate_name": "Sarah van der Berg",
    "overall_score": 87.5,
    "message": {
      "subject": "Your Rust work at Coolblue + our distributed systems challenge",
      "message": "Hi Sarah,\n\nI saw your tokio-based distributed cache...",
      "personalization_points": [
        "Mentioned GitHub project: tokio-cache",
        "Referenced Stack Overflow answer",
        "Connected to tech stack"
      ]
    },
    "review_status": "pending"
  }
]
```

---

## 🔐 Security & Compliance

### GDPR Compliance

The workflow is designed with GDPR compliance in mind:

1. **Zero PII to AI:**
   - The backend's batch scoring endpoint MUST anonymize candidates before sending to Claude
   - Only anonymized data (UUIDs, metrics) sent to AI
   - PII (names, emails) never leaves your infrastructure

2. **Audit Trail:**
   - n8n automatically logs all executions
   - Enable in Settings → Executions → "Save execution data"
   - Retention: Configure based on your GDPR policy (default: 180 days)

3. **Data Encryption:**
   - Use HTTPS for all API calls
   - Encrypt n8n database at rest
   - Use encrypted volumes for n8n data

### EU AI Act Compliance

1. **Human-in-the-Loop:**
   - Workflow outputs to review dashboard
   - Human must approve before sending messages
   - Implemented in frontend, not in n8n workflow

2. **Transparent Scoring:**
   - Skill-by-skill breakdown provided
   - Evidence links included
   - Reasoning documented

---

## 📊 Monitoring & Debugging

### View Executions

1. **n8n UI:**
   - Click "Executions" tab
   - View execution history
   - Click any execution to see data flow

2. **n8n API:**
   ```bash
   curl "${N8N_URL}/api/v1/executions?workflowId=${WORKFLOW_ID}" \
     -H "X-N8N-API-KEY: ${N8N_API_KEY}"
   ```

### Common Issues

#### Issue: Workflow times out

**Cause:** API endpoints taking too long

**Solution:**
- Increase timeout in node settings
- Optimize backend API performance
- Enable caching for search results

#### Issue: No candidates found

**Cause:** Search queries too restrictive

**Solution:**
- Check Boolean queries generated by JD extraction
- Verify search APIs are returning data
- Test search endpoints independently

#### Issue: All candidates rejected

**Cause:** Score threshold too high or requirements too strict

**Solution:**
- Lower threshold from 80% to 70%
- Review rejection reasons in scoring response
- Adjust must-have vs. nice-to-have skills

---

## 🚀 Production Deployment

### Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - WEBHOOK_URL=https://your-domain.com/
      - GENERIC_TIMEZONE=Europe/Amsterdam
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      - EXECUTIONS_DATA_SAVE_ON_MANUAL_SUCCESS=true
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

**Deploy:**

```bash
# Set environment variables
export N8N_USER="admin"
export N8N_PASSWORD="secure-password"
export N8N_ENCRYPTION_KEY="$(openssl rand -hex 32)"
export POSTGRES_PASSWORD="secure-password"

# Start services
docker-compose up -d

# Import workflow
docker exec -it n8n n8n import:workflow --input=/data/search-score-send-workflow.json
```

---

## 📈 Performance Optimization

### Enable Caching

Add caching to search endpoints:

```python
# backend/api/search.py
from functools import lru_cache

@lru_cache(maxsize=1000)
def search_linkedin(query: str, limit: int):
    # Cache results for 15 minutes
    pass
```

### Parallel Execution

The workflow already uses parallel execution for searches. Ensure your backend API can handle concurrent requests:

```python
# backend/main.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        workers=4  # Enable multiple workers
    )
```

### Database Optimization

Use connection pooling for database queries:

```python
# backend/database/pool.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## 🔄 Workflow Updates

### Version Control

1. **Export current version:**
   ```bash
   curl "${N8N_URL}/api/v1/workflows/${WORKFLOW_ID}" \
     -H "X-N8N-API-KEY: ${N8N_API_KEY}" > workflow-v1.0.json
   ```

2. **Make changes in n8n UI**

3. **Export new version:**
   ```bash
   curl "${N8N_URL}/api/v1/workflows/${WORKFLOW_ID}" \
     -H "X-N8N-API-KEY: ${N8N_API_KEY}" > workflow-v1.1.json
   ```

4. **Commit to git:**
   ```bash
   git add workflow-v1.1.json
   git commit -m "Update workflow: add error handling"
   git push
   ```

---

## 📞 Support

**Issues:**
- Check n8n execution logs
- Review backend API logs
- Test individual nodes
- Verify environment variables

**Resources:**
- n8n Documentation: https://docs.n8n.io
- n8n Community: https://community.n8n.io
- This project: https://github.com/Bonacc61/search-score-send

---

**Workflow ready for deployment! 🚀**
