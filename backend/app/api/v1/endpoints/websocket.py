"""WebSocket endpoints for real-time updates."""

import asyncio
import json
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from jose import JWTError

from app.core.security import decode_token
from app.repositories.user import UserRepository, get_user_repository

logger = structlog.get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self) -> None:
        # Map of user_id -> list of websocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}
        # Map of project_id -> list of (user_id, websocket) subscriptions
        self.project_subscriptions: dict[str, list[tuple[str, WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept a WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info("WebSocket connected", user_id=user_id)

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from project subscriptions
        for project_id, subs in list(self.project_subscriptions.items()):
            self.project_subscriptions[project_id] = [
                (uid, ws) for uid, ws in subs if ws != websocket
            ]
            if not self.project_subscriptions[project_id]:
                del self.project_subscriptions[project_id]

        logger.info("WebSocket disconnected", user_id=user_id)

    def subscribe_to_project(
        self, websocket: WebSocket, user_id: str, project_id: str
    ) -> None:
        """Subscribe to project updates."""
        if project_id not in self.project_subscriptions:
            self.project_subscriptions[project_id] = []
        self.project_subscriptions[project_id].append((user_id, websocket))
        logger.info("Subscribed to project", user_id=user_id, project_id=project_id)

    def unsubscribe_from_project(
        self, websocket: WebSocket, user_id: str, project_id: str
    ) -> None:
        """Unsubscribe from project updates."""
        if project_id in self.project_subscriptions:
            self.project_subscriptions[project_id] = [
                (uid, ws)
                for uid, ws in self.project_subscriptions[project_id]
                if ws != websocket
            ]
            if not self.project_subscriptions[project_id]:
                del self.project_subscriptions[project_id]
        logger.info("Unsubscribed from project", user_id=user_id, project_id=project_id)

    async def send_personal_message(self, message: dict, user_id: str) -> None:
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error("Failed to send message", user_id=user_id, error=str(e))

    async def broadcast_to_project(self, message: dict, project_id: str) -> None:
        """Broadcast a message to all users subscribed to a project."""
        if project_id in self.project_subscriptions:
            for user_id, websocket in self.project_subscriptions[project_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(
                        "Failed to broadcast",
                        project_id=project_id,
                        user_id=user_id,
                        error=str(e),
                    )

    async def broadcast_job_progress(
        self,
        project_id: str,
        job_id: str,
        progress: float,
        status: str,
        message: str | None = None,
        stats: dict | None = None,
    ) -> None:
        """Broadcast job progress update."""
        await self.broadcast_to_project(
            {
                "type": "job.progress",
                "project_id": project_id,
                "job_id": job_id,
                "progress": progress,
                "status": status,
                "message": message,
                "stats": stats,
            },
            project_id,
        )

    async def broadcast_job_completed(
        self,
        project_id: str,
        job_id: str,
        stats: dict,
    ) -> None:
        """Broadcast job completion."""
        await self.broadcast_to_project(
            {
                "type": "job.completed",
                "project_id": project_id,
                "job_id": job_id,
                "stats": stats,
            },
            project_id,
        )

    async def broadcast_job_failed(
        self,
        project_id: str,
        job_id: str,
        error: str,
    ) -> None:
        """Broadcast job failure."""
        await self.broadcast_to_project(
            {
                "type": "job.failed",
                "project_id": project_id,
                "job_id": job_id,
                "error": error,
            },
            project_id,
        )


# Global connection manager instance
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager


async def authenticate_websocket(
    token: str,
) -> str | None:
    """Authenticate a WebSocket connection using JWT token."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        return user_id
    except (JWTError, Exception):
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """
    WebSocket endpoint for real-time updates.

    Connect with: ws://host/api/v1/ws?token=<access_token>

    Message types:
    - subscribe: {"action": "subscribe", "project_id": "..."}
    - unsubscribe: {"action": "unsubscribe", "project_id": "..."}
    - ping: {"action": "ping"}

    Server sends:
    - job.progress: Progress updates for scrape jobs
    - job.completed: Job completion notification
    - job.failed: Job failure notification
    - pong: Response to ping
    """
    # Authenticate
    user_id = await authenticate_websocket(token)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "ping":
                    await websocket.send_json({"type": "pong"})

                elif action == "subscribe":
                    project_id = message.get("project_id")
                    if project_id:
                        manager.subscribe_to_project(websocket, user_id, project_id)
                        await websocket.send_json({
                            "type": "subscribed",
                            "project_id": project_id,
                        })

                elif action == "unsubscribe":
                    project_id = message.get("project_id")
                    if project_id:
                        manager.unsubscribe_from_project(websocket, user_id, project_id)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "project_id": project_id,
                        })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}",
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        manager.disconnect(websocket, user_id)


@router.websocket("/ws/jobs/{project_id}")
async def job_progress_websocket(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """
    WebSocket endpoint for project job progress.

    Automatically subscribes to the specified project.
    """
    # Authenticate
    user_id = await authenticate_websocket(token)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(websocket, user_id)
    manager.subscribe_to_project(websocket, user_id, project_id)

    try:
        # Send confirmation
        await websocket.send_json({
            "type": "connected",
            "project_id": project_id,
        })

        while True:
            # Keep connection alive, handle pings
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                if message.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        manager.disconnect(websocket, user_id)
