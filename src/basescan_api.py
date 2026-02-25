#!/usr/bin/env python3
"""
Basescan API Client
Interacts with Basescan API for blockchain data
"""

import logging
import os
import asyncio
from typing import Dict, List, Optional
import aiohttp
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class BasescanAPI:
    """
    Client for Basescan API
    """
    
    def __init__(self):
        self.api_key = os.getenv('BASESCAN_API_KEY')
        self.base_url = os.getenv('BASESCAN_API_URL', 'https://api.basescan.org/api')
        self.rate_limit = int(os.getenv('BASESCAN_RATE_LIMIT', '5'))  # requests per second
        
        if not self.api_key:
            logger.warning("Basescan API key not configured")
        
        logger.info("Basescan API client initialized")
    
    async def _make_request(self, params: Dict) -> Dict:
        """Make API request with rate limiting"""
        try:
            # Add API key to params
            params['apikey'] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1':
                            return data.get('result', {})
                        else:
                            logger.error(f"Basescan API error: {data.get('message')}")
                            return {}
                    else:
                        logger.error(f"Basescan HTTP error: {response.status}")
                        return {}
            
            # Rate limiting
            await asyncio.sleep(1 / self.rate_limit)
            
        except Exception as e:
            logger.error(f"Error making Basescan request: {e}")
            return {}
    
    async def get_transaction_details(self, tx_hash: str) -> Dict:
        """Get transaction details"""
        try:
            params = {
                'module': 'proxy',
                'action': 'eth_getTransactionByHash',
                'txhash': tx_hash
            }
            return await self._make_request(params)
        except Exception as e:
            logger.error(f"Error getting transaction details: {e}")
            return {}
    
    async def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt"""
        try:
            params = {
                'module': 'proxy',
                'action': 'eth_getTransactionReceipt',
                'txhash': tx_hash
            }
            return await self._make_request(params)
        except Exception as e:
            logger.error(f"Error getting transaction receipt: {e}")
            return {}
    
    async def get_erc20_transfers(self, contract_address: str, address: Optional[str] = None,
                                  start_block: int = 0, end_block: int = 99999999) -> List[Dict]:
        """Get ERC-20 token transfers"""
        try:
            params = {
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': contract_address,
                'startblock': start_block,
                'endblock': end_block,
                'sort': 'desc'
            }
            
            if address:
                params['address'] = address
            
            result = await self._make_request(params)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.error(f"Error getting ERC-20 transfers: {e}")
            return []
    
    async def get_account_balance(self, address: str) -> float:
        """Get ETH balance for address"""
        try:
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest'
            }
            
            result = await self._make_request(params)
            
            if result:
                balance_wei = int(result)
                return balance_wei / 10**18
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return 0.0
    
    async def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """Get ERC-20 token balance"""
        try:
            params = {
                'module': 'account',
                'action': 'tokenbalance',
                'contractaddress': token_address,
                'address': wallet_address,
                'tag': 'latest'
            }
            
            result = await self._make_request(params)
            
            if result:
                # USDC has 6 decimals
                balance_raw = int(result)
                return balance_raw / 10**6
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0.0
    
    async def get_contract_abi(self, contract_address: str) -> List[Dict]:
        """Get contract ABI"""
        try:
            params = {
                'module': 'contract',
                'action': 'getabi',
                'address': contract_address
            }
            
            result = await self._make_request(params)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.error(f"Error getting contract ABI: {e}")
            return []
    
    async def get_block_number_by_timestamp(self, timestamp: int, closest: str = 'before') -> int:
        """Get block number by timestamp"""
        try:
            params = {
                'module': 'block',
                'action': 'getblocknobytime',
                'timestamp': timestamp,
                'closest': closest
            }
            
            result = await self._make_request(params)
            return int(result) if result else 0
            
        except Exception as e:
            logger.error(f"Error getting block by timestamp: {e}")
            return 0