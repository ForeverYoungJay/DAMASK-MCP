import asyncio

from damask_mcp.mcp_servers.auth import auth_provider_from_environment


def test_auth_provider_is_disabled_without_bearer_token(monkeypatch):
    monkeypatch.delenv("MCP_BEARER_TOKEN", raising=False)

    assert auth_provider_from_environment() is None


def test_auth_provider_accepts_configured_bearer_token(monkeypatch):
    monkeypatch.setenv("MCP_BEARER_TOKEN", "secret-token")
    provider = auth_provider_from_environment()

    accepted = asyncio.run(provider.verify_token("secret-token"))
    rejected = asyncio.run(provider.verify_token("wrong-token"))

    assert accepted is not None
    assert accepted.client_id == "MCP_BEARER_TOKEN"
    assert rejected is None
