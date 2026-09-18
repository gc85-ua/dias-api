import contextvars
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        request_id_var.set(request_id)

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response
