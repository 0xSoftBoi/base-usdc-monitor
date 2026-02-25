#!/usr/bin/env python3
"""
Base Network RPC Connector
Handles all Web3 RPC interactions with Base network
"""

import asyncio
import logging
from typing import Dict, List, Optional
from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class BaseRPCConnector:
    """
    Manages connection to Base network RPC endpoints
    """
    
    def __init__(self):
        self.rpc_url = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
        self.rpc_url_backup = os.getenv('BASE_RPC_URL_BACKUP', 'https://base.llamarpc.com')
        self.chain_id = int(os.getenv('BASE_CHAIN_ID', '8453'))
        
        logger.info(f"Initializing Base RPC connection to {self.rpc_url}")
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Test connection
        if not self.w3.is_connected():
            logger.warning(f"Primary RPC {self.rpc_url} not connected, trying backup")
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url_backup))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if self.w3.is_connected():
            logger.info(f"✓ Connected to Base network (Chain ID: {self.chain_id})")
            logger.info(f"Latest block: {self.w3.eth.block_number}")
        else:
            logger.error("Failed to connect to Base network")
            raise ConnectionError("Cannot connect to Base RPC")
    
    async def get_latest_block_number(self) -> int:
        """Get the latest block number"""
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            raise
    
    async def get_block(self, block_number: int, full_transactions: bool = False) -> Dict:
        """Get block data"""
        try:
            return dict(self.w3.eth.get_block(block_number, full_transactions=full_transactions))
        except Exception as e:
            logger.error(f"Error getting block {block_number}: {e}")
            raise
    
    async def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction details"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            return dict(tx)
        except Exception as e:
            logger.error(f"Error getting transaction {tx_hash}: {e}")
            return {}
    
    async def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error getting receipt for {tx_hash}: {e}")
            return {}
    
    async def get_logs(self, filter_params: Dict) -> List[Dict]:
        """Get event logs based on filter parameters"""
        try:
            logs = self.w3.eth.get_logs(filter_params)
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    def create_filter(self, contract_address: str, event_signature: str, 
                     from_block: int, to_block: int = 'latest') -> Dict:
        """Create a log filter for events"""
        return {
            'address': Web3.to_checksum_address(contract_address),
            'fromBlock': from_block,
            'toBlock': to_block,
            'topics': [event_signature]
        }
    
    def decode_log(self, log: Dict, abi: List[Dict]) -> Dict:
        """Decode an event log"""
        try:
            # Find event in ABI
            event_abi = None
            for item in abi:
                if item['type'] == 'event' and log['topics'][0].hex() == self.w3.keccak(text=f"{item['name']}({','.join([inp['type'] for inp in item['inputs']])})").hex():
                    event_abi = item
                    break
            
            if not event_abi:
                return {}
            
            # Decode log
            decoded = self.w3.eth.contract(abi=[event_abi]).events[event_abi['name']]().process_log(log)
            return dict(decoded['args'])
        except Exception as e:
            logger.error(f"Error decoding log: {e}")
            return {}
    
    def get_balance(self, address: str) -> float:
        """Get ETH balance of address"""
        try:
            balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
            return self.w3.from_wei(balance_wei, 'ether')
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            return 0.0
    
    def get_token_balance(self, token_address: str, wallet_address: str, decimals: int = 18) -> float:
        """Get ERC-20 token balance"""
        try:
            # ERC-20 balanceOf function signature
            balance_of_abi = [
                {
                    'constant': True,
                    'inputs': [{'name': '_owner', 'type': 'address'}],
                    'name': 'balanceOf',
                    'outputs': [{'name': 'balance', 'type': 'uint256'}],
                    'type': 'function'
                }
            ]
            
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=balance_of_abi
            )
            
            balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
            return balance / (10 ** decimals)
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0.0
    
    async def close(self):
        """Close connection"""
        logger.info("Closing RPC connection")
        # Web3.py doesn't require explicit closing for HTTP provider