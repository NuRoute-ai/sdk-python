"""
Regression tests for a class of bug found auditing the SDK docs against actual behavior: the
gateway returns snake_case for some endpoints (project policy/budget, invite info) and
camelCase for others, and get_invite_info() returned whatever the wire sent with no
translation — so `info["orgName"]` was a KeyError even though the declared TypedDict promised
it. Project policy/budget already round-trip snake_case directly (matching this SDK's other
Python-idiomatic snake_case kwargs), so only get_invite_info() needed a fix.
"""

from __future__ import annotations

import json

import httpx
import respx

from nuroute import NuRouteClient


@respx.mock
def test_get_invite_info_translates_snake_case_response():
    respx.get("http://example.test/auth/invite/info").mock(
        return_value=httpx.Response(
            200,
            json={
                "org_name": "Acme",
                "email": "a@acme.test",
                "role": "developer",
                "expires_at": 1234567890,
            },
        )
    )

    client = NuRouteClient(api_key="x", base_url="http://example.test")
    info = client.auth.get_invite_info("tok")
    client.close()

    assert info == {
        "orgName": "Acme",
        "email": "a@acme.test",
        "role": "developer",
        "expiresAt": 1234567890,
    }
    assert "orgId" not in info


@respx.mock
def test_project_budget_and_policy_already_round_trip_snake_case():
    respx.get("http://example.test/v1/projects/proj_1/budget").mock(
        return_value=httpx.Response(
            200,
            json={
                "project_id": "proj_1", "org_id": "org_1",
                "monthly_usd": 100, "alert_pct": 80, "hard_limit": True, "current_spend": 42.5,
            },
        )
    )
    respx.put("http://example.test/v1/projects/proj_1/policy").mock(
        return_value=httpx.Response(200, json={"success": True})
    )

    client = NuRouteClient(api_key="x", base_url="http://example.test")
    budget = client.project("proj_1").get_budget()
    client.project("proj_1").set_policy(max_tokens=4096, allowed_models=["gpt-4o"])
    client.close()

    assert budget["current_spend"] == 42.5
    assert budget["monthly_usd"] == 100

    sent_body = json.loads(respx.calls[-1].request.content)
    assert sent_body == {"max_tokens": 4096, "allowed_models": ["gpt-4o"]}
