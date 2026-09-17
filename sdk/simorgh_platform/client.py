"""SIMORGH Platform SDK Client."""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from simorgh_platform.ai import AIClient
from simorgh_platform.knowledge import KnowledgeClient
from simorgh_platform.usage import UsageClient
from simorgh_platform.billing import BillingClient


class SimorghClient:
    """Main client for SIMORGH Platform API.
    
    Usage:
        client = SimorghClient(api_key="your-api-key")
        
        # AI operations
        response = await client.ai.chat(messages=[...], model="reasoning")
        embeddings = await client.ai.embedding(text="hello")
        
        # Knowledge operations
        results = await client.knowledge.search(query="topic")
        
        # Usage tracking
        usage = await client.usage.get()
        
        # Billing
        balance = await client.billing.get_balance()
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ):
        """Initialize SIMORGH Platform client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of the Platform API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # Initialize HTTP client
        self._http_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(timeout),
        )
        
        # Initialize sub-clients
        self.ai = AIClient(self._http_client)
        self.knowledge = KnowledgeClient(self._http_client)
        self.usage = UsageClient(self._http_client)
        self.billing = BillingClient(self._http_client)
    
    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = await self._http_client.get("/health")
        response.raise_for_status()
        return response.json()
