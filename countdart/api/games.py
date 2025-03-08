"""REST API endpoint for games.
Provides a game context for the user to interact with the procedures.
It automatically loads the current active dartboard and camera.
"""

import asyncio
import json

import redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from countdart.database.crud import dartboard as crud_dartboard
from countdart.settings import settings

router = APIRouter(prefix="/game", tags=["Games"])


@router.websocket("/ws")
async def game_context_endpoint(websocket: WebSocket):
    """Will return websocket, which sends information about the current active dartboard
    and its detections

    Args:
        websocket (WebSocket): _description_
    """
    await websocket.accept()
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    old_msg = ""
    # Get active dartboard
    dartboard = crud_dartboard.get_dartboards(active=True)
    while len(dartboard) != 1:
        if len(dartboard) > 1:
            message = json.dumps(
                {"message_type": "error", "payload": "Multiple active dartboards found"}
            )
        else:
            message = json.dumps(
                {"message_type": "error", "payload": "No active dartboard found"}
            )
        if message != old_msg:
            await websocket.send_text(message)
            old_msg = message
        await asyncio.sleep(2)
        dartboard = crud_dartboard.get_dartboards(active=True)

    result_key = f"dartboard_{dartboard[0].id}_result"

    try:
        while True:
            # Add this try block to yield back control to fastapi and allow
            # context switch and serve multiple request concurrently
            # receive_text is also needed to update state of connection:
            # https://github.com/tiangolo/fastapi/discussions/9031#discussion-4911299
            # Important: you need to wait as long as 0.001, otherwise disconnections
            # will not be received, because the wait time is too short
            try:
                _ = await asyncio.wait_for(websocket.receive_text(), 0.001)
            except asyncio.TimeoutError:
                pass

            # Get cls from redis
            msg = r.get(result_key)
            if msg and msg != old_msg:
                old_msg = msg
                await websocket.send_text(
                    json.dumps({"message_type": "result", "payload": msg.decode()})
                )
                continue
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        pass
