"""SIMORGH Platform SDK - Knowledge client."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class KnowledgeSpace:
    """Knowledge space representation."""
    id: str
    name: str
    description: Optional[str]
    tenant_id: str
    workspace_id: str


@dataclass
class KnowledgeDocument:
    """Knowledge document representation."""
    id: str
    title: str
    content_type: str
    status: str
    tenant_id: str
    workspace_id: str
    space_id: str


@dataclass
class SearchResults:
    """Search results from knowledge base."""
    query: str
    results: List[Dict[str, Any]]
    total_count: int


class KnowledgeClient:
    """Knowledge client for document and search operations."""
    
    def __init__(self, http_client):
        self._http = http_client
    
    async def search(
        self,
        query: str,
        space_id: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> SearchResults:
        """Search the knowledge base.
        
        Args:
            query: Search query string
            space_id: Optional knowledge space to search within
            limit: Maximum number of results
            filters: Optional filters (e.g., document types, date ranges)
            
        Returns:
            SearchResults with matching chunks and documents
        """
        payload = {
            "query": query,
            "limit": limit,
        }
        if space_id:
            payload["space_id"] = space_id
        if filters:
            payload["filters"] = filters
        
        response = await self._http.post("/knowledge/search", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return SearchResults(
            query=data.get("query", query),
            results=data.get("results", []),
            total_count=data.get("total_count", 0),
        )
    
    async def list_spaces(self) -> List[KnowledgeSpace]:
        """List all knowledge spaces.
        
        Returns:
            List of KnowledgeSpace objects
        """
        response = await self._http.get("/knowledge/spaces")
        response.raise_for_status()
        data = response.json()
        return [
            KnowledgeSpace(
                id=item["id"],
                name=item["name"],
                description=item.get("description"),
                tenant_id=item["tenant_id"],
                workspace_id=item["workspace_id"],
            )
            for item in data.get("spaces", [])
        ]
    
    async def create_space(
        self,
        name: str,
        description: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> KnowledgeSpace:
        """Create a new knowledge space.
        
        Args:
            name: Space name
            description: Optional description
            workspace_id: Optional workspace ID (uses default if not provided)
            
        Returns:
            Created KnowledgeSpace
        """
        payload = {"name": name}
        if description:
            payload["description"] = description
        if workspace_id:
            payload["workspace_id"] = workspace_id
        
        response = await self._http.post("/knowledge/spaces", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return KnowledgeSpace(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            tenant_id=data["tenant_id"],
            workspace_id=data["workspace_id"],
        )
    
    async def list_documents(
        self,
        space_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[KnowledgeDocument]:
        """List documents in knowledge base.
        
        Args:
            space_id: Filter by knowledge space
            status: Filter by indexing status
            
        Returns:
            List of KnowledgeDocument objects
        """
        params = {}
        if space_id:
            params["space_id"] = space_id
        if status:
            params["status"] = status
        
        response = await self._http.get("/knowledge/documents", params=params)
        response.raise_for_status()
        data = response.json()
        
        return [
            KnowledgeDocument(
                id=item["id"],
                title=item["title"],
                content_type=item["content_type"],
                status=item["status"],
                tenant_id=item["tenant_id"],
                workspace_id=item["workspace_id"],
                space_id=item["space_id"],
            )
            for item in data.get("documents", [])
        ]
    
    async def upload_document(
        self,
        title: str,
        content: str,
        space_id: str,
        content_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeDocument:
        """Upload a document to the knowledge base.
        
        Args:
            title: Document title
            content: Document content
            space_id: Target knowledge space
            content_type: Content type (text, markdown, code, etc.)
            metadata: Optional metadata
            
        Returns:
            Created KnowledgeDocument
        """
        payload = {
            "title": title,
            "content": content,
            "space_id": space_id,
            "content_type": content_type,
        }
        if metadata:
            payload["metadata"] = metadata
        
        response = await self._http.post("/knowledge/documents", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return KnowledgeDocument(
            id=data["id"],
            title=data["title"],
            content_type=data["content_type"],
            status=data["status"],
            tenant_id=data["tenant_id"],
            workspace_id=data["workspace_id"],
            space_id=data["space_id"],
        )
    
    async def get_document(self, document_id: str) -> KnowledgeDocument:
        """Get a specific document.
        
        Args:
            document_id: Document ID
            
        Returns:
            KnowledgeDocument details
        """
        response = await self._http.get(f"/knowledge/documents/{document_id}")
        response.raise_for_status()
        data = response.json()
        
        return KnowledgeDocument(
            id=data["id"],
            title=data["title"],
            content_type=data["content_type"],
            status=data["status"],
            tenant_id=data["tenant_id"],
            workspace_id=data["workspace_id"],
            space_id=data["space_id"],
        )
    
    async def delete_document(self, document_id: str) -> None:
        """Delete a document from the knowledge base.
        
        Args:
            document_id: Document ID to delete
        """
        response = await self._http.delete(f"/knowledge/documents/{document_id}")
        response.raise_for_status()
