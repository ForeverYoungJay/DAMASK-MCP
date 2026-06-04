"""Optional authentication helpers for hosted DAMASK MCP deployments."""

from __future__ import annotations

import os
import secrets
from typing import Any


class EnvironmentBearerTokenVerifier:
    """FastMCP token verifier backed by one environment variable."""

    def __new__(cls, token: str, env_var: str = "MCP_BEARER_TOKEN") -> Any:
        try:
            from fastmcp.server.auth import AccessToken, TokenVerifier
        except ImportError as exc:
            raise RuntimeError("FastMCP auth support is required when MCP_BEARER_TOKEN is set.") from exc

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
