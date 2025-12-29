"""
Bitcoin transaction parser
"""
from typing import Dict, Any, List, Optional


class BitcoinTransactionParser:
    """Parse Bitcoin transactions from RPC data"""
    
    def parse_transactions(self, block: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse transactions from Bitcoin block.
        
        Args:
            block: Raw block data from Bitcoin RPC
            
        Returns:
            List of parsed transactions
        """
        transactions = []
        
        for tx in block.get('tx', []):
            parsed_tx = self.parse_transaction(tx, block.get('height', 0), block.get('time', 0))
            transactions.append(parsed_tx)
        
        return transactions
    
    def parse_transaction(
        self,
        tx: Dict[str, Any],
        block_height: int,
        block_time: int
    ) -> Dict[str, Any]:
        """
        Parse individual Bitcoin transaction.
        
        Args:
            tx: Raw transaction data
            block_height: Block height
            block_time: Block timestamp
            
        Returns:
            Parsed transaction
        """
        # Parse inputs
        inputs = []
        for vin in tx.get('vin', []):
            if 'coinbase' in vin:
                # Coinbase transaction (mining reward)
                inputs.append({
                    "type": "coinbase",
                    "coinbase": vin['coinbase']
                })
            else:
                inputs.append({
                    "type": "standard",
                    "txid": vin.get('txid'),
                    "vout": vin.get('vout'),
                    "script_sig": vin.get('scriptSig', {})
                })
        
        # Parse outputs
        outputs = []
        for vout in tx.get('vout', []):
            script_pub_key = vout.get('scriptPubKey', {})
            outputs.append({
                "value": vout.get('value', 0),
                "n": vout.get('n'),
                "script_pub_key": {
                    "asm": script_pub_key.get('asm'),
                    "hex": script_pub_key.get('hex'),
                    "type": script_pub_key.get('type'),
                    "address": script_pub_key.get('address')
                }
            })
        
        return {
            "txid": tx.get('txid', ''),
            "version": tx.get('version'),
            "size": tx.get('size'),
            "vsize": tx.get('vsize'),
            "weight": tx.get('weight'),
            "locktime": tx.get('locktime'),
            "inputs": inputs,
            "outputs": outputs,
            "block_height": block_height,
            "block_time": block_time,
            "fee": None  # Fee calculation requires fetching input values
        }
    
    def calculate_fee(
        self,
        inputs: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate transaction fee.
        
        Args:
            inputs: Transaction inputs
            outputs: Transaction outputs
            
        Returns:
            Fee in BTC (0.0 if cannot calculate)
        """
        # Fee calculation requires fetching input values from previous transactions
        # This is a placeholder - actual implementation would need to fetch UTXO data
        return 0.0
    
    def extract_addresses(self, tx: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract addresses from transaction.
        
        Args:
            tx: Parsed transaction
            
        Returns:
            Dict with input and output addresses
        """
        input_addresses = []
        output_addresses = []
        
        # Extract output addresses
        for out in tx.get('outputs', []):
            addr = out.get('script_pub_key', {}).get('address')
            if addr:
                output_addresses.append(addr)
        
        # Input addresses require scriptSig parsing (more complex)
        # Placeholder for now
        
        return {
            "input_addresses": input_addresses,
            "output_addresses": output_addresses
        }

