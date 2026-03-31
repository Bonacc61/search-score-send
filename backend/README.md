# Search-Score-Send Backend API

FastAPI backend for the Search-Score-Send recruitment automation system.

## 🚀 Features

- **AI-Powered JD Extraction**: Claude Sonnet 4 extracts structured requirements from raw job descriptions
- **Multi-Platform Search**: Parallel search across LinkedIn, GitHub, and Stack Overflow
- **GDPR-Compliant Scoring**: Anonymization layer before AI scoring (zero PII to Claude)
- **Personalized Messaging**: No templates - truly personalized outreach based on actual experience
- **Human-in-the-Loop (HITL)**: EU AI Act compliance with mandatory human review gates
- **Real-Time Progress**: Server-Sent Events (SSE) for live workflow updates
- **Audit Logging**: Complete compliance trail for GDPR and EU AI Act

## 📋 Prerequisites

- Python 3.11+
- Anthropic API key (Claude Sonnet 4)
- n8n instance (local or cloud)
- Optional: Redis (for SSE and task queue)

## 🛠️ Installation

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required environment variables:**

```env
# Claude AI
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database Encryption
DATABASE_ENCRYPTION_KEY=your-32-byte-key-here  # Generate with: openssl rand -hex 32

# Email (for HITL notifications)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Reviewer
DEFAULT_REVIEWER_EMAIL=recruiter@company.com

# Security
SECRET_KEY=your-secret-key  # Generate with: openssl rand -hex 32
```

### 3. Create Data Directories

```bash
mkdir -p data logs
```

### 4. Run Database Migrations

```bash
# Database tables are auto-created on first run
# Or manually:
python -c "from api.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

## 🚦 Running the API

### Development Mode

```bash
# From backend/ directory
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using uvicorn directly
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn with uvicorn workers
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```bash
# Build image
docker build -t search-score-send-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  --name search-score-send-api \
  search-score-send-api
```

## 📡 API Endpoints

### Health & Status

```bash
# Health check
GET /

# Detailed health
GET /api/health
```

### Job Description

```bash
# Extract structured requirements from JD
POST /api/jd/extract
Content-Type: application/json

{
  "raw_text": "Senior Python Engineer with 5+ years..."
}
```

### Search

```bash
# Search LinkedIn
POST /api/search/linkedin
{
  "query": "Python AND Django AND (Amsterdam OR Remote)",
  "limit": 20,
  "execution_id": "exec_123"
}

# Search GitHub
POST /api/search/github
{
  "query": "language:python location:amsterdam followers:>100",
  "limit": 20,
  "execution_id": "exec_123"
}

# Search Stack Overflow
POST /api/search/stackoverflow
{
  "query": "[python] OR [django] location:amsterdam",
  "limit": 20,
  "execution_id": "exec_123"
}
```

### Scoring

```bash
# Score candidates in batch
POST /api/scoring/batch
{
  "candidates": [...],
  "job_requirements": {...},
  "threshold": 80.0,
  "execution_id": "exec_123"
}
```

### Messages

```bash
# Generate personalized messages
POST /api/messages/generate-batch
{
  "qualified_candidates": [...],
  "job": {...},
  "execution_id": "exec_123"
}
```

### HITL (Human-in-the-Loop)

```bash
# Create approval request
POST /api/hitl/create-approval-request
{
  "workflow_id": "workflow_123",
  "execution_id": "exec_123",
  "stage": "jd_review",
  "data": {...},
  "reviewer_email": "recruiter@company.com"
}

# Submit approval decision
POST /api/hitl/submit-decision/{approval_id}
{
  "approval_id": "approval_123",
  "status": "approved",
  "approved_data": {...}
}

# Get approval details
GET /api/hitl/approval/{approval_id}
```

### Progress (Real-Time Updates)

```bash
# Server-Sent Events stream (frontend connects to this)
GET /api/progress/stream/{execution_id}
Accept: text/event-stream

# Post progress update (called by n8n workflow)
POST /api/progress/update
{
  "execution_id": "exec_123",
  "stage": "searching",
  "message": "Searching across platforms...",
  "progress_percent": 30
}
```

## 🔒 GDPR & Compliance

### Anonymization Layer

All candidate data is anonymized before being sent to Claude API:

```python
# ❌ Never sent to Claude API:
- name
- email
- profile_url

# ✅ Only anonymized data sent:
- skills (list)
- headline (text)
- experience_years (number)
- location (text)
- anonymized_id (UUID)
```

### Data Retention

- Default: 180 days
- Configurable via `DATA_RETENTION_DAYS`
- Auto-deletion via scheduled cleanup job (TODO)

### Audit Logging

All operations are logged for compliance:
- Who did what, when
- Data access and modifications
- AI decisions and human approvals
- GDPR data subject requests

### EU AI Act Compliance

- **High-Risk AI System**: Recruitment decisions
- **Human-in-the-Loop**: Mandatory review at 2 stages
  1. JD Review (60 min timeout)
  2. Final Review (24 hr timeout)
- **Transparency**: Explainable scoring with evidence
- **Right to Explanation**: Scoring criteria visible to candidates

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=api --cov-report=html

# Specific test file
pytest tests/test_jd_extraction.py -v
```

## 📊 Monitoring

### Logs

```bash
# View API logs
tail -f logs/api.log

# Search for errors
grep ERROR logs/api.log
```

### Database

```bash
# SQLite CLI
sqlite3 data/search_score_send.db

# Check execution stats
SELECT execution_id, status, candidates_found, candidates_qualified
FROM workflow_executions
ORDER BY started_at DESC
LIMIT 10;
```

## 🔧 Development

### Code Quality

```bash
# Format code
black api/

# Lint
ruff check api/

# Type check
mypy api/
```

### Adding New Endpoints

1. Create router in `api/routers/`
2. Add models to `api/models.py`
3. Include router in `api/main.py`
4. Add tests in `tests/`

## 🐛 Troubleshooting

### Claude API Errors

```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Test API connection
python -c "import anthropic; print(anthropic.AsyncAnthropic(api_key='$ANTHROPIC_API_KEY'))"
```

### Database Locked

```bash
# SQLite is single-writer
# If you see "database is locked" errors:
# 1. Close all connections
# 2. Consider upgrading to PostgreSQL for production
```

### SSE Not Working

```bash
# Check Redis is running (if using Redis backend)
redis-cli ping

# Check SSE connections
curl -N http://localhost:8000/api/progress/stream/test_123
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Next Steps

1. **Integrate Real Search APIs**
   - Replace mock data in `api/routers/search.py`
   - Add LinkedIn Recruiter API
   - Add GitHub Search API
   - Add Stack Overflow API

2. **Add Email Notifications**
   - HITL approval requests
   - Workflow completion
   - Error alerts

3. **Production Database**
   - Migrate from SQLite to PostgreSQL
   - Add connection pooling
   - Configure backups

4. **Caching & Performance**
   - Add Redis for SSE
   - Cache JD extractions
   - Rate limiting

5. **Security Enhancements**
   - Add authentication middleware
   - API key management
   - Rate limiting per user

## 📄 License

MIT License - See LICENSE file for details
