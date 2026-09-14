"""TypedDicts for all NuRoute API shapes. Import for type annotations."""

from __future__ import annotations

from typing import Any, Literal
from typing_extensions import TypedDict, NotRequired

Period = Literal["24h", "7d", "30d", "90d"]
UserRole = Literal["owner", "project_manager", "developer"]


# ─── Auth ─────────────────────────────────────────────────────────────────────

class Org(TypedDict):
    id: str
    name: str
    plan: str
    email: str
    active: bool
    createdAt: int


class User(TypedDict):
    id: str
    orgId: str
    email: str
    name: str
    role: UserRole
    createdAt: int


class Project(TypedDict):
    id: str
    orgId: str
    name: str
    slug: str
    description: NotRequired[str]
    active: bool
    createdAt: int
    updatedAt: NotRequired[int]


class AuthResponse(TypedDict):
    org: Org
    user: User
    token: str
    project: NotRequired[Project]


# No orgId here: the backend's GET /auth/invite/info response schema (see
# apps/api-gateway/src/routes/members.ts) never includes one.
class InviteInfo(TypedDict):
    orgName: str
    email: str
    role: UserRole
    expiresAt: int


# ─── Members ──────────────────────────────────────────────────────────────────

class Invitation(TypedDict):
    id: str
    email: str
    role: UserRole
    expiresAt: int
    createdAt: int


class InviteResponse(TypedDict):
    invitationId: str
    token: str


# ─── API Keys ─────────────────────────────────────────────────────────────────

class ApiKey(TypedDict):
    id: str
    orgId: str
    projectId: NotRequired[str]
    projectName: NotRequired[str]
    name: str
    keyPrefix: str
    scopes: list[str]
    revoked: bool
    expiresAt: int
    lastUsed: int
    createdAt: int


class CreateKeyResponse(TypedDict):
    keyId: str
    keyValue: str


# ─── Providers ────────────────────────────────────────────────────────────────

class ProviderConfig(TypedDict):
    id: str
    orgId: str
    provider: str
    enabled: bool
    enabledModels: list[str]
    createdAt: int
    updatedAt: int


class ProviderTestResult(TypedDict):
    healthy: bool
    latencyMs: int
    error: str


# ─── Routing ──────────────────────────────────────────────────────────────────

class RoutingWeights(TypedDict):
    cost: int
    latency: int
    quality: int


RoutingStrategy = Literal["balanced", "cheapest", "fastest", "highest_quality", "manual"]


class RoutingPolicy(TypedDict, total=False):
    """Org-level governance policy. Not enforced at the project level — project
    routing config (`ProjectRoutingConfig`, once added) has no `policy` field on
    the backend."""

    preferredProviders: list[str]
    blockedProviders: list[str]
    maxCostPerRequest: float
    maxLatencyMs: int
    allowOpenSource: bool
    allowProprietary: bool
    allowSelfHosted: bool
    allowManaged: bool
    fallbackBehavior: Literal["fail", "allow_commercial", "allow_global", "allow_cheapest"]


class RoutingConfig(TypedDict):
    mode: Literal["auto", "manual"]
    strategy: RoutingStrategy
    manualProvider: NotRequired[str]
    manualModel: NotRequired[str]
    providerOrder: list[str]
    providerAffinity: dict[str, Any]
    modelAliases: dict[str, str]
    allowedRegions: list[str]
    weights: RoutingWeights
    params: dict[str, Any]
    policy: RoutingPolicy


class RoutingAlias(TypedDict):
    alias: str
    model: str


class Candidate(TypedDict):
    provider: str
    model: str
    costUsd: float
    latencyMs: int
    score: int
    winner: bool


class ExcludedProvider(TypedDict):
    provider: str
    reason: str


class RoutingDecisionSummary(TypedDict):
    id: str
    timestamp: str
    project: str
    strategy: str
    selectedProvider: str
    selectedModel: str
    costUsd: float
    latencyMs: int
    status: str
    requestId: str


class RoutingDecision(RoutingDecisionSummary, total=False):
    reasons: list[str]
    candidates: list[Candidate]
    excluded: list[ExcludedProvider]
    constraints: list[str]
    requestMessages: list[dict[str, str]] | None
    responseContent: str | None


# ─── Request Explorer ─────────────────────────────────────────────────────────

class RequestSummary(TypedDict):
    id: str
    requestId: str
    traceId: str
    timestamp: str
    project: str
    strategy: str
    selectedProvider: str
    selectedModel: str
    costUsd: float
    latencyMs: int
    routingDurationMs: int
    promptTokens: int
    completionTokens: int
    totalTokens: int
    status: str


class RequestDetail(RequestSummary, total=False):
    score: int
    confidence: float
    reasons: list[str]
    candidates: list[Candidate]
    excluded: list[ExcludedProvider]
    constraints: list[str]
    requestMessages: list[dict[str, str]] | None
    responseContent: str | None


class TimelineEvent(TypedDict):
    phase: str
    label: str
    startMs: int
    durationMs: int


class ReplayData(TypedDict):
    messages: list[dict[str, str]]
    model: str
    strategy: str
    provider: str


# ─── Usage ────────────────────────────────────────────────────────────────────

class UsageOverview(TypedDict):
    totalRequests: int
    totalSpend: float
    baselineSpend: float
    totalPromptTokens: int
    totalCompletionTokens: int
    avgLatencyMs: int
    p50LatencyMs: int
    p95LatencyMs: int
    successRate: float
    avgRoutingMs: int
    efficiencyScore: int


class UsageSeriesPoint(TypedDict):
    bucket: str
    requests: int
    spend: float
    tokens: int
    avgLatency: int


class ProviderBreakdown(TypedDict):
    provider: str
    requests: int
    spend: float
    avgLatency: int
    successRate: float


class ModelBreakdown(TypedDict):
    model: str
    provider: str
    requests: int
    spend: float
    avgLatency: int
    tokens: int


class StrategyBreakdown(TypedDict):
    strategy: str
    requests: int
    spend: float
    avgLatency: int


class UsageBreakdown(TypedDict):
    providers: list[ProviderBreakdown]
    models: list[ModelBreakdown]
    strategies: list[StrategyBreakdown]


class Recommendation(TypedDict):
    id: str
    title: str
    reason: str
    action: str
    impactType: Literal["cost", "latency", "reliability"]
    estimatedSavings: float


class UsageRecommendations(TypedDict):
    efficiencyScore: int
    recommendations: list[Recommendation]


# ─── Chat ─────────────────────────────────────────────────────────────────────

class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


# snake_case field names below are deliberate: this endpoint is OpenAI-compatible on purpose
# (see apps/api-gateway/src/routes/chat.ts), so the response mirrors OpenAI's own
# chat-completions shape field-for-field rather than this SDK's usual camelCase. Declaring it
# as camelCase previously meant every field on it was silently missing at runtime.
class ChatCompletionChoice(TypedDict):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: ChatCompletionUsage


# owned_by is snake_case for the same OpenAI-compatibility reason as ChatCompletionResponse.
class ModelInfo(TypedDict):
    id: str
    object: str
    created: int
    owned_by: str
