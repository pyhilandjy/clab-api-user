from fastapi import HTTPException
import sentry_sdk
from typing import Callable, Any


def raise_http_500(e: Exception, detail: str = "Internal Server Error"):
    sentry_sdk.capture_exception(e)
    raise HTTPException(status_code=500, detail=detail)


def raise_http_404(detail: str = "Not Found"):
    raise HTTPException(status_code=404, detail=detail)


def raise_http_400(detail: str = "Bad Request"):
    raise HTTPException(status_code=400, detail=detail)


def raise_http_401(detail: str = "Unauthorized"):
    raise HTTPException(status_code=401, detail=detail)


def raise_http_403(detail: str = "Forbidden"):
    raise HTTPException(status_code=403, detail=detail)


def capture_message(message: str, level: str = "info"):
    """
    Log a non-exception warning or informational message to Sentry.

    Args:
        message (str): The message to log.
        level (str): The severity level of the message (e.g., "info", "warning", "error").
    """
    sentry_sdk.capture_message(message, level=level)


def safe_execute(
    fn: Callable[..., Any], *args, exception_detail: str = "처리 중 오류 발생", **kwargs
):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        raise_http_500(e, detail=exception_detail)
