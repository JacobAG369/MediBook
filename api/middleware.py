# medibook/api/middleware.py
"""
Middleware de FastAPI para logging de requests y responses.
"""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("medibook.api.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que loggea cada request HTTP entrante con:
    - Método HTTP y ruta
    - Tiempo de respuesta en ms
    - Código de estado
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        # Loggear request entrante
        logger.info(
            "→ %s %s",
            request.method,
            request.url.path,
        )

        response: Response = await call_next(request)

        # Calcular duración
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Loggear response
        logger.info(
            "← %s %s → %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
