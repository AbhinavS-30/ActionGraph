"""Bound raw HTTP bodies before FastAPI parses JSON or runs dependencies."""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

MAX_REQUEST_BYTES = 2 * 1024 * 1024
LIMIT_DETAIL = "Request body exceeds 2097152 bytes (2 MiB). Send a smaller batch."


class RequestBodyLimit:
    def __init__(self, app: ASGIApp, max_bytes: int = MAX_REQUEST_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        response = JSONResponse({"detail": LIMIT_DETAIL}, status_code=413)
        for name, value in scope.get("headers", []):
            # Header is only an early rejection hint; always count actual bytes.
            if name.lower() == b"content-length" and value.isdigit():
                # Compare decimal bytes to avoid integer-conversion limits on bad headers.
                size = value.lstrip(b"0") or b"0"
                cap = str(self.max_bytes).encode("ascii")
                if len(size) > len(cap) or (len(size) == len(cap) and size > cap):
                    await response(scope, receive, send)
                    return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_bytes:
                await response(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)
