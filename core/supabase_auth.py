import os
import secrets
import logging
from typing import Optional, Dict, Any

from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseAuth:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager

        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.url:
            raise RuntimeError("SUPABASE_URL is not configured")

        if not self.service_role_key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not configured")

        self.client: Client = create_client(
            self.url,
            self.service_role_key,
        )

    def _username_from_email(self, email: str) -> str:
        username = email.split("@")[0].strip().lower()

        username = "".join(
            c for c in username
            if c.isalnum() or c in ("_", "-", ".")
        )

        if not username:
            username = f"user_{secrets.token_hex(4)}"

        return username

    def verify_access_token(self, access_token: str):
        import requests

        response = requests.get(
            f"{self.url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": self.anon_key,
            },
        )

        print("STATUS:", response.status_code)
        print("BODY:", response.text)

        response.raise_for_status()
        return response.json()
        try:
            logger.info("TOKEN RECEIVED: %s", access_token[:50])

            user = self.client.auth.get_user(access_token)

            logger.info("USER RESULT: %s", user)

            if not user or not user.user:
                raise ValueError("Invalid Supabase token")

            return user.user.model_dump()

        except Exception as e:
            logger.exception("SUPABASE ERROR")
            logger.exception("Supabase token verification failed")
            raise

        try:
            user = self.client.auth.get_user(access_token)

            if not user or not user.user:
                raise ValueError("Invalid Supabase token")

            return user.user.model_dump()

        except Exception as e:
            logger.exception("Supabase token verification failed")
            raise ValueError(f"Invalid token: {e}")

    def find_or_create_helix_user(self, user_data: Dict[str, Any]) -> str:
        email = (user_data.get("email") or "").strip().lower()

        if not email:
            raise ValueError("Email not found in Supabase user")

        username = self._username_from_email(email)

        if username not in self.auth_manager.users:
            random_password = secrets.token_urlsafe(32)

            created = self.auth_manager.create_user(
                username=username,
                password=random_password,
                is_admin=False,
            )

            if not created:
                suffix = secrets.token_hex(2)

                username = f"{username}_{suffix}"

                self.auth_manager.create_user(
                    username=username,
                    password=random_password,
                    is_admin=False,
                )

            logger.info(
                "Created HELIX user from Google login: %s",
                username,
            )

        return username
    
    raise Exception("SUPABASE_AUTH_V2")

    def login_with_google_token(self, access_token: str) -> Dict[str, Any]:
        user_data = self.verify_access_token(access_token)

        username = self.find_or_create_helix_user(user_data)

        session_token = self.auth_manager.create_session_trusted(
            username
        )

        return {
            "ok": True,
            "username": username,
            "email": user_data.get("email"),
            "session_token": session_token,
            "provider": "google",
        }
