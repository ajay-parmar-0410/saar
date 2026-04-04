"""Supabase client initialization."""

import os
from functools import lru_cache

from supabase import Client, create_client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Return a cached Supabase client using the service role key.

    Uses service role key for backend operations (bypasses RLS).
    """
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)


@lru_cache(maxsize=1)
def get_supabase_anon_client() -> Client:
    """Return a cached Supabase client using the anon key.

    Uses anon key for operations that should respect RLS.
    """
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)
