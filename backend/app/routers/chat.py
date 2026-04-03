from __future__ import annotations

import logging

from chatkit.server import StreamingResult
from fastapi import APIRouter, Request
from fastapi.responses import Response, StreamingResponse

from app.services.chat_server import get_server

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/exam-assistant/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    try:
        payload = await request.body()
        server = get_server()
        result = await server.process(payload, context={"request": request})

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")

        return Response(content=result.json, media_type="application/json")
    except Exception as e:
        logger.error(f"Error processing chatkit request: {e}")
        raise
