#!/usr/bin/env python3
"""
USDC Transfer Tracker
Monitors USDC (ERC-20) transfers on Base network
"""

import logging
from typing import Dict, List, Optional
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class USDCTracker:
    """
    Tracks USDC transfers on Base network
    """
    
    # ERC-20 Transfer event signature
    TRANSFER_EVENT_SIGNATURE = Web3.keccak(text="Transfer(address,address,uint256)").hex()
    
    def __init__(self, rpc_connector):
        self.rpc = rpc_connector
        self.usdc_address = os.getenv('USDC_CONTRACT_ADDRESS', '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
        self.usdc_decimals = int(os.getenv('USDC_DECIMALS', '6'))
        
        logger.info(f"Initialized USDC Tracker for contract: {self.usdc_address}")
    
    async def get_transfers(self, from_block: int, to_block: int, 
                           addresses: Optional[List[str]] = None) -> List[Dict]:
        """
        Get USDC transfers in a block range
        
        Args:
            from_block: Starting block number
            to_block: Ending block number
            addresses: Optional list of addresses to filter (monitors both from and to)
        
        Returns:
            List of transfer events
        """
        try:
            # Create filter for Transfer events
            filter_params = {
                'address': Web3.to_checksum_address(self.usdc_address),
                'fromBlock': from_block,
                'toBlock': to_block,
                'topics': [self.TRANSFER_EVENT_SIGNATURE]
            }
            
            # Get logs
            logs = await self.rpc.get_logs(filter_params)
            
            # Parse transfers
            transfers = []
            for log in logs:
                transfer = self._parse_transfer_log(log)
                
                # Filter by addresses if specified
                if addresses:
                    if transfer['from'] in addresses or transfer['to'] in addresses:
                        transfers.append(transfer)
                else:
                    transfers.append(transfer)
            
            return transfers
            
        except Exception as e:
            logger.error(f"Error getting transfers: {e}", exc_info=True)
            return []
    
    def _parse_transfer_log(self, log: Dict) -> Dict:
        """
        Parse a Transfer event log
        
        Log structure:
        - topics[0]: Event signature
        - topics[1]: From address (padded)
        - topics[2]: To address (padded)
        - data: Amount (uint256)
        """
        try:
            # Extract addresses from topics (remove padding)
            from_address = '0x' + log['topics'][1].hex()[-40:]
            to_address = '0x' + log['topics'][2].hex()[-40:]
            
            # Decode amount from data
            amount_raw = int(log['data'].hex(), 16)
            amount = amount_raw / (10 ** self.usdc_decimals)
            
            return {
                'transactionHash': log['transactionHash'].hex(),
                'blockNumber': log['blockNumber'],
                'logIndex': log['logIndex'],
                'from': Web3.to_checksum_address(from_address),
                'to': Web3.to_checksum_address(to_address),
                'amount': amount,
                'amountRaw': amount_raw
            }
        except Exception as e:
            logger.error(f"Error parsing transfer log: {e}")
            return {}
    
    async def get_balance(self, address: str) -> float:
        """
        Get USDC balance for an address
        """
        try:
            balance = self.rpc.get_token_balance(
                token_address=self.usdc_address,
                wallet_address=address,
                decimals=self.usdc_decimals
            )
            return balance
        except Exception as e:
            logger.error(f"Error getting USDC balance for {address}: {e}")
            return 0.0
    
    async def track_address(self, address: str, from_block: int = 0) -> List[Dict]:
        """
        Get all USDC transfers for a specific address
        """
        try:
            current_block = await self.rpc.get_latest_block_number()
            
            logger.info(f"Tracking USDC transfers for {address} from block {from_block} to {current_block}")
            
            transfers = await self.get_transfers(
                from_block=from_block,
                to_block=current_block,
                addresses=[address]
            )
            
            return transfers
        except Exception as e:
            logger.error(f"Error tracking address: {e}")
            return []
    
    async def get_recent_transfers(self, num_blocks: int = 100) -> List[Dict]:
        """
        Get recent USDC transfers from the last N blocks
        """
        try:
            current_block = await self.rpc.get_latest_block_number()
            from_block = max(0, current_block - num_blocks)
            
            transfers = await self.get_transfers(
                from_block=from_block,
                to_block=current_block
            )
            
            return transfers
        except Exception as e:
            logger.error(f"Error getting recent transfers: {e}")
            return []
    
    def filter_by_amount(self, transfers: List[Dict], min_amount: float = None, 
                        max_amount: float = None, exact_amount: float = None) -> List[Dict]:
        """
        Filter transfers by amount
        """
        filtered = []
        
        for transfer in transfers:
            amount = transfer.get('amount', 0)
            
            if exact_amount is not None:
                if abs(amount - exact_amount) < 0.01:  # Allow small floating point difference
                    filtered.append(transfer)
            else:
                if min_amount is not None and amount < min_amount:
                    continue
                if max_amount is not None and amount > max_amount:
                    continue
                filtered.append(transfer)
        
        return filtered
    
    async def get_100_usdc_transfers(self, from_block: int, to_block: int) -> List[Dict]:
        """
        Specifically get transfers of exactly 100 USDC
        """
        transfers = await self.get_transfers(from_block, to_block)
        return self.filter_by_amount(transfers, exact_amount=100.0)