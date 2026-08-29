import os
from dotenv import load_dotenv
load_dotenv()

AZURE_ENDPOINT = os.getenv(
    "AZURE_ANTHROPIC_ENDPOINT",
    "https://claude-pandora-resource.services.ai.azure.com/anthropic",
)
AZURE_API_KEY        = os.getenv("AZURE_ANTHROPIC_API_KEY", "")
DEFAULT_DEPLOYMENT   = os.getenv("AZURE_ANTHROPIC_DEPLOYMENT", "claude-sonnet-4-6")
AVAILABLE_DEPLOYMENTS = {
    "claude-sonnet-4-6": "claude-sonnet-4-6",
    "claude-opus-4-8":   "claude-opus-4-8",
}