"""Asynchronous NuRoute client."""

from __future__ import annotations

import json as _json
import warnings
from collections.abc import AsyncIterator
from typing import Any

import httpx

from .errors import NuRouteError
from .types import (
    ApiKey,
    AuthResponse,
    ChatCompletionResponse,
    ChatMessage,
    CreateKeyResponse,
    InviteInfo,
    InviteResponse,
    Invitation,
    ModelInfo,
    Period,
    Project,
    ProviderConfig,
    ProviderTestResult,
    ReplayData,
    RequestDetail,
    RequestSummary,
    RoutingAlias,
    RoutingConfig,
    RoutingDecision,
    RoutingDecisionSummary,
    TimelineEvent,
    UsageBreakdown,
    UsageOverview,
    UsageRecommendations,
    UsageSeriesPoint,
    UserRole,
)


# ─── Namespace base ───────────────────────────────────────────────────────────

class _Namespace:
    def __init__(self, client: "AsyncNuRouteClient") -> None:
        self._c = client


# ─── auth ─────────────────────────────────────────────────────────────────────

class _Auth(_Namespace):
    async def signup(
        self,
        org_name: str,
        email: str,
        password: str,
        user_name: str | None = None,
    ) -> AuthResponse:
        return await self._c._req("POST", "/auth/signup", json={
            "org_name":  org_name,
            "email":     email,
            "password":  password,
            "user_name": user_name,
        })

    async def login(self, email: str, password: str) -> AuthResponse:
        return await self._c._req("POST", "/auth/login", json={
            "email": email, "password": password,
        })

    async def get_invite_info(self, token: str) -> InviteInfo:
        # See the sync client's get_invite_info for why this translation exists.
        w = await self._c._req("GET", "/auth/invite/info", params={"token": token})
        return {
            "orgName":   w["org_name"],
            "email":     w["email"],
            "role":      w["role"],
            "expiresAt": w["expires_at"],
        }

    async def accept_invite(self, token: str, name: str, password: str) -> AuthResponse:
        return await self._c._req("POST", "/auth/invite/accept", json={
            "token": token, "name": name, "password": password,
        })


# ─── members ──────────────────────────────────────────────────────────────────

class _Members(_Namespace):
    async def list(self) -> dict[str, list]:
        return await self._c._req("GET", "/auth/members")

    async def list_invitations(self) -> dict[str, list[Invitation]]:
        return await self._c._req("GET", "/auth/invitations")

    async def invite(self, email: str, role: UserRole) -> InviteResponse:
        return await self._c._req("POST", "/auth/invite", json={"email": email, "role": role})


# ─── projects ─────────────────────────────────────────────────────────────────

class _Projects(_Namespace):
    async def list(self) -> dict[str, list[Project]]:
        return await self._c._req("GET", "/projects")

    async def get(self, id: str) -> Project:
        return await self._c._req("GET", f"/projects/{id}")

    async def create(
        self,
        name: str,
        slug: str | None = None,
        description: str | None = None,
    ) -> Project:
        return await self._c._req("POST", "/projects", json={
            "name": name, "slug": slug, "description": description,
        })

    async def update(
        self,
        id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> Project:
        body: dict[str, Any] = {}
        if name is not None:        body["name"]        = name
        if description is not None: body["description"] = description
        return await self._c._req("PATCH", f"/projects/{id}", json=body)

    async def delete(self, id: str) -> dict[str, bool]:
        return await self._c._req("DELETE", f"/projects/{id}")


# ─── keys ─────────────────────────────────────────────────────────────────────

class _Keys(_Namespace):
    async def list(self, project_id: str | None = None) -> dict[str, list[ApiKey]]:
        params = {"project_id": project_id} if project_id else None
        return await self._c._req("GET", "/keys", params=params)

    async def create(
        self,
        name: str,
        project_id: str | None = None,
        scopes: list[str] | None = None,
        expires_at: int | None = None,
    ) -> CreateKeyResponse:
        return await self._c._req("POST", "/keys", json={
            "name": name, "project_id": project_id,
            "scopes": scopes, "expires_at": expires_at,
        })

    async def delete(self, id: str) -> dict[str, bool]:
        return await self._c._req("DELETE", f"/keys/{id}")


# ─── providers ────────────────────────────────────────────────────────────────

class _Providers(_Namespace):
    async def list(self) -> dict[str, list[ProviderConfig]]:
        return await self._c._req("GET", "/v1/providers")

    async def add(
        self,
        provider: str,
        api_key: str,
        enabled_models: list[str] | None = None,
    ) -> dict[str, bool]:
        return await self._c._req("POST", "/v1/providers", json={
            "provider": provider, "api_key": api_key,
            "enabled_models": enabled_models or [],
        })

    async def delete(self, provider: str) -> dict[str, bool]:
        return await self._c._req("DELETE", f"/v1/providers/{provider}")

    async def enable(self, provider: str) -> dict[str, bool]:
        return await self._c._req("PATCH", f"/v1/providers/{provider}/enable")

    async def disable(self, provider: str) -> dict[str, bool]:
        return await self._c._req("PATCH", f"/v1/providers/{provider}/disable")

    async def test(self, provider: str) -> ProviderTestResult:
        return await self._c._req("POST", f"/v1/providers/{provider}/test")


# ─── routing ──────────────────────────────────────────────────────────────────

class _Routing(_Namespace):
    async def get_config(self) -> RoutingConfig:
        return await self._c._req("GET", "/v1/routing/config")

    async def update_config(self, config: dict[str, Any]) -> dict[str, bool]:
        return await self._c._req("PUT", "/v1/routing/config", json=config)

    async def list_history(
        self,
        limit: int = 50,
        offset: int = 0,
        provider: str | None = None,
        strategy: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if provider: params["provider"] = provider
        if strategy: params["strategy"] = strategy
        if status:   params["status"]   = status
        return await self._c._req("GET", "/v1/routing/history", params=params)

    async def get_decision(self, id: str) -> RoutingDecision:
        return await self._c._req("GET", f"/v1/routing/history/{id}")

    async def list_aliases(self) -> list[RoutingAlias]:
        return await self._c._req("GET", "/v1/routing/aliases")

    async def set_alias(self, alias: str, model: str) -> RoutingAlias:
        return await self._c._req("PUT", "/v1/routing/aliases", json={"alias": alias, "model": model})

    async def delete_alias(self, alias: str) -> None:
        await self._c._req("DELETE", f"/v1/routing/aliases/{alias}")


# ─── requests ─────────────────────────────────────────────────────────────────

class _Requests(_Namespace):
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
        provider: str | None = None,
        strategy: str | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if search:    params["search"]    = search
        if provider:  params["provider"]  = provider
        if strategy:  params["strategy"]  = strategy
        if status:    params["status"]    = status
        if date_from: params["date_from"] = date_from
        if date_to:   params["date_to"]   = date_to
        return await self._c._req("GET", "/v1/requests", params=params)

    async def get(self, id: str) -> RequestDetail:
        return await self._c._req("GET", f"/v1/requests/{id}")

    async def get_timeline(self, id: str) -> dict[str, list[TimelineEvent]]:
        return await self._c._req("GET", f"/v1/requests/{id}/timeline")

    async def replay(self, id: str) -> ReplayData:
        return await self._c._req("POST", f"/v1/requests/{id}/replay")


# ─── usage ────────────────────────────────────────────────────────────────────

class _Usage(_Namespace):
    async def overview(self, period: Period = "24h") -> UsageOverview:
        return await self._c._req("GET", "/v1/usage/overview", params={"period": period})

    async def series(self, period: Period = "24h") -> dict[str, list[UsageSeriesPoint]]:
        return await self._c._req("GET", "/v1/usage/series", params={"period": period})

    async def breakdown(self, period: Period = "24h") -> UsageBreakdown:
        return await self._c._req("GET", "/v1/usage/breakdown", params={"period": period})

    async def recommendations(self, period: Period = "24h") -> UsageRecommendations:
        return await self._c._req("GET", "/v1/usage/recommendations", params={"period": period})


# ─── models ───────────────────────────────────────────────────────────────────

class _Models(_Namespace):
    async def list(self) -> dict[str, Any]:
        return await self._c._req("GET", "/v1/models")


# ─── chat ─────────────────────────────────────────────────────────────────────

class _Chat(_Namespace):
    async def complete(
        self,
        model: str,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        provider: str | None = None,
    ) -> ChatCompletionResponse:
        body: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
        if temperature is not None: body["temperature"] = temperature
        if max_tokens is not None:  body["max_tokens"]  = max_tokens
        if provider is not None:    body["provider"]    = provider
        return await self._c._req("POST", "/v1/chat/completions", json=body)

    async def stream(
        self,
        model: str,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        provider: str | None = None,
    ) -> AsyncIterator[str]:
        body: dict[str, Any] = {"model": model, "messages": messages, "stream": True}
        if temperature is not None: body["temperature"] = temperature
        if max_tokens is not None:  body["max_tokens"]  = max_tokens
        if provider is not None:    body["provider"]    = provider
        async for chunk in self._c._stream("/v1/chat/completions", body):
            yield chunk


# ─── Main client ──────────────────────────────────────────────────────────────

class AsyncNuRouteClient:
    """
    Asynchronous NuRoute client. Use with ``async/await`` and ``async for``.

    Args:
        api_key:  Bearer token — JWT session token or ``aicp-…`` API key.
        base_url: Gateway base URL. Defaults to ``http://localhost:3000``.
        timeout:  Request timeout in seconds. Defaults to 30.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "http://localhost:3000",
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key  = api_key
        self._timeout  = timeout
        self._http     = httpx.AsyncClient(timeout=timeout)

        self.auth      = _Auth(self)
        self.chat      = _Chat(self)
        self.keys      = _Keys(self)
        self.members   = _Members(self)
        self.models    = _Models(self)
        self.projects  = _Projects(self)
        self.providers = _Providers(self)
        self.requests  = _Requests(self)
        self.routing   = _Routing(self)
        self.usage     = _Usage(self)

    def project(self, project_id: str) -> "AsyncProjectClient":
        """Return an async sub-client scoped to a single project."""
        return AsyncProjectClient(project_id, self)

    def set_api_key(self, api_key: str) -> None:
        self._api_key = api_key

    async def health(self) -> dict[str, str]:
        return await self._req("GET", "/health")

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncNuRouteClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    # ─── Internal helpers ────────────────────────────────────────────────────

    @property
    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    async def _req(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = self._base_url + path
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            res = await self._http.request(
                method,
                url,
                headers=self._headers,
                json=json,
                params=clean_params or None,
            )
        except httpx.RequestError as exc:
            raise NuRouteError(0, str(exc), "network_error") from exc

        if res.status_code == 204:
            return None

        if not res.is_success:
            body = {}
            try:
                body = res.json()
            except Exception:
                pass
            msg   = body.get("error", {}).get("message", f"HTTP {res.status_code}")
            etype = body.get("error", {}).get("type",    "api_error")
            code  = body.get("error", {}).get("code",    None)
            raise NuRouteError(res.status_code, msg, etype, code)

        return res.json()

    async def _stream(self, path: str, body: dict[str, Any]) -> AsyncIterator[str]:
        url = self._base_url + path
        try:
            async with self._http.stream("POST", url, headers=self._headers, json=body) as res:
                if not res.is_success:
                    content = await res.aread()
                    try:
                        err = _json.loads(content)
                    except Exception:
                        err = {}
                    msg   = err.get("error", {}).get("message", f"HTTP {res.status_code}")
                    etype = err.get("error", {}).get("type",    "api_error")
                    raise NuRouteError(res.status_code, msg, etype)

                async for line in res.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        return
                    try:
                        parsed = _json.loads(data)
                        delta  = parsed.get("choices", [{}])[0].get("delta", {}).get("content")
                        if delta:
                            yield delta
                    except Exception:
                        pass
        except httpx.RequestError as exc:
            raise NuRouteError(0, str(exc), "network_error") from exc


# ─── AsyncProjectClient — project-scoped sub-client (Epic F) ──────────────────

class AsyncProjectClient:
    """Async scoped sub-client for a single project's runtime configuration."""

    def __init__(self, project_id: str, _client: AsyncNuRouteClient) -> None:
        self._pid = project_id
        self._c   = _client

    # ── Connections ───────────────────────────────────────────────────────────

    async def list_connections(self) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/connections")

    async def add_connection(
        self,
        provider_id: str,
        *,
        enabled: bool = True,
        allowed_models: list[str] | None = None,
    ) -> dict:
        return await self._c._req("POST", f"/v1/projects/{self._pid}/connections", json={
            "provider_id":    provider_id,
            "enabled":        enabled,
            "allowed_models": allowed_models or [],
        })

    async def enable_connection(self, provider_id: str) -> dict:
        return await self._c._req("PATCH", f"/v1/projects/{self._pid}/connections/{provider_id}/enable")

    async def disable_connection(self, provider_id: str) -> dict:
        return await self._c._req("PATCH", f"/v1/projects/{self._pid}/connections/{provider_id}/disable")

    async def remove_connection(self, provider_id: str) -> dict:
        return await self._c._req("DELETE", f"/v1/projects/{self._pid}/connections/{provider_id}")

    # ── Routing Config ────────────────────────────────────────────────────────

    async def get_routing_config(self) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/routing/config")

    async def set_routing_config(self, **fields: object) -> dict:
        return await self._c._req("PUT", f"/v1/projects/{self._pid}/routing/config", json=fields)

    async def get_aliases(self) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/routing/aliases")

    async def set_aliases(self, aliases: dict[str, str]) -> dict:
        return await self._c._req("PUT", f"/v1/projects/{self._pid}/routing/aliases", json={"aliases": aliases})

    async def delete_alias(self, alias: str) -> dict:
        return await self._c._req("DELETE", f"/v1/projects/{self._pid}/routing/aliases/{alias}")

    # ── Policy ────────────────────────────────────────────────────────────────

    async def get_policy(self) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/policy")

    async def set_policy(self, **fields: object) -> dict:
        return await self._c._req("PUT", f"/v1/projects/{self._pid}/policy", json=fields)

    # ── Budget ────────────────────────────────────────────────────────────────

    async def get_budget(self) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/budget")

    async def set_budget(
        self,
        *,
        monthly_usd: float | None = None,
        alert_pct:   int | None   = None,
        hard_limit:  bool | None  = None,
    ) -> dict:
        return await self._c._req("PUT", f"/v1/projects/{self._pid}/budget", json={
            k: v for k, v in {
                "monthly_usd": monthly_usd,
                "alert_pct":   alert_pct,
                "hard_limit":  hard_limit,
            }.items() if v is not None
        })

    # ── Environments ──────────────────────────────────────────────────────────

    async def list_environments(self) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/environments")

    async def create_environment(
        self,
        name: str,
        *,
        slug:          str | None  = None,
        description:   str | None  = None,
        is_production: bool        = False,
    ) -> dict:
        return await self._c._req("POST", f"/v1/projects/{self._pid}/environments", json={
            "name":          name,
            "slug":          slug,
            "description":   description,
            "is_production": is_production,
        })

    async def delete_environment(self, env_id: str) -> dict:
        return await self._c._req("DELETE", f"/v1/projects/{self._pid}/environments/{env_id}")

    # ── Usage ─────────────────────────────────────────────────────────────────

    async def usage_overview(self, period_hours: int = 24) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/usage/overview",
                                  params={"period_hours": period_hours})

    async def usage_series(self, period_hours: int = 24, granularity: str = "hour") -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/usage/series",
                                  params={"period_hours": period_hours, "granularity": granularity})

    async def usage_breakdown(self, period_hours: int = 24) -> dict:
        return await self._c._req("GET", f"/v1/projects/{self._pid}/usage/breakdown",
                                  params={"period_hours": period_hours})


# ─── Deprecated alias ──────────────────────────────────────────────────────────

class AsyncAICPClient(AsyncNuRouteClient):
    """
    Deprecated alias for :class:`AsyncNuRouteClient`.

    .. deprecated::
        Use :class:`AsyncNuRouteClient` instead. ``AsyncAICPClient`` will be removed in a
        future major version. Behaves identically — this is a plain subclass with no
        overrides, so all existing code that constructs ``AsyncAICPClient(...)`` keeps
        working unchanged.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "AsyncAICPClient is deprecated and will be removed in a future major version; "
            "use AsyncNuRouteClient instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
