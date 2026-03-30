# Complete Search-Score-Send System Guide

**For: Work Laptop Implementation**
**Date:** 2026-03-30
**Status:** Ready for Development

---

## 📋 Quick Links to Documents

All documentation is saved in `/root/NanoClaw/n8n/` on the server:

1. **SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md** (50+ pages)
   - Complete technical specification
   - Database schema
   - Full code examples (Python backend, React frontend)
   - 8-week roadmap
   - Cost analysis & ROI

2. **N8N-INTEGRATION-GUIDE.md** (Integration documentation)
   - n8n-MCP setup instructions
   - Claude Code configuration
   - API integration examples
   - Deployment options

3. **n8n-mcp/** (Cloned repository)
   - Source: https://github.com/czlonkowski/n8n-mcp
   - Pre-built MCP server for n8n workflow management
   - 1,396 n8n nodes documented
   - 2,709 workflow templates available

---

## 🚀 System Overview

### The Three-Step Workflow

**Problem:** Traditional recruiting takes 2 hours per search (manual Boolean queries, gut-feel scoring, template messages)

**Solution:** Search-Score-Send automates it in 5 minutes (95% time reduction)

```
Step 1: JD Reader (Search) - 2 minutes
├─ Paste job description into form
├─ AI extracts requirements automatically
├─ Generates Boolean queries (LinkedIn, GitHub, Stack Overflow)
├─ Parallel search finds 50 candidates
└─ No manual query construction needed

Step 2: Fit Filter (Qualification) - 3 minutes
├─ AI scores each candidate (0-100%)
├─ Skill-by-skill breakdown with evidence
├─ Only 80%+ matches proceed
├─ Transparent reasoning (EU AI Act compliant)
└─ GDPR-safe (zero PII to Claude)

Step 3: Personal Opener (Outreach) - 1 minute
├─ Generates personalized message per candidate
├─ References their actual GitHub projects
├─ Mentions specific Stack Overflow answers
├─ Connects experience to job challenges
└─ Not [FIRST NAME] or templates
```

**Total Time:** 5 minutes (vs. 2 hours manual)

---

## 🏗️ Architecture

### High-Level Components

```
┌──────────────────────────────────────────────────────┐
│              Frontend (Next.js)                      │
│  • Job description input form                        │
│  • Real-time progress tracking (SSE)                 │
│  • Candidate review dashboard                        │
│  • Message editing & approval                        │
└───────────────────┬──────────────────────────────────┘
                    │ HTTP/REST
                    ↓
┌──────────────────────────────────────────────────────┐
│              Backend (FastAPI Python)                │
│  ┌────────────────────────────────────────────────┐ │
│  │ JD Extraction Engine (Claude API)              │ │
│  │ • Parses job description                        │ │
│  │ • Extracts must-have/nice-to-have skills       │ │
│  │ • Generates Boolean queries per platform        │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │ Unified Search Coordinator                      │ │
│  │ • LinkedIn Agent (parallel)                     │ │
│  │ • GitHub Agent (parallel)                       │ │
│  │ • Stack Overflow Agent (parallel)               │ │
│  │ • Deduplication (HMAC-based)                    │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │ Fit Scoring Engine (Claude API)                │ │
│  │ • Anonymizes candidates (GDPR)                  │ │
│  │ • Scores 0-100% per skill                       │ │
│  │ • Filters 80%+ matches                          │ │
│  │ • Categorizes rejections                        │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │ Message Generator (Claude API)                  │ │
│  │ • Generates personalized messages               │ │
│  │ • References actual projects                    │ │
│  │ • Extracts personalization points               │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │ Database (SQLite + SQLCipher)                   │ │
│  │ • Dual encryption (AES-256 + Fernet)           │ │
│  │ • GDPR audit trail                              │ │
│  │ • 180-day auto-deletion                         │ │
│  └────────────────────────────────────────────────┘ │
└───────────────────┬──────────────────────────────────┘
                    │ Webhook Trigger
                    ↓
┌──────────────────────────────────────────────────────┐
│              n8n Workflow Engine (Optional)          │
│  • Visual workflow orchestration                     │
│  • Parallel execution                                │
│  • Error handling & retries                          │
│  • Real-time progress webhooks                       │
│  • Easy to modify without code changes               │
└──────────────────────────────────────────────────────┘
```

### Existing Infrastructure (Reuse from Olórin)

**You already have 70% of the infrastructure built!**

Located in `/root/olorin/`:

```
✅ GDPR Anonymization Layer
   • /root/olorin/anonymization-system/
   • Zero-PII architecture
   • Dual encryption (SQLCipher + Fernet)
   • Automated DSAR handling

✅ AI Scoring Engine
   • /root/olorin/backend/scoring/
   • Claude-based evaluation
   • Structured reasoning
   • Audit trail

✅ Database Models
   • /root/olorin/backend/database/
   • SQLite with encryption
   • Schema already designed

✅ HITL Dashboard
   • /root/olorin/frontend/
   • Human approval gates
   • Next.js + Tailwind
   • Real-time updates

✅ Sourcing Engine
   • /root/olorin/sourcing_engine/
   • GitHub agent
   • LinkedIn agent
   • Stack Overflow agent
```

**What's New (30% to build):**

```
🆕 JD Extraction Engine
   • Claude-based parsing
   • Boolean query generation
   • ~500 lines Python

🆕 Unified Search API
   • Parallel coordinator
   • Deduplication
   • ~300 lines Python

🆕 Message Generator
   • Personalization extractor
   • Batch processing
   • ~400 lines Python

🆕 Frontend Workflow UI
   • Job input form
   • Progress tracking
   • Candidate review
   • ~3 React pages
```

---

## 📊 Database Schema

### New Tables to Add

```sql
-- Job Descriptions
CREATE TABLE job_descriptions (
    id TEXT PRIMARY KEY,                    -- UUID
    raw_text TEXT NOT NULL,                 -- Original paste
    extracted_requirements JSON NOT NULL,   -- Parsed data
    title TEXT NOT NULL,
    seniority TEXT,                        -- Junior/Mid/Senior/Lead
    must_have_skills JSON,                 -- ["Rust", "Distributed Systems"]
    nice_to_have_skills JSON,              -- ["Docker", "K8s"]
    location TEXT,
    remote_policy TEXT,                    -- On-site/Hybrid/Remote
    salary_min INTEGER,
    salary_max INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    status TEXT DEFAULT 'active',
    GDPR_retention_days INTEGER DEFAULT 180
);

-- Search Workflows
CREATE TABLE search_workflows (
    id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES job_descriptions(id),
    status TEXT DEFAULT 'pending',         -- pending/searching/scoring/ready/completed
    search_channels JSON,                  -- ["linkedin", "github", "stackoverflow"]
    candidates_found INTEGER DEFAULT 0,
    candidates_scored INTEGER DEFAULT 0,
    candidates_approved INTEGER DEFAULT 0,
    threshold_score REAL DEFAULT 80.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Extend existing candidates table
ALTER TABLE candidates ADD COLUMN workflow_id TEXT REFERENCES search_workflows(id);
ALTER TABLE candidates ADD COLUMN overall_match_score REAL;
ALTER TABLE candidates ADD COLUMN match_breakdown JSON;

-- Outreach Messages
CREATE TABLE outreach_messages (
    id TEXT PRIMARY KEY,
    candidate_id TEXT REFERENCES candidates(id),
    job_id TEXT REFERENCES job_descriptions(id),
    message_text TEXT NOT NULL,
    personalization_data JSON,             -- What was personalized
    review_status TEXT DEFAULT 'pending',  -- pending/approved/edited/rejected
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    sent_at TIMESTAMP,
    channel TEXT,                          -- linkedin/email/whatsapp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 💻 Key Code Examples

### 1. JD Extraction Engine

```python
# backend/services/jd_extractor.py
import anthropic
from typing import Dict
import json

class JDExtractor:
    """Extract structured requirements from job descriptions"""

    def __init__(self):
        self.claude_client = anthropic.Anthropic()

    async def extract_requirements(self, raw_jd: str) -> Dict:
        """
        Use Claude to parse JD into structured format

        Returns:
        {
            "title": "Senior Rust Engineer",
            "seniority": "Senior",
            "must_have_skills": ["Rust", "Distributed Systems", "PostgreSQL"],
            "nice_to_have": ["Docker", "Kubernetes"],
            "years_experience": 5,
            "location": "Amsterdam or Remote EU",
            "remote_policy": "Remote",
            "salary_range": [70000, 95000],
            "search_boolean": {
                "linkedin": "(Rust OR Tokio) AND ...",
                "github": "language:rust stars:>10",
                "stackoverflow": "[rust] or [tokio] score:50"
            }
        }
        """

        prompt = f"""
        Extract structured hiring requirements from this job description.

        Job Description:
        {raw_jd}

        Return JSON with:
        - title, seniority, must_have_skills, nice_to_have
        - years_experience, location, remote_policy, salary_range
        - search_boolean (optimized queries for LinkedIn/GitHub/SO)
        """

        response = await self.claude_client.messages.create(
            model="claude-sonnet-4",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)
```

### 2. Unified Search Coordinator

```python
# backend/services/unified_search.py
import asyncio
from typing import List, Dict

class UnifiedSearchCoordinator:
    """Parallel search across multiple platforms"""

    async def search_all_platforms(
        self,
        search_params: Dict,
        max_results: int = 50
    ) -> List[Dict]:
        """Execute searches in parallel"""

        per_platform = max_results // 3

        # Execute in parallel (2-3x faster)
        results = await asyncio.gather(
            self.linkedin_agent.search(
                search_params["search_boolean"]["linkedin"],
                limit=per_platform
            ),
            self.github_agent.search(
                search_params["search_boolean"]["github"],
                limit=per_platform
            ),
            self.stackoverflow_agent.search(
                search_params["search_boolean"]["stackoverflow"],
                limit=per_platform
            ),
            return_exceptions=True
        )

        # Deduplicate by email/username
        candidates = []
        seen = set()
        for platform_results in results:
            if isinstance(platform_results, Exception):
                continue
            for profile in platform_results:
                profile_id = profile.get("email") or profile.get("username")
                if profile_id not in seen:
                    seen.add(profile_id)
                    candidates.append(profile)

        return candidates[:max_results]
```

### 3. Fit Scoring Engine

```python
# backend/scoring/fit_scorer.py
from backend.anonymization.anonymizer import Anonymizer
from backend.scoring.ai_scorer import AIScorer

class FitScorer:
    """Score candidates against job requirements"""

    async def score_candidate_fit(
        self,
        candidate_profile: Dict,
        job_requirements: Dict,
        threshold: float = 80.0
    ) -> Dict:
        """
        Returns:
        {
            "candidate_id": "uuid",
            "overall_score": 87.5,
            "meets_threshold": True,
            "skill_breakdown": [
                {
                    "skill": "Rust",
                    "required": True,
                    "score": 95,
                    "evidence": "5 years Rust, 1200 commits",
                    "reasoning": "Strong expertise..."
                }
            ],
            "seniority_match": {
                "required": "Senior",
                "assessed": "Senior",
                "score": 90
            }
        }
        """

        # Step 1: Anonymize (GDPR)
        anonymous = await self.anonymizer.anonymize(candidate_profile)

        # Step 2: Score with Claude
        evaluation = await self.ai_scorer.score(
            anonymous,
            job_requirements
        )

        # Step 3: Calculate overall score
        evaluation["overall_score"] = self._calculate_overall(evaluation)
        evaluation["meets_threshold"] = evaluation["overall_score"] >= threshold

        return evaluation
```

### 4. Message Generator

```python
# backend/services/message_generator.py
class PersonalizedMessageGenerator:
    """Generate tailored outreach messages (NOT templates)"""

    async def generate_message(
        self,
        candidate: Dict,      # With PII (approved only)
        job: Dict,
        evaluation: Dict
    ) -> Dict:
        """
        Returns:
        {
            "subject": "Your Rust work at [Company]...",
            "message": "Hi Sarah,\n\nI saw your tokio cache...",
            "personalization_points": [
                "Mentioned GitHub project",
                "Referenced Stack Overflow answer",
                "Connected to tech stack"
            ]
        }
        """

        prompt = f"""
        Write a personalized LinkedIn message.

        CANDIDATE: {candidate["name"]} at {candidate["current_company"]}
        PROJECTS: {candidate["notable_projects"]}
        JOB: {job["title"]} at {job["company_name"]}

        INSTRUCTIONS:
        1. Use their ACTUAL name (not [FIRST NAME])
        2. Reference SPECIFIC projects from their profile
        3. Connect experience to our challenges
        4. Keep under 150 words
        5. Natural, conversational tone
        6. NO templates or placeholders
        """

        response = await self.claude_client.messages.create(
            model="claude-sonnet-4",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        message_data = json.loads(response.content[0].text)
        message_data["personalization_points"] = self._extract_personalization(
            message_data["message"],
            candidate
        )

        return message_data
```

---

## 🗺️ Implementation Roadmap (8 Weeks)

### Phase 0: Setup (Week 1)
**Duration:** 3-5 days

Tasks:
- [ ] Install n8n-MCP on work laptop
- [ ] Extend Olórin database schema
- [ ] Set up development environment
- [ ] GDPR compliance review with legal

Exit Criteria:
- ✅ n8n-MCP accessible at localhost
- ✅ Database migrations applied
- ✅ All existing tests passing
- ✅ Legal sign-off

---

### Phase 1: JD Reader (Week 2)
**Duration:** 5-7 days

Files to Create:
```
backend/services/jd_extractor.py          # JD parsing
backend/services/requirements_parser.py   # Requirement extraction
backend/services/query_generator.py       # Boolean queries
backend/api/jd_routes.py                  # API endpoints
frontend/app/jobs/new/page.tsx            # Input form
tests/test_jd_extractor.py                # Tests
```

Exit Criteria:
- ✅ 90%+ extraction accuracy
- ✅ Boolean queries work on all platforms
- ✅ Frontend form allows editing
- ✅ API response time < 3 seconds

---

### Phase 2: Unified Search (Week 3)
**Duration:** 7-10 days

Files to Create:
```
backend/services/unified_search.py        # Coordinator
sourcing_engine/linkedin_agent.py         # Adapt existing
sourcing_engine/github_agent.py           # Adapt existing
sourcing_engine/stackoverflow_agent.py    # Adapt existing
backend/services/deduplicator.py          # HMAC dedup
backend/services/workflow_tracker.py      # Progress
tests/test_unified_search.py              # Tests
```

Exit Criteria:
- ✅ Finds 50 candidates in < 2 minutes
- ✅ Zero duplicates
- ✅ Progress updates every 5 seconds
- ✅ Works with n8n parallel execution

---

### Phase 3: Fit Filter (Week 4-5)
**Duration:** 10-12 days

Files to Create:
```
backend/scoring/fit_scorer.py             # Scoring engine
backend/services/batch_scorer.py          # Batch processing
backend/services/rejection_analyzer.py    # Categorization
frontend/app/workflows/[id]/review/page.tsx  # Review UI
frontend/components/ScoreBreakdown.tsx    # Score display
tests/test_fit_scorer.py                  # Tests
```

Exit Criteria:
- ✅ 85%+ scoring accuracy vs. human
- ✅ 50 candidates scored in < 3 minutes
- ✅ GDPR compliant (zero PII to Claude)
- ✅ EU AI Act compliant (structured explanations)

---

### Phase 4: Personal Opener (Week 6)
**Duration:** 5-7 days

Files to Create:
```
backend/services/message_generator.py     # Message gen
backend/services/personalization_extractor.py  # Evidence
backend/services/batch_message_generator.py    # Batch
frontend/components/MessageReview.tsx     # Review UI
backend/services/message_approval.py      # HITL
tests/test_message_generator.py           # Tests
```

Exit Criteria:
- ✅ Zero template messages
- ✅ 100% include project mentions
- ✅ Human review required
- ✅ Editable inline in UI

---

### Phase 5: Integration (Week 7)
**Duration:** 5-7 days

Tasks:
- [ ] Wire all components together
- [ ] Add WebSocket real-time updates
- [ ] Implement error handling & retries
- [ ] Create monitoring dashboard
- [ ] Complete GDPR audit trail

Exit Criteria:
- ✅ Full workflow completes in < 5 minutes
- ✅ 95%+ success rate (no crashes)
- ✅ Real-time progress visible
- ✅ Complete audit trail logged

---

### Phase 6: Polish & Launch (Week 8)
**Duration:** 5 days

Tasks:
- [ ] User testing with 5 recruiters
- [ ] Write documentation & video
- [ ] Performance optimization
- [ ] Legal final review
- [ ] Production deployment

Exit Criteria:
- ✅ User satisfaction: 8/10+
- ✅ Legal approval for production
- ✅ Performance targets met
- ✅ Documentation complete

---

## 💰 Cost & ROI Analysis

### Development Costs

| Phase | Duration | Cost (€800/day) |
|-------|----------|-----------------|
| Phase 0: Setup | 5 days | €4,000 |
| Phase 1: JD Reader | 7 days | €5,600 |
| Phase 2: Unified Search | 10 days | €12,000 |
| Phase 3: Fit Filter | 12 days | €14,400 |
| Phase 4: Personal Opener | 7 days | €5,600 |
| Phase 5: Integration | 7 days | €11,200 |
| Phase 6: Polish | 5 days | €4,000 |
| **Total** | **53 days** | **€56,800** |

### Operational Costs (Monthly)

| Service | Cost |
|---------|------|
| Claude API (~1000 searches) | €500 |
| AWS (database, hosting) | €200 |
| n8n Cloud (optional) | €50 |
| LinkedIn Premium | €100 |
| **Total** | **€850/month** |

### ROI Calculation

**Assumptions:**
- Recruiter time saved: 1.5 hours per search
- Recruiter hourly rate: €50/hour
- Searches per month: 100

**Savings:**
- Time saved per search: 1.5 hours
- Cost saved per search: €75
- Monthly savings: €7,500
- **Annual savings: €90,000**

**Break-even:** ~8 months (€56,800 / €7,500/month)

---

## 🚀 Quick Start on Work Laptop (Tomorrow)

### Step 1: Install n8n-MCP

```bash
# Option A: npx (quickest)
npx n8n-mcp

# Option B: Docker (recommended)
docker pull ghcr.io/czlonkowski/n8n-mcp:latest
```

### Step 2: Configure Claude Code

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "http://localhost:5678",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Restart Claude Code**

### Step 3: Start Local n8n

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=changeme \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Open http://localhost:5678 and generate API key

### Step 4: Build Workflow with Claude

Open Claude Code and say:

```
Using n8n-MCP, build the Search-Score-Send workflow:

1. Webhook Trigger (POST /webhook/job-search)
2. JD Extraction (HTTP Request to API)
3. Parallel Search (LinkedIn + GitHub + Stack Overflow)
4. Merge Results
5. Batch Scoring
6. Filter 80%+
7. Generate Messages
8. Respond to Webhook

Add error handling and validate before showing me.
```

### Step 5: Test It

```bash
curl -X POST http://localhost:5678/webhook/search-score-send \
  -H "Content-Type: application/json" \
  -d '{
    "jobDescription": "Senior Rust Engineer with 5+ years...",
    "maxCandidates": 10,
    "scoreThreshold": 80
  }'
```

---

## 📚 Additional Resources

### Documentation Files (on server)
- `/root/NanoClaw/n8n/SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md`
- `/root/NanoClaw/n8n/N8N-INTEGRATION-GUIDE.md`

### Existing Codebase (to reuse)
- `/root/olorin/` - Main Olórin project (70% reusable)
- `/root/olorin/backend/` - FastAPI backend
- `/root/olorin/frontend/` - Next.js frontend
- `/root/olorin/sourcing_engine/` - Search agents
- `/root/olorin/anonymization-system/` - GDPR layer

### External Links
- **n8n-MCP:** https://github.com/czlonkowski/n8n-mcp
- **n8n Docs:** https://docs.n8n.io
- **MCP Docs:** https://modelcontextprotocol.io
- **Claude API:** https://docs.anthropic.com

---

## ✅ Success Metrics

### Performance Targets

| Metric | Target | Baseline |
|--------|--------|----------|
| JD Extraction | < 3 seconds | N/A |
| Search (50 candidates) | < 2 minutes | ~5 min manual |
| Scoring (50 candidates) | < 3 minutes | ~30 min manual |
| Messages (12 candidates) | < 1 minute | ~1 hour manual |
| **Total Workflow** | **< 5 minutes** | **~2 hours manual** |

**ROI:** 95% time reduction

### Quality Targets

| Metric | Target |
|--------|--------|
| JD Extraction Accuracy | 90%+ |
| Scoring Accuracy | 85%+ |
| Message Personalization | 100% non-template |
| Recruiter Approval Rate | 80%+ |
| Candidate Response Rate | 15%+ |

### Compliance Targets

| Requirement | Target |
|-------------|--------|
| GDPR Compliance | 100% |
| EU AI Act Compliance | 100% |
| Zero PII to Claude | 100% |
| Audit Trail | 100% |
| Data Retention | 180 days max |

---

## 🎯 Next Actions (Tomorrow on Work Laptop)

1. **Copy this document** to Google Drive
2. **Read SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md** (detailed technical spec)
3. **Read N8N-INTEGRATION-GUIDE.md** (n8n-MCP setup)
4. **Install n8n-MCP** (npx or Docker)
5. **Configure Claude Code** with n8n-MCP
6. **Start local n8n** instance
7. **Build workflow** using Claude Code + n8n-MCP
8. **Test with sample JD**
9. **Review and iterate**

---

## 📞 Questions?

When you get stuck:
1. Check the detailed implementation plan
2. Review n8n-MCP documentation
3. Test individual components
4. Use Claude Code to debug

---

**You have everything you need to start building tomorrow! 🚀**

All files are in `/root/NanoClaw/n8n/` on the server.
Copy this document and the other two to Google Drive for offline access.

Good luck with the implementation!
