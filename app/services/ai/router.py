"""
SIMORGH Platform API - AI Model Router

Deterministic model routing based on policies and availability.
"""
from typing import Optional, Any

from app.providers.base import AIProvider
from app.core.exceptions import ProviderUnavailableError


# Model routing policies
ROUTING_POLICIES = {
    "reasoning": ["claude-3-opus", "claude-3-sonnet", "gpt-4", "qwen-max"],
    "fast": ["claude-3-haiku", "gpt-3.5-turbo", "qwen-turbo"],
    "cheap": ["gpt-3.5-turbo", "qwen-turbo", "claude-3-haiku"],
    "embedding": ["text-embedding-ada-002", "text-embedding-3-small"],
    "vision": ["gpt-4-vision", "claude-3-opus"],
    "coding": ["gpt-4", "claude-3-sonnet", "qwen-plus"],
}

# Policy to provider mapping
POLICY_PROVIDER_ORDER = {
    "reasoning": ["anthropic", "openai", "qwen"],
    "fast": ["anthropic", "openai", "qwen"],
    "cheap": ["openai", "qwen", "anthropic"],
    "embedding": ["openai", "qwen"],
    "vision": ["openai", "anthropic"],
    "coding": ["anthropic", "openai", "qwen"],
}


class ModelRouter:
    """Routes model requests to appropriate providers."""
    
    def __init__(self, providers: dict[str, AIProvider]):
        self.providers = providers
    
    async def resolve_model(
        self,
        requested_model: str,
        policy: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Resolve a model request to (provider_id, model_id).
        
        Args:
            requested_model: Model identifier or routing policy
            policy: Optional routing policy override
        
        Returns:
            Tuple of (provider_id, model_id)
        """
        # Check if it's an explicit model ID
        if requested_model in ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]:
            if await self.providers.get("openai", type("None", (), {"is_available": lambda: False})()).is_available():
                return "openai", requested_model
        
        if requested_model.startswith("claude-"):
            if await self.providers.get("anthropic", type("None", (), {"is_available": lambda: False})()).is_available():
                return "anthropic", requested_model
        
        if requested_model.startswith("qwen-"):
            if await self.providers.get("qwen", type("None", (), {"is_available": lambda: False})()).is_available():
                return "qwen", requested_model
        
        # Check if it's a routing policy
        if requested_model in ROUTING_POLICIES or policy:
            effective_policy = policy or requested_model
            provider_order = POLICY_PROVIDER_ORDER.get(effective_policy, ["openai", "anthropic", "qwen"])
            
            for provider_id in provider_order:
                provider = self.providers.get(provider_id)
                if provider and await provider.is_available():
                    # Get first available model from this provider
                    models = await provider.list_models()
                    if models:
                        return provider_id, models[0]["id"]
            
            raise ProviderUnavailableError(f"No provider available for policy: {effective_policy}")
        
        # Default: try providers in order
        for provider_id in ["openai", "anthropic", "qwen"]:
            provider = self.providers.get(provider_id)
            if provider and await provider.is_available():
                models = await provider.list_models()
                if models:
                    return provider_id, models[0]["id"]
        
        raise ProviderUnavailableError("No AI provider is available")
    
    def get_policy_for_operation(self, operation: str) -> Optional[str]:
        """Get recommended routing policy for an operation type."""
        operation_policies = {
            "decision_analysis": "reasoning",
            "summarization": "fast",
            "classification": "fast",
            "code_generation": "coding",
            "data_extraction": "reasoning",
            "chat": "fast",
        }
        return operation_policies.get(operation)
