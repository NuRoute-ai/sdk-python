# NuRoute Python SDK

[![PyPI version](https://img.shields.io/pypi/v/nuroute)](https://pypi.org/project/nuroute/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

The official Python SDK for [NuRoute](https://nuroute.ai), a provider-agnostic LLM gateway that lets you route, monitor, and control inference requests across OpenAI, Anthropic, Google, and more.

Point `model="auto"` at any request and NuRoute predicts the cheapest model that can still answer it well, so you stop paying frontier prices for prompts a cheaper model would handle just as well.

## Installation

```bash
pip install nuroute
```

Requires **Python 3.9+**.

## Quick start

```python
from nuroute import NuRouteClient

client = NuRouteClient(
    api_key="aicp-...",
    base_url="https://your-nuroute-gateway",
)

response = client.chat.complete(
    model="auto",  # classifies the request and routes it — see nuroute.ai/docs for strategies
    messages=[{"role": "user", "content": "Hello!"}],
)

print(response["choices"][0]["message"]["content"])
```

> Upgrading from an older version? `AICPClient` is still importable as a deprecated alias of
> `NuRouteClient` — existing code keeps working unchanged (it now raises a `DeprecationWarning`).

## Streaming

```python
for chunk in client.chat.stream(
    model="auto",
    messages=[{"role": "user", "content": "Tell me a story"}],
):
    print(chunk, end="", flush=True)
```

## Async client

```python
from nuroute import AsyncNuRouteClient

async with AsyncNuRouteClient(api_key="aicp-...", base_url="https://your-nuroute-gateway") as client:
    response = await client.chat.complete(
        model="auto",
        messages=[{"role": "user", "content": "Hello!"}],
    )
```

## Authentication

```python
result = client.auth.login(email="you@example.com", password="...")
client.set_api_key(result["token"])
```

## Documentation

Full SDK documentation: [nuroute.ai/docs](https://nuroute.ai/docs)

How routing decisions are made: [nuroute.ai/docs/concepts/routing-performance](https://nuroute.ai/docs/concepts/routing-performance)

## Community

Questions, ideas, or show-and-tell: [github.com/NuRoute-ai/.github/discussions](https://github.com/NuRoute-ai/.github/discussions)

## License

MIT
