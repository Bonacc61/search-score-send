# Search-Score-Send Project Log

**Project:** AI-Powered Recruitment Automation System
**Created:** 2026-03-30
**Status:** Planning Phase Complete
**Location:** `/root/NanoClaw/n8n/`

---

## 📋 Session Summary

### Date: 2026-03-30
**Duration:** ~2 hours
**Participants:** User, Claude Code (Sonnet 4.5)

### Objective
Develop a comprehensive implementation plan for the **Search-Score-Send** system - a recruitment automation workflow that reduces search time from 2 hours to 5 minutes (95% reduction).

---

## 🎯 What Was Built

### 1. Complete Implementation Plan
**File:** `SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md` (1,920 lines)

**Contents:**
- System architecture leveraging 70% existing Olórin codebase
- Database schema design (4 new tables, 3 table extensions)
- Complete backend implementation (Python/FastAPI):
  - JD Extraction Engine (~500 lines)
  - Unified Search Coordinator (~300 lines)
  - Fit Scoring Engine (~400 lines)
  - Message Generator (~400 lines)
- Complete frontend design (React/Next.js):
  - Job description input form
  - Real-time progress tracking
  - Candidate review dashboard
- 8-week phased roadmap with exit criteria
- Cost analysis: €56,800 dev, €850/month ops
- ROI calculation: 8 months break-even, €90K/year savings

---

### 2. n8n-MCP Integration Guide
**File:** `N8N-INTEGRATION-GUIDE.md` (810 lines)

**Contents:**
- n8n-MCP capabilities overview (1,396 nodes, 2,709 templates)
- Setup instructions (npx/Docker/local installation)
- Claude Code configuration examples
- API integration patterns:
  - Python FastAPI endpoints
  - n8n webhook triggers
  - Real-time progress updates (SSE)
- Deployment options:
  - Local development setup
  - Railway cloud deployment
  - Production Docker Compose

---

### 3. Google Drive Ready Guide
**File:** `COMPLETE-GUIDE-FOR-GOOGLE-DRIVE.md` (831 lines)

**Contents:**
- Executive summary for easy copy-paste
- Quick start guide for work laptop implementation
- Architecture diagrams and component breakdown
- Key code examples (Python & React)
- Step-by-step implementation roadmap
- Success metrics and KPIs
- Next actions checklist

---

### 4. n8n-MCP Repository Clone
**Directory:** `n8n-mcp/` (removed from staging)

**Source:** https://github.com/czlonkowski/n8n-mcp

**Note:** Repository was cloned for reference but removed from git staging to avoid submodule complexity. User can clone directly from GitHub when needed.

---

## 🏗️ System Architecture

### The Three-Step Workflow

```
┌──────────────────────────────────────────────────────┐
│  Step 1: JD Reader (Search) - 2 minutes             │
│  ─────────────────────────────────────────────────   │
│  Input:  Job description (paste)                     │
│  Output: 50 candidates from LinkedIn/GitHub/SO      │
│  Tech:   Claude API for extraction                   │
│          Parallel search across platforms            │
└──────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│  Step 2: Fit Filter (Qualification) - 3 minutes     │
│  ─────────────────────────────────────────────────   │
│  Input:  50 raw candidate profiles                   │
│  Output: 12 candidates scoring 80%+                  │
│  Tech:   Claude API for scoring                      │
│          GDPR anonymization layer                    │
│          Skill-by-skill breakdown                    │
└──────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│  Step 3: Personal Opener (Outreach) - 1 minute      │
│  ─────────────────────────────────────────────────   │
│  Input:  12 qualified candidates                     │
│  Output: Personalized messages (not templates)       │
│  Tech:   Claude API for generation                   │
│          Evidence extraction                         │
│          Human review (HITL)                         │
└──────────────────────────────────────────────────────┘
```

**Total Time:** 5 minutes (vs. 2 hours manual)
**Time Savings:** 95%

---

## 💻 Technical Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** SQLite with SQLCipher encryption
- **AI:** Claude Sonnet 4 (Anthropic API)
- **Queue:** Async processing with asyncio

### Frontend
- **Framework:** Next.js 14 (React 18)
- **Styling:** Tailwind CSS + shadcn/ui components
- **State Management:** TanStack Query (React Query)
- **Real-time:** Server-Sent Events (SSE)
- **Charts:** Recharts + Chart.js

### Automation
- **Orchestration:** n8n workflow engine
- **Integration:** n8n-MCP (Model Context Protocol)
- **Deployment:** Docker + Docker Compose

### Compliance
- **GDPR:** Zero-PII architecture, dual encryption, automated DSAR
- **EU AI Act:** HITL approval gates, transparent explanations
- **Audit:** Immutable append-only logs
- **Retention:** 180-day auto-deletion

---

## 🗂️ Existing Infrastructure (Reuse 70%)

**Location:** `/root/olorin/`

### Reusable Components

1. **GDPR Anonymization System** (`/root/olorin/anonymization-system/`)
   - Zero-PII architecture
   - Dual encryption (SQLCipher + Fernet)
   - HMAC searchable encryption
   - Automated data subject rights

2. **AI Scoring Engine** (`/root/olorin/backend/scoring/`)
   - Claude-based evaluation
   - Structured reasoning
   - Audit trail
   - HITL integration

3. **Database Models** (`/root/olorin/backend/database/`)
   - SQLite with encryption
   - Schema already designed
   - Migration system

4. **HITL Dashboard** (`/root/olorin/frontend/`)
   - Human approval gates
   - Next.js + Tailwind
   - Real-time updates
   - Review workflows

5. **Sourcing Engine** (`/root/olorin/sourcing_engine/`)
   - GitHub agent
   - LinkedIn agent
   - Stack Overflow agent
   - Multi-platform search

---

## 📊 New Components to Build (30%)

### 1. JD Extraction Engine
**Estimated Lines:** ~500
**Dependencies:** Claude API, existing parsers
**Key Features:**
- Natural language JD parsing
- Boolean query generation (LinkedIn/GitHub/SO)
- Requirement extraction (must-have/nice-to-have)
- Salary/location parsing

### 2. Unified Search Coordinator
**Estimated Lines:** ~300
**Dependencies:** Existing sourcing agents
**Key Features:**
- Parallel execution across platforms
- HMAC-based deduplication
- Progress tracking
- Error handling

### 3. Message Generator
**Estimated Lines:** ~400
**Dependencies:** Claude API, anonymization
**Key Features:**
- Personalized message generation
- Evidence extraction (projects/answers)
- Personalization point tracking
- Batch processing

### 4. Frontend Workflow UI
**Estimated Lines:** ~3 React pages
**Dependencies:** Next.js, shadcn/ui
**Key Features:**
- Job description input form
- Real-time progress tracking (SSE)
- Candidate review dashboard
- Message editing interface

---

## 💰 Financial Analysis

### Development Costs

| Phase | Duration | FTE | Cost (€800/day) |
|-------|----------|-----|-----------------|
| Phase 0: Setup & Dependencies | 5 days | 1.0 | €4,000 |
| Phase 1: JD Reader | 7 days | 1.0 | €5,600 |
| Phase 2: Unified Search | 10 days | 1.5 | €12,000 |
| Phase 3: Fit Filter | 12 days | 1.5 | €14,400 |
| Phase 4: Personal Opener | 7 days | 1.0 | €5,600 |
| Phase 5: Integration | 7 days | 2.0 | €11,200 |
| Phase 6: Polish & Launch | 5 days | 1.0 | €4,000 |
| **TOTAL** | **53 days** | **1.3 avg** | **€56,800** |

### Operational Costs (Monthly)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Claude API | ~1,000 searches | €500 |
| AWS Infrastructure | Database, hosting | €200 |
| n8n Cloud | Optional workflow hosting | €50 |
| LinkedIn Premium | Sourcing access | €100 |
| **TOTAL** | | **€850** |

### ROI Calculation

**Assumptions:**
- Recruiter time saved: 1.5 hours per search
- Recruiter hourly rate: €50/hour
- Searches per month: 100

**Financial Impact:**
- Time saved per search: 1.5 hours
- Cost saved per search: €75
- Monthly savings: €7,500
- **Annual savings: €90,000**

**Break-even Period:** 8 months (€56,800 / €7,500/month)

**5-Year ROI:**
- Total investment: €56,800 + (€850 × 60) = €107,800
- Total savings: €90,000 × 5 = €450,000
- **Net profit: €342,200**
- **ROI: 317%**

---

## 🗺️ Implementation Roadmap

### Phase 0: Setup & Dependencies (Week 1)
**Duration:** 3-5 days | **Status:** Not Started

**Tasks:**
- [ ] Install n8n-MCP (npx or Docker)
- [ ] Extend Olórin database schema
- [ ] Set up development environment
- [ ] GDPR compliance review with legal
- [ ] Generate encryption keys
- [ ] Configure environment variables

**Exit Criteria:**
- ✅ n8n-MCP accessible at localhost
- ✅ Database migrations applied
- ✅ All existing Olórin tests passing
- ✅ Legal sign-off obtained

---

### Phase 1: JD Reader (Week 2)
**Duration:** 5-7 days | **Status:** Not Started

**Files to Create:**
```
backend/services/jd_extractor.py          # Claude-based JD parsing
backend/services/requirements_parser.py   # Requirement extraction
backend/services/query_generator.py       # Boolean query generation
backend/api/jd_routes.py                  # API endpoints
frontend/app/jobs/new/page.tsx            # Job input form
tests/test_jd_extractor.py                # Unit tests
```

**Exit Criteria:**
- ✅ JD extraction accuracy: 90%+ on test set
- ✅ Boolean queries work on LinkedIn/GitHub/SO
- ✅ Frontend form allows editing extracted data
- ✅ API response time < 3 seconds

---

### Phase 2: Unified Search (Week 3)
**Duration:** 7-10 days | **Status:** Not Started

**Files to Create:**
```
backend/services/unified_search.py        # Parallel coordinator
sourcing_engine/linkedin_agent.py         # Adapt existing
sourcing_engine/github_agent.py           # Adapt existing
sourcing_engine/stackoverflow_agent.py    # Adapt existing
backend/services/deduplicator.py          # HMAC-based dedup
backend/services/workflow_tracker.py      # Progress tracking
tests/test_unified_search.py              # Integration tests
```

**Exit Criteria:**
- ✅ Finds 50 candidates in < 2 minutes
- ✅ Zero duplicates (email/username dedup)
- ✅ Progress updates every 5 seconds
- ✅ Works with n8n parallel execution

---

### Phase 3: Fit Filter (Week 4-5)
**Duration:** 10-12 days | **Status:** Not Started

**Files to Create:**
```
backend/scoring/fit_scorer.py             # AI scoring engine
backend/services/batch_scorer.py          # Batch processing
backend/services/rejection_analyzer.py    # Rejection categorization
frontend/app/workflows/[id]/review/page.tsx  # Review dashboard
frontend/components/ScoreBreakdown.tsx    # Score visualization
tests/test_fit_scorer.py                  # Unit tests
tests/test_batch_scorer.py                # Integration tests
```

**Exit Criteria:**
- ✅ Scoring accuracy: 85%+ vs. human evaluation
- ✅ Batch processing: 50 candidates in < 3 minutes
- ✅ GDPR compliant: Zero PII to Claude
- ✅ EU AI Act: Structured explanations for all scores

---

### Phase 4: Personal Opener (Week 6)
**Duration:** 5-7 days | **Status:** Not Started

**Files to Create:**
```
backend/services/message_generator.py     # Message generation
backend/services/personalization_extractor.py  # Evidence linking
backend/services/batch_message_generator.py    # Batch processing
frontend/components/MessageReview.tsx     # Review UI
backend/services/message_approval.py      # HITL approval
tests/test_message_generator.py           # Unit tests
```

**Exit Criteria:**
- ✅ Zero template messages ([FIRST NAME], etc.)
- ✅ 100% include specific project mentions
- ✅ Human review required before sending
- ✅ Editable inline in UI

---

### Phase 5: Integration (Week 7)
**Duration:** 5-7 days | **Status:** Not Started

**Tasks:**
- [ ] Wire all components together
- [ ] Add WebSocket real-time updates
- [ ] Implement error handling & retries
- [ ] Create monitoring dashboard
- [ ] Complete GDPR audit trail
- [ ] Load testing

**Exit Criteria:**
- ✅ Full workflow completes in < 5 minutes
- ✅ 95%+ success rate (no crashes)
- ✅ Real-time progress visible
- ✅ Complete audit trail

---

### Phase 6: Polish & Launch (Week 8)
**Duration:** 5 days | **Status:** Not Started

**Tasks:**
- [ ] User testing with 5 recruiters
- [ ] Write user documentation & video
- [ ] Performance optimization
- [ ] Legal final review
- [ ] Production deployment
- [ ] Training materials

**Exit Criteria:**
- ✅ User satisfaction: 8/10+
- ✅ Legal approval for production use
- ✅ Performance targets met
- ✅ Documentation complete

---

## 📈 Success Metrics

### Performance Targets

| Metric | Target | Current (Baseline) | Status |
|--------|--------|-------------------|--------|
| JD Extraction Time | < 3 seconds | N/A (new) | ⏳ Not started |
| Search Time (50 candidates) | < 2 minutes | ~5 min (manual) | ⏳ Not started |
| Scoring Time (50 candidates) | < 3 minutes | ~30 min (manual) | ⏳ Not started |
| Message Generation (12) | < 1 minute | ~1 hour (manual) | ⏳ Not started |
| **Total Workflow Time** | **< 5 minutes** | **~2 hours (manual)** | ⏳ Not started |

---

### Quality Targets

| Metric | Target | Measurement Method | Status |
|--------|--------|-------------------|--------|
| JD Extraction Accuracy | 90%+ | AI vs. human extraction | ⏳ Not started |
| Scoring Accuracy | 85%+ | AI scores vs. recruiter judgment | ⏳ Not started |
| Message Personalization | 100% | Manual review (no [FIRST NAME]) | ⏳ Not started |
| Recruiter Approval Rate | 80%+ | % of AI messages sent without edits | ⏳ Not started |
| Candidate Response Rate | 15%+ | LinkedIn InMail response rate | ⏳ Not started |

---

### Compliance Targets

| Requirement | Target | Status |
|-------------|--------|--------|
| GDPR Compliance | 100% | ✅ Design complete |
| EU AI Act Compliance | 100% | ✅ HITL design complete |
| Zero PII to Claude | 100% | ✅ Anonymization layer designed |
| Audit Trail Completeness | 100% | ✅ Logging strategy defined |
| Data Retention Policy | 180 days max | ✅ Auto-deletion designed |

---

## 🔗 External Resources

### Documentation
- **n8n-MCP Repository:** https://github.com/czlonkowski/n8n-mcp
- **n8n Documentation:** https://docs.n8n.io
- **MCP Protocol Docs:** https://modelcontextprotocol.io
- **Claude API Docs:** https://docs.anthropic.com

### Existing Codebase
- **Olórin Project:** `/root/olorin/`
- **Backend:** `/root/olorin/backend/`
- **Frontend:** `/root/olorin/frontend/`
- **Sourcing Engine:** `/root/olorin/sourcing_engine/`
- **Anonymization:** `/root/olorin/anonymization-system/`

---

## 📝 Notes & Decisions

### Design Decisions

1. **n8n-MCP Integration**
   - **Decision:** Use n8n-MCP for workflow orchestration instead of pure Python
   - **Rationale:** Visual workflow editor, easier to modify, parallel execution built-in
   - **Trade-off:** Additional dependency, but significant UX improvement

2. **Reuse Olórin Codebase**
   - **Decision:** Leverage 70% of existing infrastructure
   - **Rationale:** GDPR compliance already built, tested, and production-ready
   - **Trade-off:** Must adapt to existing patterns, but massive time savings

3. **Real-Time Updates via SSE**
   - **Decision:** Use Server-Sent Events instead of WebSockets
   - **Rationale:** Simpler implementation, one-way communication sufficient
   - **Trade-off:** Less flexible than WebSockets, but adequate for use case

4. **Claude Sonnet 4 for All AI Tasks**
   - **Decision:** Use same model for extraction, scoring, and message generation
   - **Rationale:** Consistency, single API integration, high quality
   - **Trade-off:** Higher cost than smaller models, but quality justifies it

---

## 🚀 Next Steps (For User)

### Immediate (Tomorrow on Work Laptop)

1. **Download Documents to Google Drive**
   - Copy `COMPLETE-GUIDE-FOR-GOOGLE-DRIVE.md`
   - Copy `SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md`
   - Copy `N8N-INTEGRATION-GUIDE.md`

2. **Install n8n-MCP**
   ```bash
   npx n8n-mcp
   ```

3. **Configure Claude Code**
   - Add n8n-MCP to Claude config
   - Restart Claude Code

4. **Start Local n8n**
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

5. **Build Workflow with Claude Code**
   - Use n8n-MCP tools to build Search-Score-Send workflow
   - Validate before deployment
   - Test with sample data

---

### Week 1 (Phase 0: Setup)

1. **Environment Setup**
   - Install Python 3.11+
   - Set up FastAPI development environment
   - Install Next.js 14

2. **Database Setup**
   - Extend Olórin schema
   - Create migration scripts
   - Test on development database

3. **Legal Review**
   - Present GDPR compliance plan
   - Review EU AI Act requirements
   - Get sign-off for development

4. **Development Planning**
   - Create GitHub project board
   - Set up CI/CD pipeline
   - Schedule weekly demos

---

## 📊 Project Statistics

### Documentation Metrics

| Document | Lines | Words (est.) | Purpose |
|----------|-------|--------------|---------|
| SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md | 1,920 | ~38,000 | Complete technical spec |
| N8N-INTEGRATION-GUIDE.md | 810 | ~16,000 | Integration guide |
| COMPLETE-GUIDE-FOR-GOOGLE-DRIVE.md | 831 | ~16,500 | Google Drive summary |
| **TOTAL** | **3,561** | **~70,500** | |

### Code Estimates

| Component | Lines | Language | Status |
|-----------|-------|----------|--------|
| JD Extractor | ~500 | Python | Not started |
| Unified Search | ~300 | Python | Not started |
| Fit Scorer | ~400 | Python | Not started |
| Message Generator | ~400 | Python | Not started |
| Frontend Pages | ~1,500 | React/TypeScript | Not started |
| Tests | ~1,000 | Python/TypeScript | Not started |
| **TOTAL NEW CODE** | **~4,100** | | |
| **REUSED FROM OLÓRIN** | **~10,000** | | Existing |
| **TOTAL PROJECT** | **~14,100** | | |

---

## 🎯 Current Status

**Phase:** Planning Complete
**Next Phase:** Phase 0 (Setup & Dependencies)
**Target Start Date:** User's work laptop tomorrow
**Estimated Completion:** 8 weeks from start

---

## ✅ Deliverables Completed

1. ✅ Complete implementation plan (50+ pages)
2. ✅ n8n-MCP integration guide
3. ✅ Google Drive-ready summary
4. ✅ Database schema design
5. ✅ Code examples (Python & React)
6. ✅ Cost analysis & ROI calculation
7. ✅ 8-week phased roadmap
8. ✅ Success metrics & KPIs

---

## 📞 Support

**If Issues Arise:**
1. Check detailed implementation plan
2. Review n8n-MCP documentation
3. Test components individually
4. Use Claude Code for debugging

---

**End of Log**

*All planning phase deliverables complete. Ready for implementation on work laptop.*

---

**Location:** `/root/NanoClaw/n8n/`
**Files:** 3 markdown documents (3,561 lines total)
**Status:** ✅ Planning Complete | ⏳ Implementation Pending
