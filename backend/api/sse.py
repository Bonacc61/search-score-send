"""
Server-Sent Events (SSE) manager for real-time progress updates
"""
import asyncio
from typing import Dict, Set
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SSEManager:
    """
    Manages Server-Sent Events for real-time progress updates

    Frontend connects to /api/progress/stream/{execution_id}
    Backend calls sse_manager.broadcast(execution_id, data) to send updates
    """

    def __init__(self):
        self.connections: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
        self.is_running = False

    async def start(self):
        """Start the SSE manager"""
        self.is_running = True
        logger.info("SSE Manager started")

    async def stop(self):
        """Stop the SSE manager and close all connections"""
        self.is_running = False

        # Send close signal to all connections
        for execution_id, queues in self.connections.items():
            for queue in queues:
                await queue.put({"type": "close"})

        self.connections.clear()
        logger.info("SSE Manager stopped")

    async def subscribe(self, execution_id: str) -> asyncio.Queue:
        """
        Subscribe to progress updates for an execution

        Returns a queue that will receive messages
        """
        queue = asyncio.Queue()
        self.connections[execution_id].add(queue)

        logger.info(f"New SSE subscription for execution {execution_id}")
        logger.debug(f"Total connections for {execution_id}: {len(self.connections[execution_id])}")

        return queue

    async def unsubscribe(self, execution_id: str, queue: asyncio.Queue):
        """Unsubscribe from progress updates"""
        if execution_id in self.connections:
            self.connections[execution_id].discard(queue)

            # Clean up if no more connections
            if not self.connections[execution_id]:
                del self.connections[execution_id]

            logger.info(f"SSE unsubscribed for execution {execution_id}")

    async def broadcast(self, execution_id: str, message: dict):
        """
        Broadcast a message to all subscribers of an execution

        Args:
            execution_id: The execution ID to broadcast to
            message: Dictionary containing the message data
        """
        if execution_id not in self.connections:
            logger.debug(f"No subscribers for execution {execution_id}, skipping broadcast")
            return

        queues = self.connections[execution_id].copy()
        logger.info(f"Broadcasting to {len(queues)} subscribers for {execution_id}")

        for queue in queues:
            try:
                await queue.put(message)
            except Exception as e:
                logger.error(f"Error broadcasting to queue: {e}")

    def get_connection_count(self, execution_id: str = None) -> int:
        """Get number of active connections"""
        if execution_id:
            return len(self.connections.get(execution_id, set()))
        return sum(len(queues) for queues in self.connections.values())


# Global SSE manager instance
sse_manager = SSEManager()
