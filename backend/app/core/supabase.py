from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


def _create() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Singleton client for request handlers (one process-wide connection)."""
    return _create()


def new_supabase() -> Client:
    """A fresh, independent client — use it from background workers.

    The pipeline runs in a separate thread and writes progress frequently. Sharing
    the request-handler singleton means two threads hit one httpx HTTP/2 connection
    at once, which on Windows surfaces as 'WinError 10035' / hung requests. Giving
    the worker its own client keeps the two connections isolated.
    """
    return _create()
