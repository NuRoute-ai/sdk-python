"""
Regression tests for the AICP -> NuRoute rebrand's deprecated aliases.

AICPClient / AsyncAICPClient / AICPError must keep behaving exactly like their NuRoute-named
counterparts for existing customer code that hasn't migrated yet. A silent behavior difference
here would land in every integration still importing the old names.
"""

from __future__ import annotations

import warnings

import httpx
import pytest
import respx

from nuroute import (
    AICPClient,
    AICPError,
    AsyncAICPClient,
    AsyncNuRouteClient,
    NuRouteClient,
    NuRouteError,
)


# ─── AICPClient ─────────────────────────────────────────────────────────────────

def test_aicp_client_is_a_nuroute_client_subclass():
    client = AICPClient(api_key="aicp-test")
    assert isinstance(client, NuRouteClient)
    assert isinstance(client, AICPClient)
    client.close()


def test_constructing_aicp_client_warns_deprecation():
    with pytest.warns(DeprecationWarning, match="AICPClient is deprecated"):
        client = AICPClient(api_key="aicp-test")
    client.close()


def test_aicp_client_behaves_identically_to_nuroute_client():
    with respx.mock:
        respx.get("http://example.test/health").mock(
            return_value=httpx.Response(200, json={"status": "ok", "version": "1.2.3"})
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            old_client = AICPClient(api_key="aicp-test", base_url="http://example.test")
        new_client = NuRouteClient(api_key="aicp-test", base_url="http://example.test")

        old_result = old_client.health()
        new_result = new_client.health()

        assert old_result == new_result == {"status": "ok", "version": "1.2.3"}

        old_client.close()
        new_client.close()


# ─── AsyncAICPClient ────────────────────────────────────────────────────────────

def test_async_aicp_client_is_an_async_nuroute_client_subclass():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        client = AsyncAICPClient(api_key="aicp-test")
    assert isinstance(client, AsyncNuRouteClient)
    assert isinstance(client, AsyncAICPClient)


def test_constructing_async_aicp_client_warns_deprecation():
    with pytest.warns(DeprecationWarning, match="AsyncAICPClient is deprecated"):
        AsyncAICPClient(api_key="aicp-test")


@pytest.mark.asyncio
async def test_async_aicp_client_behaves_identically_to_async_nuroute_client():
    with respx.mock:
        respx.get("http://example.test/health").mock(
            return_value=httpx.Response(200, json={"status": "ok", "version": "1.2.3"})
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            old_client = AsyncAICPClient(api_key="aicp-test", base_url="http://example.test")
        new_client = AsyncNuRouteClient(api_key="aicp-test", base_url="http://example.test")

        old_result = await old_client.health()
        new_result = await new_client.health()

        assert old_result == new_result == {"status": "ok", "version": "1.2.3"}

        await old_client.aclose()
        await new_client.aclose()


# ─── AICPError ──────────────────────────────────────────────────────────────────

def test_aicp_error_is_the_exact_same_class_as_nuroute_error():
    # A plain alias (`AICPError = NuRouteError`), not a subclass — so errors raised internally
    # as NuRouteError still satisfy `except AICPError` / `isinstance(exc, AICPError)` for
    # existing user code written against the old name.
    assert AICPError is NuRouteError


def test_errors_raised_by_the_client_satisfy_isinstance_aicp_error():
    with respx.mock:
        respx.get("http://example.test/v1/models").mock(
            return_value=httpx.Response(
                400, json={"error": {"message": "bad request", "type": "bad_request", "code": "X"}}
            )
        )

        client = NuRouteClient(api_key="aicp-test", base_url="http://example.test")
        with pytest.raises(AICPError) as exc_info:
            client.models.list()

        assert exc_info.value.status == 400
        assert exc_info.value.error_type == "bad_request"
        client.close()
