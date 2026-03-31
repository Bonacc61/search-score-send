"""
Progress update router for real-time SSE updates
"""
from fastapi import APIRouter, HTTPException
from ..models import ProgressUpdate
from ..sse import sse_manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/update")
async def update_progress(update: ProgressUpdate):
    """
    Post a progress update that will be broadcast via SSE

    Called by n8n workflow nodes to send real-time updates to frontend
    """
    try:
        logger.info(f"Progress update for {update.execution_id}: {update.stage} - {update.message}")

        # Broadcast to all SSE subscribers
        await sse_manager.broadcast(
            execution_id=update.execution_id,
            message=update.dict()
        )

        return {
            "status": "broadcasted",
            "execution_id": update.execution_id,
            "subscribers": sse_manager.get_connection_count(update.execution_id)
        }

    except Exception as e:
        logger.error(f"Failed to broadcast progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
