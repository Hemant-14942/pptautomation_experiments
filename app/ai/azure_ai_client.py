from app.config.ai_config import (
    AZURE_ENDPOINT,
    AZURE_API_KEY,
    DEFAULT_DEPLOYMENT,
    AVAILABLE_DEPLOYMENTS,
)

from anthropic import AnthropicFoundry
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def _build_client(endpoint: str = None, api_key: str = None) -> AnthropicFoundry:
    endpoint = endpoint or AZURE_ENDPOINT
    api_key = api_key or AZURE_API_KEY

    if api_key:
        return AnthropicFoundry(api_key=api_key, base_url=endpoint)

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default",
    )
    return AnthropicFoundry(
        azure_ad_token_provider=token_provider,
        base_url=endpoint,
    )


_client_cache: dict[str, AnthropicFoundry] = {}


def get_client(deployment: str = None) -> AnthropicFoundry:
    deployment = deployment or DEFAULT_DEPLOYMENT
    if deployment not in _client_cache:
        _client_cache[deployment] = _build_client()
    return _client_cache[deployment]


def chat(
    prompt: str,
    deployment: str = None,
    max_tokens: int = 1024,
    system: str = None,
    **kwargs,
):
    deployment = deployment or DEFAULT_DEPLOYMENT
    client = get_client(deployment)

    messages = [{"role": "user", "content": prompt}]
    params = {
        "model": deployment,
        "messages": messages,
        "max_tokens": max_tokens,
        **kwargs,
    }
    if system:
        params["system"] = system

    return client.messages.create(**params)


if __name__ == "__main__":
    import sys

    prompt = sys.argv[1] if len(sys.argv) > 1 else "What is the capital of France?"
    deployment = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEPLOYMENT

    if deployment not in AVAILABLE_DEPLOYMENTS:
        print(f"Unknown deployment '{deployment}'. Available: {list(AVAILABLE_DEPLOYMENTS)}")
        sys.exit(1)

    print(f"Deployment: {deployment}")
    print(f"Endpoint:   {AZURE_ENDPOINT}")
    print(f"Prompt:     {prompt}\n")

    response = chat(prompt=prompt, deployment=deployment)
    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)