# n8n-MCP Integration Guide for Search-Score-Send

**Integration between Search-Score-Send recruitment automation and n8n-MCP**

This guide shows how to use the n8n-MCP server to build and manage the Search-Score-Send workflow automation system.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [n8n-MCP Capabilities](#n8n-mcp-capabilities)
3. [Integration Architecture](#integration-architecture)
4. [Setup Instructions](#setup-instructions)
5. [Workflow Implementation](#workflow-implementation)
6. [API Integration Examples](#api-integration-examples)
7. [Deployment Options](#deployment-options)

---

## Overview

**n8n-MCP** is a Model Context Protocol server that gives AI assistants (like Claude) comprehensive access to n8n's workflow automation platform:

- **1,396 n8n nodes** (812 core + 584 community)
- **2,709 workflow templates** with metadata
- **Real-time workflow management** via n8n API
- **Validation & testing** before deployment

**Why use n8n-MCP for Search-Score-Send?**
- ✅ Visual workflow editor (modify without code changes)
- ✅ Built-in error handling and retries
- ✅ Parallel execution (LinkedIn + GitHub + SO simultaneously)
- ✅ Real-time progress webhooks
- ✅ Template library for common patterns
- ✅ Easy to add new platforms (Twitter, Medium, Dev.to)

---

## n8n-MCP Capabilities

### Available Tools

**Documentation Tools (7 tools):**
- `search_nodes` - Find n8n nodes by functionality
- `get_node` - Get node configuration details
- `validate_node` - Validate node configurations
- `validate_workflow` - Validate complete workflows
- `search_templates` - Find workflow templates
- `get_template` - Retrieve workflow JSON
- `tools_documentation` - Get help for any tool

**Workflow Management Tools (13 tools - requires n8n API):**
- `n8n_create_workflow` - Deploy new workflows
- `n8n_get_workflow` - Retrieve workflows
- `n8n_update_partial_workflow` - Batch updates
- `n8n_list_workflows` - List all workflows
- `n8n_delete_workflow` - Remove workflows
- `n8n_validate_workflow` - Validate deployed workflows
- `n8n_autofix_workflow` - Auto-fix common errors
- `n8n_test_workflow` - Trigger workflow execution
- `n8n_executions` - Monitor execution status
- `n8n_health_check` - Check API connectivity

**Execution Management:**
- `n8n_test_workflow` - Trigger workflow with custom data
- `n8n_executions` - List/get/delete execution records

---

## Integration Architecture

### Option 1: Claude Code + n8n-MCP (Recommended for Development)

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code                          │
│  (Development Environment on Work Laptop)               │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ MCP Protocol
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    n8n-MCP Server                       │
│  (npx n8n-mcp or Docker)                                │
│                                                          │
│  • Node documentation (1,396 nodes)                     │
│  • Workflow templates (2,709)                           │
│  • Validation engine                                    │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ n8n REST API
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    n8n Instance                         │
│  (Local or Cloud: localhost:5678 or n8n.cloud)         │
│                                                          │
│  • Workflow execution engine                            │
│  • Scheduled triggers                                   │
│  • Webhook endpoints                                    │
│  • Database storage                                     │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Build workflows visually with AI assistance
- ✅ Validate before deployment
- ✅ Test locally before production
- ✅ Version control with git

---

### Option 2: Backend API → n8n-MCP → n8n (Production)

```
┌─────────────────────────────────────────────────────────┐
│              Search-Score-Send Backend                  │
│  (FastAPI Python Service)                               │
│                                                          │
│  POST /api/workflows/create                             │
│  POST /api/workflows/trigger                            │
│  GET  /api/workflows/{id}/status                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ HTTP/SSE
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    n8n-MCP Server                       │
│  (Railway/Docker/Local)                                 │
│                                                          │
│  • Workflow validation                                  │
│  • Template deployment                                  │
│  • Execution monitoring                                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ n8n REST API
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    n8n Instance                         │
│  (Production: n8n.cloud or self-hosted)                 │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Search-Score-Send Workflow                      │  │
│  │                                                   │  │
│  │  Webhook → JD Extract → Parallel Search →        │  │
│  │  → Batch Scoring → Filter 80%+ →                 │  │
│  │  → Generate Messages → Notify Complete           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Production-grade automation
- ✅ Error handling & retries
- ✅ Real-time progress updates
- ✅ Scalable execution

---

## Setup Instructions

### Step 1: Install n8n-MCP

**Option A: npx (Quickest)**

```bash
# Run directly (no installation needed)
npx n8n-mcp
```

**Option B: Docker (Recommended for Production)**

```bash
# Pull image
docker pull ghcr.io/czlonkowski/n8n-mcp:latest

# Run with n8n API credentials
docker run -i --rm --init \
  -e MCP_MODE=stdio \
  -e N8N_API_URL=https://your-n8n-instance.com \
  -e N8N_API_KEY=your-api-key \
  ghcr.io/czlonkowski/n8n-mcp:latest
```

**Option C: Local Development**

```bash
cd /root/NanoClaw/n8n/n8n-mcp
npm install
npm run build
npm run rebuild  # Build node database
npm start
```

---

### Step 2: Configure Claude Code

Add to Claude Code config (work laptop):

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

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

**Restart Claude Code** after updating config.

---

### Step 3: Set Up Local n8n Instance

**Option A: Docker Compose (Recommended)**

```bash
# Create docker-compose.yml
cd /root/NanoClaw/n8n
cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=Europe/Amsterdam
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

volumes:
  n8n_data:
EOF

# Start n8n
docker-compose up -d

# Get API key
# 1. Open http://localhost:5678
# 2. Login with admin/changeme
# 3. Go to Settings → API
# 4. Generate API key
```

**Option B: n8n Cloud**

1. Sign up at [n8n.cloud](https://n8n.cloud)
2. Get API key from Settings → API
3. Use your cloud URL: `https://your-workspace.app.n8n.cloud`

---

## Workflow Implementation

### Phase 1: Build Workflow with Claude Code

**Prompt to Claude Code:**

```
Using n8n-MCP, build a Search-Score-Send recruitment workflow:

1. Webhook Trigger (POST /webhook/job-search)
   - Accepts: { jobDescription, maxCandidates, scoreThreshold }

2. JD Extraction Node (HTTP Request to our API)
   - POST /api/jd/extract
   - Returns: structured requirements

3. Parallel Search (Split in Batches)
   - LinkedIn Search (HTTP Request)
   - GitHub Search (HTTP Request)
   - Stack Overflow Search (HTTP Request)

4. Merge Results (Merge node)

5. Batch Scoring (HTTP Request)
   - POST /api/scoring/batch
   - Returns: scored candidates

6. Filter Qualified (IF node)
   - Condition: overall_score >= scoreThreshold

7. Generate Messages (HTTP Request)
   - POST /api/messages/generate-batch

8. Respond to Webhook
   - Return: workflow_id, candidates_ready, review_url

Requirements:
- Add error handling for each HTTP node
- Use expressions: $json, $node["NodeName"].json
- Set timeouts: 60s for search, 120s for scoring
- Enable parallel execution for searches

Validate the workflow before showing it to me.
```

Claude will:
1. ✅ Search for appropriate nodes (`search_nodes`)
2. ✅ Get node configurations (`get_node`)
3. ✅ Validate each node (`validate_node`)
4. ✅ Build complete workflow JSON
5. ✅ Validate workflow (`validate_workflow`)
6. ✅ Show you the result in an artifact

---

### Phase 2: Deploy to n8n

**Deploy via Claude Code:**

```
Deploy this workflow to my local n8n instance (http://localhost:5678).
Name it: "Search-Score-Send Workflow"
Set it to active.
```

Claude will:
1. ✅ Use `n8n_create_workflow` to deploy
2. ✅ Return workflow ID and webhook URL
3. ✅ Test connectivity with `n8n_health_check`

---

### Phase 3: Test Workflow

**Test via Claude Code:**

```
Test the Search-Score-Send workflow with this sample data:

{
  "jobDescription": "Senior Rust Engineer with 5+ years experience...",
  "maxCandidates": 10,
  "scoreThreshold": 80
}

Monitor the execution and show me the results.
```

Claude will:
1. ✅ Use `n8n_test_workflow` to trigger
2. ✅ Use `n8n_executions` to monitor
3. ✅ Show execution results

---

## API Integration Examples

### Example 1: Trigger Workflow from Python Backend

```python
# backend/services/n8n_client.py
import httpx
from typing import Dict

class N8nClient:
    """Client for triggering n8n workflows"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout

    async def trigger_search_score_send(
        self,
        job_description: str,
        max_candidates: int = 50,
        score_threshold: float = 80.0,
        callback_url: str = None
    ) -> Dict:
        """
        Trigger the Search-Score-Send workflow

        Args:
            job_description: Raw JD text
            max_candidates: Total candidates to find
            score_threshold: Minimum match percentage
            callback_url: URL for progress webhooks

        Returns:
            {
                "workflow_id": "wf-123",
                "execution_id": "exec-456",
                "status": "running",
                "estimated_duration": "3-5 minutes"
            }
        """

        payload = {
            "jobDescription": job_description,
            "maxCandidates": max_candidates,
            "scoreThreshold": score_threshold,
            "callbackUrl": callback_url or f"{settings.API_URL}/api/webhooks/n8n-progress"
        }

        response = await self.client.post(
            self.webhook_url,
            json=payload
        )

        response.raise_for_status()
        return response.json()

    async def get_execution_status(self, execution_id: str) -> Dict:
        """
        Get workflow execution status

        Note: This requires n8n API credentials
        Use n8n-MCP's n8n_executions tool or direct API call
        """

        response = await self.client.get(
            f"{settings.N8N_API_URL}/api/v1/executions/{execution_id}",
            headers={"X-N8N-API-KEY": settings.N8N_API_KEY}
        )

        response.raise_for_status()
        return response.json()
```

---

### Example 2: FastAPI Endpoint

```python
# backend/api/workflows.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

class WorkflowTriggerRequest(BaseModel):
    job_description: str
    max_candidates: int = 50
    score_threshold: float = 80.0

class WorkflowResponse(BaseModel):
    workflow_id: str
    execution_id: str
    status: str
    webhook_url: str
    estimated_duration: str

@router.post("/trigger", response_model=WorkflowResponse)
async def trigger_workflow(
    request: WorkflowTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger Search-Score-Send workflow

    This endpoint triggers the n8n workflow and returns immediately.
    Use /api/workflows/{workflow_id}/status to poll for progress.
    """

    # Generate unique workflow ID
    workflow_id = f"wf-{uuid.uuid4().hex[:8]}"

    # Trigger n8n workflow
    n8n_client = N8nClient(webhook_url=settings.N8N_WEBHOOK_URL)

    try:
        result = await n8n_client.trigger_search_score_send(
            job_description=request.job_description,
            max_candidates=request.max_candidates,
            score_threshold=request.score_threshold,
            callback_url=f"{settings.API_URL}/api/webhooks/n8n-progress/{workflow_id}"
        )

        # Store workflow metadata in database
        await db.workflows.insert({
            "id": workflow_id,
            "execution_id": result["execution_id"],
            "status": "running",
            "created_at": datetime.utcnow(),
            "request": request.dict()
        })

        return WorkflowResponse(
            workflow_id=workflow_id,
            execution_id=result["execution_id"],
            status="running",
            webhook_url=f"{settings.API_URL}/api/workflows/{workflow_id}/status",
            estimated_duration="3-5 minutes"
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger n8n workflow: {str(e)}"
        )

@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """
    Get workflow execution status

    Returns real-time progress updates from n8n
    """

    workflow = await db.workflows.find_one({"id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Get execution status from n8n
    n8n_client = N8nClient(webhook_url=settings.N8N_WEBHOOK_URL)
    execution = await n8n_client.get_execution_status(workflow["execution_id"])

    return {
        "workflow_id": workflow_id,
        "status": execution["status"],  # running, success, error
        "current_step": execution.get("currentNode"),
        "progress": execution.get("progress", 0),
        "candidates_found": workflow.get("candidates_found", 0),
        "candidates_scored": workflow.get("candidates_scored", 0),
        "candidates_qualified": workflow.get("candidates_qualified", 0),
        "completed_at": execution.get("finishedAt")
    }

@router.post("/webhooks/n8n-progress/{workflow_id}")
async def handle_n8n_progress_webhook(workflow_id: str, data: dict):
    """
    Receive progress updates from n8n workflow

    n8n sends POST requests to this endpoint with progress data
    """

    # Update workflow status in database
    await db.workflows.update_one(
        {"id": workflow_id},
        {"$set": {
            "status": data.get("status"),
            "current_step": data.get("current_step"),
            "candidates_found": data.get("candidates_found"),
            "candidates_scored": data.get("candidates_scored"),
            "candidates_qualified": data.get("candidates_qualified"),
            "updated_at": datetime.utcnow()
        }}
    )

    # Emit SSE event to frontend
    await sse_manager.send_event(
        channel=workflow_id,
        event="progress",
        data=data
    )

    return {"status": "ok"}
```

---

### Example 3: Real-Time Progress Updates (SSE)

```python
# backend/api/sse.py
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio

router = APIRouter(prefix="/api/sse", tags=["sse"])

@router.get("/workflows/{workflow_id}/progress")
async def workflow_progress_stream(workflow_id: str):
    """
    Server-Sent Events stream for real-time workflow progress

    Frontend connects to this endpoint to receive live updates
    """

    async def event_generator():
        """Generate SSE events"""

        # Initial connection
        yield {
            "event": "connected",
            "data": json.dumps({"workflow_id": workflow_id})
        }

        # Subscribe to workflow progress channel
        async for message in sse_manager.subscribe(workflow_id):
            yield {
                "event": message["event"],
                "data": json.dumps(message["data"])
            }

    return EventSourceResponse(event_generator())
```

**Frontend Usage (React):**

```tsx
// frontend/hooks/useWorkflowProgress.ts
import { useEffect, useState } from 'react';

export function useWorkflowProgress(workflowId: string) {
  const [progress, setProgress] = useState({
    status: 'connecting',
    current_step: null,
    candidates_found: 0,
    candidates_scored: 0,
    candidates_qualified: 0
  });

  useEffect(() => {
    const eventSource = new EventSource(
      `/api/sse/workflows/${workflowId}/progress`
    );

    eventSource.addEventListener('connected', (event) => {
      console.log('Connected to progress stream');
    });

    eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);
      setProgress(prev => ({ ...prev, ...data }));
    });

    eventSource.addEventListener('completed', (event) => {
      const data = JSON.parse(event.data);
      setProgress(prev => ({ ...prev, status: 'completed', ...data }));
      eventSource.close();
    });

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      setProgress(prev => ({ ...prev, status: 'error' }));
      eventSource.close();
    };

    return () => eventSource.close();
  }, [workflowId]);

  return progress;
}
```

---

## Deployment Options

### Option 1: Local Development

**Best for:** Development and testing

```bash
# Terminal 1: n8n
docker-compose up n8n

# Terminal 2: n8n-MCP
npx n8n-mcp

# Terminal 3: Backend API
cd backend
uvicorn api.main:app --reload --port 3000

# Terminal 4: Frontend
cd frontend
npm run dev
```

**Access:**
- n8n: http://localhost:5678
- Backend: http://localhost:3000
- Frontend: http://localhost:3001

---

### Option 2: Railway Cloud Deployment

**Best for:** Staging and small production

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/n8n-mcp?referralCode=n8n-mcp)

1. Click "Deploy on Railway"
2. Configure environment variables:
   - `N8N_API_URL`: Your n8n instance URL
   - `N8N_API_KEY`: Your n8n API key
3. Deploy
4. Get deployment URL
5. Update backend config with Railway URL

---

### Option 3: Production (Docker Compose)

**Best for:** Production self-hosted

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    environment:
      - N8N_BASIC_AUTH_ACTIVE=false
      - N8N_JWT_AUTH_ACTIVE=true
      - WEBHOOK_URL=https://your-domain.com/
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - redis
      - postgres

  n8n-mcp:
    image: ghcr.io/czlonkowski/n8n-mcp:latest
    environment:
      - MCP_MODE=http
      - N8N_API_URL=http://n8n:5678
      - N8N_API_KEY=${N8N_API_KEY}
    ports:
      - "3333:3000"

  backend:
    build: ./backend
    environment:
      - N8N_WEBHOOK_URL=http://n8n:5678/webhook/search-score-send
      - N8N_API_URL=http://n8n:5678
      - N8N_API_KEY=${N8N_API_KEY}
    depends_on:
      - n8n
      - postgres

  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=https://api.your-domain.com

  redis:
    image: redis:alpine

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

**Deploy:**

```bash
# Set environment variables
export N8N_API_KEY="your-api-key"
export POSTGRES_PASSWORD="secure-password"

# Deploy
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose ps
```

---

## Next Steps

1. **Set up n8n-MCP** on your work laptop (npx or Docker)
2. **Configure Claude Code** with n8n-MCP server
3. **Build the workflow** using Claude Code + n8n-MCP
4. **Test locally** with sample job descriptions
5. **Deploy to production** (Railway or Docker Compose)
6. **Integrate backend API** with n8n webhooks
7. **Add real-time updates** (SSE) to frontend

---

## Resources

- **n8n-MCP Repo:** https://github.com/czlonkowski/n8n-mcp
- **n8n Docs:** https://docs.n8n.io
- **MCP Docs:** https://modelcontextprotocol.io
- **Search-Score-Send Plan:** [SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md](./SEARCH-SCORE-SEND-IMPLEMENTATION-PLAN.md)

---

**Built with 🚀 n8n + Claude + MCP**
