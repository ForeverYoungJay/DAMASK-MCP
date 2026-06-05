"""Optional authentication helpers for hosted DAMASK MCP deployments."""

from __future__ import annotations

from dataclasses import dataclass
import os
import secrets
from typing import Any


@dataclass(frozen=True)
class FallbackAccessToken:
    """Small AccessToken stand-in for tests without FastMCP auth installed."""

    token: str
    client_id: str
    scopes: list[str]


class EnvironmentBearerTokenVerifier:
    """FastMCP token verifier backed by one environment variable."""

    def __new__(cls, token: str, env_var: str = "MCP_BEARER_TOKEN") -> Any:
        try:
            from fastmcp.server.auth import AccessToken, TokenVerifier
        except ImportError:
            class _FallbackVerifier:
                async def verify_token(self, candidate: str) -> FallbackAccessToken | None:
                    if not secrets.compare_digest(candidate, token):
                        return None
                    return FallbackAccessToken(token=candidate, client_id=env_var, scopes=[])

            return _FallbackVerifier()

        class _Verifier(TokenVerifier):  # type: ignore[misc, valid-type]
            async def verify_token(self, candidate: str) -> AccessToken | None:  # type: ignore[override]
                if not secrets.compare_digest(candidate, token):
                    return None
                return AccessToken(token=candidate, client_id=env_var, scopes=[])

        return _Verifier()


def auth_provider_from_environment(env_var: str = "MCP_BEARER_TOKEN") -> Any | None:
    """Return a FastMCP auth provider when a bearer token env var is configured."""
    token = os.environ.get(env_var)
    if not token:
        return None
    return EnvironmentBearerTokenVerifier(token=token, env_var=env_var)
