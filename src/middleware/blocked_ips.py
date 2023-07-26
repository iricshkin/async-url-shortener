from typing import Callable

from fastapi import Request, Response, status

from services import my_logger

logger = my_logger.get_logger(__name__)


class BlockedIpsMiddleware:
    def __init__(self, blocked_ips: list[str]):
        self._blocked_ips = blocked_ips

    async def __call__(
        self, request: Request, call_next: Callable
    ) -> Response:
        if request.client and request.client.host not in self._blocked_ips:
            return await call_next(request)
        logger.info(
            'Request from client %s in blocked ips', request.client.host
        )
        return Response('Acsess denied', status_code=status.HTTP_403_FORBIDDEN)
