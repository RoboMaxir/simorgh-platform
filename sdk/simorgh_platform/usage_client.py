"""SIMORGH Platform SDK - Usage client."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class UsageEntry:
    """Single usage entry."""
    request_id: str
    provider: str
    model: str
    operation: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    status: str
    timestamp: str


@dataclass
class UsageSummary:
    """Usage summary."""
    total_requests: int
    total_tokens: int
    total_cost: int
    date_range: Dict[str, str]


class UsageClient:
    """Usage tracking client."""
    
    def __init__(self, http_client):
        self._http = http_client
    
    async def get(
        self,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        application_id: Optional[str] = None,
    ) -> List[UsageEntry]:
        """Get AI usage history.
        
        Args:
            limit: Maximum number of entries to return
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            application_id: Filter by application ID
            
        Returns:
            List of UsageEntry objects
        """
        params = {"limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if application_id:
            params["application_id"] = application_id
        
        response = await self._http.get("/ai/usage", params=params)
        response.raise_for_status()
        data = response.json()
        
        return [
            UsageEntry(
                request_id=item["request_id"],
                provider=item["provider"],
                model=item["model"],
                operation=item["operation"],
                input_tokens=item["input_tokens"],
                output_tokens=item["output_tokens"],
                total_tokens=item["total_tokens"],
                status=item["status"],
                timestamp=item["timestamp"],
            )
            for item in data.get("entries", [])
        ]
    
    async def get_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> UsageSummary:
        """Get usage summary.
        
        Args:
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            
        Returns:
            UsageSummary with aggregated statistics
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await self._http.get("/ai/usage/summary", params=params)
        response.raise_for_status()
        data = response.json()
        
        return UsageSummary(
            total_requests=data.get("total_requests", 0),
            total_tokens=data.get("total_tokens", 0),
            total_cost=data.get("total_cost", 0),
            date_range=data.get("date_range", {}),
        )
