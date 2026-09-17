"""
SIMORGH Platform API - Event System

Simple, extensible internal event system for platform events.
Events are published and consumed within the platform for:
- AIRequestCompleted
- CreditConsumed
- DocumentIndexed
- UserCreated
- And other platform events

Kept simple and extensible - no external message broker required for MVP.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional
import uuid
import asyncio


@dataclass
class PlatformEvent:
    """Base class for all platform events."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: Optional[str] = None
    workspace_id: Optional[str] = None
    application_id: Optional[str] = None
    actor_id: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "application_id": self.application_id,
            "actor_id": self.actor_id,
            "data": self.data,
        }


@dataclass
class AIRequestCompleted(PlatformEvent):
    """Event fired when an AI request completes."""
    
    event_type: str = "ai.request.completed"
    request_id: str = ""
    provider: str = ""
    model: str = ""
    operation: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: int = 0
    status: str = "success"
    

@dataclass
class CreditConsumed(PlatformEvent):
    """Event fired when credits are consumed."""
    
    event_type: str = "billing.credit_consumed"
    account_id: str = ""
    transaction_id: str = ""
    amount: int = 0
    balance_after: int = 0
    reference_type: str = ""
    reference_id: str = ""
    

@dataclass
class CreditAdded(PlatformEvent):
    """Event fired when credits are added."""
    
    event_type: str = "billing.credit_added"
    account_id: str = ""
    transaction_id: str = ""
    amount: int = 0
    balance_after: int = 0
    transaction_type: str = ""
    description: str = ""
    

@dataclass
class DocumentIndexed(PlatformEvent):
    """Event fired when a document is indexed."""
    
    event_type: str = "knowledge.document_indexed"
    document_id: str = ""
    space_id: str = ""
    title: str = ""
    chunk_count: int = 0
    

@dataclass
class UserCreated(PlatformEvent):
    """Event fired when a user is created."""
    
    event_type: str = "identity.user_created"
    user_id: str = ""
    email: str = ""
    name: str = ""
    

@dataclass
class APIKeyCreated(PlatformEvent):
    """Event fired when an API key is created."""
    
    event_type: str = "identity.api_key_created"
    credential_id: str = ""
    key_prefix: str = ""
    application_id: str = ""
    

@dataclass
class SubscriptionChanged(PlatformEvent):
    """Event fired when a subscription changes."""
    
    event_type: str = "billing.subscription_changed"
    subscription_id: str = ""
    workspace_id: str = ""
    plan_id: str = ""
    status: str = ""
    

class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    async def handle(self, event: PlatformEvent) -> None:
        """Handle an event."""
        pass


class EventBus:
    """Simple in-memory event bus for platform events."""
    
    def __init__(self):
        self._handlers: dict[str, list[Callable[[PlatformEvent], Any]]] = {}
        self._async_handlers: dict[str, list[Callable[[PlatformEvent], Any]]] = {}
    
    def subscribe(self, event_type: str, handler: Callable[[PlatformEvent], None]) -> None:
        """Subscribe a synchronous handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def subscribe_async(self, event_type: str, handler: Callable[[PlatformEvent], Any]) -> None:
        """Subscribe an asynchronous handler to an event type."""
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        self._async_handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable[[PlatformEvent], Any]) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
        if event_type in self._async_handlers:
            self._async_handlers[event_type].remove(handler)
    
    def publish(self, event: PlatformEvent) -> None:
        """Publish an event to all subscribers (synchronous)."""
        event_type = event.event_type
        
        # Call sync handlers
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                # Log error but don't fail other handlers
                print(f"Event handler error for {event_type}: {e}")
        
        # Schedule async handlers
        for handler in self._async_handlers.get(event_type, []):
            try:
                asyncio.create_task(self._call_async_handler(handler, event))
            except Exception as e:
                print(f"Failed to schedule async handler for {event_type}: {e}")
    
    async def publish_async(self, event: PlatformEvent) -> None:
        """Publish an event to all subscribers (asynchronous)."""
        event_type = event.event_type
        
        # Call sync handlers
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                print(f"Event handler error for {event_type}: {e}")
        
        # Call async handlers
        tasks = []
        for handler in self._async_handlers.get(event_type, []):
            try:
                tasks.append(self._call_async_handler(handler, event))
            except Exception as e:
                print(f"Failed to schedule async handler for {event_type}: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _call_async_handler(
        self,
        handler: Callable[[PlatformEvent], Any],
        event: PlatformEvent,
    ) -> None:
        """Call an async handler."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            print(f"Async event handler error for {event.event_type}: {e}")


# Global event bus instance
event_bus = EventBus()


def publish_event(event: PlatformEvent) -> None:
    """Convenience function to publish an event."""
    event_bus.publish(event)


async def publish_event_async(event: PlatformEvent) -> None:
    """Convenience function to publish an event asynchronously."""
    await event_bus.publish_async(event)