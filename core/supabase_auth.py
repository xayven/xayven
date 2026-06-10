import os
import secrets
import logging
from typing import Dict, Any

import requests
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

        if not self.anon_key:
            raise RuntimeError("SUPABASE_ANON_KEY is not configured")

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

    def verify_access_token(self, access_token: str) -> Dict[str, Any]:
        logger.error("VERIFY_ACCESS_TOKEN CALLED")
        logger.error("TOKEN PREFIX: %s", access_token[:40])

        response = requests.get(
            f"{self.url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": self.anon_key,
            },
            timeout=30,
        )

        logger.error("SUPABASE STATUS: %s", response.status_code)
        logger.error("SUPABASE BODY: %s", response.text)

        if response.status_code != 200:
            raise ValueError(
                f"Supabase rejected token. "
                f"Status={response.status_code} "
                f"Body={response.text}"
            )

        return response.json()

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
                username = f"{username}_{secrets.token_hex(2)}"

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

    def login_with_google_token(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        logger.error("LOGIN_WITH_GOOGLE_TOKEN CALLED")

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
