from typing import Dict, Set
from fastapi import WebSocket
import asyncio
import json

class WSManager:

    def __init__(self) -> None:
        self.job_connections: Dict[int, Set[WebSocket]] = {}
        self.session_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect_job(self, job_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            self.job_connections.setdefault(job_id, set()).add(websocket)

    async def disconnect_job(self, job_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self.job_connections.get(job_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if len(conns) == 0:
                    self.job_connections.pop(job_id, None)

    async def connect_session(self, session_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self.session_connections.setdefault(session_id, set()).add(websocket)

    async def disconnect_session(self, session_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self.session_connections.get(session_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if len(conns) == 0:
                    self.session_connections.pop(session_id, None)

    async def broadcast_job(self, job_id: int, payload: dict) -> None:
        conns = list(self.job_connections.get(job_id, set()))
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect_job(job_id, ws)

    async def broadcast_session(self, session_id: str, payload: dict) -> None:
        conns = list(self.session_connections.get(session_id, set()))
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect_session(session_id, ws)
ws_manager = WSManager()