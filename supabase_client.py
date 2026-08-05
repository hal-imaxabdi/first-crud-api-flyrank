"""
supabase_client.py
-------------------
Creates a single shared Supabase client using credentials from .env.

Keeping this in its own file (rather than inline in main.py) means
main.py and the auth routes just import `supabase` and use it -- they
never touch environment variables or client setup directly.
"""

import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
