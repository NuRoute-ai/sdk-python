# NuRoute Python SDK

The official Python SDK for [NuRoute](https://github.com/NuRoute-ai/sdk-python) — a provider-agnostic LLM gateway that lets you route, monitor, and control inference requests across OpenAI, Anthropic, Google, and more.

## Installation

```bash
pip install aicp
```

Requires **Python 3.9+**.

## Quick start

```python
from aicp import NuRouteClient

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
from aicp import AsyncNuRouteClient

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

## License

MIT
