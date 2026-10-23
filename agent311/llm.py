"""Everything that talks to the Claude API lives here, so the rest of the code
doesn't need to know API details.
"""

import json

import anthropic

from . import config

# Opus supports a server-side "refusal fallback": if a safety filter wrongly
# declines a request, the API retries it on another model inside the same call.
FALLBACK_MODELS = {"claude-opus-5-5"}

_client = None


def get_client():
    """Create the API client once. It reads ANTHROPIC_API_KEY from the environment."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def call_claude(model, **request):
    """Send one request to Claude and return the response object."""
    client = get_client()
    if model in FALLBACK_MODELS:
        return client.beta.messages.create(
            model=model,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **request,
        )
    return client.beta.messages.create(model=model, **request)


def response_text(response):
    """Join all the text blocks in a response into one string."""
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()


def cost_usd(response, model):
    """Dollar cost of one response, from token counts and the price table in config."""
    price_in, price_out = config.MODEL_PRICES.get(model, (0.0, 0.0))
    usage = response.usage
    return (usage.input_tokens * price_in + usage.output_tokens * price_out) / 1_000_000


CLASSIFY_SYSTEM = """You sort messages sent to Toronto's 311 service into request types.
Pick exactly one request type from the allowed list. Use OTHER if none fit.
Give a confidence from 0 to 1 for how sure you are."""


def classify_with_claude(message, model):
    """Ask Claude for a request type. Returns a dict like the TF-IDF model's output."""
    allowed = config.REQUEST_TYPES + ["OTHER"]
    schema = {
        "type": "object",
        "properties": {
            "request_type": {"type": "string", "enum": allowed},
            "confidence": {"type": "number"},
        },
        "required": ["request_type", "confidence"],
        "additionalProperties": False,
    }
    response = call_claude(
        model,
        max_tokens=2000,
        system=CLASSIFY_SYSTEM,
        messages=[{"role": "user", "content": message}],
        # "format" forces the answer to be JSON matching the schema above.
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
    )

    if response.stop_reason == "refusal":
        return {"request_type": "OTHER", "confidence": 0.0, "cost_usd": cost_usd(response, model)}

    answer = json.loads(response_text(response))
    return {
        "request_type": answer["request_type"],
        "confidence": float(answer["confidence"]),
        "cost_usd": cost_usd(response, model),
    }
