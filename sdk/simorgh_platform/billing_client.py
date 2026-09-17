"""SIMORGH Platform SDK - Billing client."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CreditAccount:
    """Credit account representation."""
    id: str
    workspace_id: str
    balance: int
    currency: str
    is_active: bool


@dataclass
class CreditTransaction:
    """Credit transaction record."""
    id: str
    account_id: str
    transaction_type: str  # credit, debit, adjustment, refund
    amount: int
    balance_after: int
    description: Optional[str]
    reference_type: Optional[str]
    reference_id: Optional[str]
    timestamp: str


class BillingClient:
    """Billing and credits client."""
    
    def __init__(self, http_client):
        self._http = http_client
    
    async def get_balance(self) -> CreditAccount:
        """Get current credit balance.
        
        Returns:
            CreditAccount with current balance
        """
        response = await self._http.get("/billing/account")
        response.raise_for_status()
        data = response.json()
        
        return CreditAccount(
            id=data["id"],
            workspace_id=data["workspace_id"],
            balance=data["balance"],
            currency=data["currency"],
            is_active=data["is_active"],
        )
    
    async def add_credits(
        self,
        amount: int,
        description: Optional[str] = None,
    ) -> CreditTransaction:
        """Add credits to the account.
        
        Args:
            amount: Amount of credits to add (in smallest currency unit)
            description: Optional description for the transaction
            
        Returns:
            CreditTransaction record
        """
        payload = {
            "amount": amount,
            "transaction_type": "credit",
        }
        if description:
            payload["description"] = description
        
        response = await self._http.post("/billing/transactions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return CreditTransaction(
            id=data["id"],
            account_id=data["account_id"],
            transaction_type=data["transaction_type"],
            amount=data["amount"],
            balance_after=data["balance_after"],
            description=data.get("description"),
            reference_type=data.get("reference_type"),
            reference_id=data.get("reference_id"),
            timestamp=data["created_at"],
        )
    
    async def get_transactions(
        self,
        limit: int = 50,
        transaction_type: Optional[str] = None,
    ) -> List[CreditTransaction]:
        """Get credit transaction history.
        
        Args:
            limit: Maximum number of transactions to return
            transaction_type: Filter by transaction type
            
        Returns:
            List of CreditTransaction records
        """
        params = {"limit": limit}
        if transaction_type:
            params["type"] = transaction_type
        
        response = await self._http.get("/billing/transactions", params=params)
        response.raise_for_status()
        data = response.json()
        
        return [
            CreditTransaction(
                id=item["id"],
                account_id=item["account_id"],
                transaction_type=item["transaction_type"],
                amount=item["amount"],
                balance_after=item["balance_after"],
                description=item.get("description"),
                reference_type=item.get("reference_type"),
                reference_id=item.get("reference_id"),
                timestamp=item["created_at"],
            )
            for item in data.get("transactions", [])
        ]
    
    async def get_subscription(self) -> Optional[Dict[str, Any]]:
        """Get current subscription details.
        
        Returns:
            Subscription details or None if no active subscription
        """
        response = await self._http.get("/billing/subscription")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
