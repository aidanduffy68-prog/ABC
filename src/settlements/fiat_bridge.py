"""
Fiat Bridge / Oracle Service
Enables fiat-compatible settlement for government clients
Government pays in USD, system settles in BTC to vendors

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PaymentMethod(Enum):
    """Payment methods supported"""
    FIAT_USD = "fiat_usd"  # Government pays in USD
    BTC_DIRECT = "btc_direct"  # Direct Bitcoin payment (for non-government clients)
    FIAT_TO_BTC_ORACLE = "fiat_to_btc_oracle"  # Oracle converts fiat to BTC


@dataclass
class FiatPayment:
    """Fiat payment from government client"""
    payment_id: str
    amount_usd: float
    client_id: str  # Government agency ID
    contract_id: Optional[str] = None
    payment_method: str = "wire_transfer"  # wire_transfer, ach, check
    status: str = "pending"  # pending, received, processed, settled
    received_at: Optional[datetime] = None
    settlement_tx_hash: Optional[str] = None


@dataclass
class BTCSettlement:
    """Bitcoin settlement to vendor"""
    settlement_id: str
    amount_btc: float
    vendor_id: str
    fiat_payment_id: Optional[str] = None  # Linked fiat payment
    tx_hash: Optional[str] = None
    status: str = "pending"  # pending, submitted, confirmed
    settled_at: Optional[datetime] = None


class FiatBridge:
    """
    Fiat-to-Bitcoin bridge for government clients
    
    Architecture:
    - Government pays in USD (FAR-compliant)
    - Oracle/custodial service converts to BTC
    - Vendors receive BTC settlements
    - No government hot wallet required
    """
    
    def __init__(self, oracle_service_url: Optional[str] = None):
        """
        Initialize Fiat Bridge
        
        Args:
            oracle_service_url: URL to oracle/custodial service (e.g., Prime, compliant custodian)
        """
        self.oracle_service_url = oracle_service_url
        self.fiat_payments: Dict[str, FiatPayment] = {}
        self.btc_settlements: Dict[str, BTCSettlement] = {}
    
    def receive_fiat_payment(
        self,
        payment_id: str,
        amount_usd: float,
        client_id: str,
        contract_id: Optional[str] = None,
        payment_method: str = "wire_transfer"
    ) -> FiatPayment:
        """
        Receive fiat payment from government client
        
        Args:
            payment_id: Unique payment identifier
            amount_usd: Payment amount in USD
            client_id: Government agency identifier
            contract_id: Related contract ID
            payment_method: Payment method (wire_transfer, ach, check)
        
        Returns:
            FiatPayment object
        """
        payment = FiatPayment(
            payment_id=payment_id,
            amount_usd=amount_usd,
            client_id=client_id,
            contract_id=contract_id,
            payment_method=payment_method,
            status="received",
            received_at=datetime.now()
        )
        
        self.fiat_payments[payment_id] = payment
        return payment
    
    def convert_fiat_to_btc(
        self,
        fiat_payment_id: str,
        btc_price_usd: Optional[float] = None
    ) -> BTCSettlement:
        """
        Convert fiat payment to BTC settlement via oracle
        
        Args:
            fiat_payment_id: Fiat payment ID to convert
            btc_price_usd: BTC price in USD (if None, fetched from oracle)
        
        Returns:
            BTCSettlement object
        """
        if fiat_payment_id not in self.fiat_payments:
            raise ValueError(f"Fiat payment {fiat_payment_id} not found")
        
        fiat_payment = self.fiat_payments[fiat_payment_id]
        
        # Get BTC price from oracle if not provided
        if btc_price_usd is None:
            btc_price_usd = self._fetch_btc_price()
        
        # Calculate BTC amount
        amount_btc = fiat_payment.amount_usd / btc_price_usd
        
        # Create BTC settlement
        settlement = BTCSettlement(
            settlement_id=f"settlement_{fiat_payment_id}",
            amount_btc=amount_btc,
            vendor_id=fiat_payment.client_id,  # In practice, would map to vendor
            fiat_payment_id=fiat_payment_id,
            status="pending"
        )
        
        self.btc_settlements[settlement.settlement_id] = settlement
        fiat_payment.status = "processed"
        
        return settlement
    
    def execute_btc_settlement(
        self,
        settlement_id: str,
        vendor_btc_address: str
    ) -> Dict[str, Any]:
        """
        Execute BTC settlement to vendor
        
        Args:
            settlement_id: Settlement ID
            vendor_btc_address: Vendor's Bitcoin address
        
        Returns:
            Settlement result with tx_hash
        """
        if settlement_id not in self.btc_settlements:
            raise ValueError(f"Settlement {settlement_id} not found")
        
        settlement = self.btc_settlements[settlement_id]
        
        # In production, this would call oracle/custodial service
        # to execute the BTC transfer
        # For now, return mock result
        
        tx_hash = self._execute_btc_transfer(
            settlement.amount_btc,
            vendor_btc_address
        )
        
        settlement.tx_hash = tx_hash
        settlement.status = "submitted"
        settlement.settled_at = datetime.now()
        
        return {
            "settlement_id": settlement_id,
            "tx_hash": tx_hash,
            "amount_btc": settlement.amount_btc,
            "status": "submitted",
            "vendor_address": vendor_btc_address
        }
    
    def _fetch_btc_price(self) -> float:
        """Fetch BTC price from oracle/exchange"""
        # In production, would call oracle service or exchange API
        # For now, return mock price
        return 45000.0  # Mock BTC price
    
    def _execute_btc_transfer(self, amount_btc: float, address: str) -> str:
        """Execute BTC transfer via oracle/custodial service"""
        # In production, would call oracle service to execute transfer
        # Returns transaction hash
        import hashlib
        tx_data = f"{amount_btc}_{address}_{datetime.now().isoformat()}"
        return hashlib.sha256(tx_data.encode()).hexdigest()
    
    def get_settlement_status(self, settlement_id: str) -> Dict[str, Any]:
        """Get settlement status"""
        if settlement_id not in self.btc_settlements:
            return {"error": "Settlement not found"}
        
        settlement = self.btc_settlements[settlement_id]
        
        return {
            "settlement_id": settlement_id,
            "amount_btc": settlement.amount_btc,
            "status": settlement.status,
            "tx_hash": settlement.tx_hash,
            "settled_at": settlement.settled_at.isoformat() if settlement.settled_at else None
        }


class OracleService:
    """
    Oracle service for fiat-to-BTC conversion
    Acts as compliant intermediary between government and vendors
    """
    
    def __init__(self, custodian_name: str = "Prime"):
        """
        Initialize Oracle Service
        
        Args:
            custodian_name: Name of custodial service (Prime, Coinbase Prime, etc.)
        """
        self.custodian_name = custodian_name
        self.fiat_bridge = FiatBridge()
    
    def process_government_payment(
        self,
        payment_id: str,
        amount_usd: float,
        agency_id: str,
        vendor_btc_address: str
    ) -> Dict[str, Any]:
        """
        Process government payment: Receive USD, convert to BTC, settle to vendor
        
        Args:
            payment_id: Payment identifier
            amount_usd: Payment amount in USD
            agency_id: Government agency ID
            vendor_btc_address: Vendor's Bitcoin address
        
        Returns:
            Settlement result
        """
        # Step 1: Receive fiat payment
        fiat_payment = self.fiat_bridge.receive_fiat_payment(
            payment_id=payment_id,
            amount_usd=amount_usd,
            client_id=agency_id
        )
        
        # Step 2: Convert to BTC
        settlement = self.fiat_bridge.convert_fiat_to_btc(fiat_payment.payment_id)
        
        # Step 3: Execute BTC settlement
        result = self.fiat_bridge.execute_btc_settlement(
            settlement.settlement_id,
            vendor_btc_address
        )
        
        return result

