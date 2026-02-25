#!/usr/bin/env python3
"""
Bitquery GraphQL API Client
Interacts with Bitquery for advanced blockchain analytics
"""

import logging
import os
from typing import Dict, List, Optional
import aiohttp
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class BitqueryAPI:
    """
    Client for Bitquery GraphQL API
    """
    
    def __init__(self):
        self.api_key = os.getenv('BITQUERY_API_KEY')
        self.endpoint = os.getenv('BITQUERY_ENDPOINT', 'https://graphql.bitquery.io')
        self.network = os.getenv('BITQUERY_NETWORK', 'base')
        
        if not self.api_key:
            logger.warning("Bitquery API key not configured")
        
        logger.info("Bitquery API client initialized")
    
    async def _execute_query(self, query: str, variables: Dict = None) -> Dict:
        """Execute GraphQL query"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {'query': query}
            if variables:
                payload['variables'] = variables
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'errors' in data:
                            logger.error(f"Bitquery GraphQL errors: {data['errors']}")
                            return {}
                        return data.get('data', {})
                    else:
                        logger.error(f"Bitquery HTTP error: {response.status}")
                        return {}
        
        except Exception as e:
            logger.error(f"Error executing Bitquery query: {e}")
            return {}
    
    async def get_token_transfers(self, token_address: str, limit: int = 100,
                                 from_address: Optional[str] = None,
                                 to_address: Optional[str] = None) -> List[Dict]:
        """Get token transfers"""
        try:
            # Build filter conditions
            filters = []
            if from_address:
                filters.append(f'sender: {{is: "{from_address}"}}')
            if to_address:
                filters.append(f'receiver: {{is: "{to_address}"}}')
            
            filter_str = ', '.join(filters) if filters else ''
            
            query = f"""
            {{
              ethereum(network: {self.network}) {{
                transfers(
                  currency: {{is: "{token_address}"}}
                  {filter_str}
                  options: {{limit: {limit}, desc: "block.height"}}
                ) {{
                  block {{
                    height
                    timestamp {{
                      unixtime
                    }}
                  }}
                  transaction {{
                    hash
                    gasValue
                    gasPrice
                  }}
                  sender {{
                    address
                  }}
                  receiver {{
                    address
                  }}
                  amount
                  currency {{
                    symbol
                    decimals
                  }}
                }}
              }}
            }}
            """
            
            result = await self._execute_query(query)
            
            if result and 'ethereum' in result:
                return result['ethereum'].get('transfers', [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting token transfers: {e}")
            return []
    
    async def get_address_statistics(self, address: str, token_address: str) -> Dict:
        """Get statistics for an address"""
        try:
            query = f"""
            {{
              ethereum(network: {self.network}) {{
                transfers(
                  currency: {{is: "{token_address}"}}
                  any: [{{
                    sender: {{is: "{address}"}}
                  }}, {{
                    receiver: {{is: "{address}"}}
                  }}]
                ) {{
                  count
                  amount(calculate: sum)
                  sender {{
                    address
                  }}
                  receiver {{
                    address
                  }}
                }}
              }}
            }}
            """
            
            result = await self._execute_query(query)
            
            if result and 'ethereum' in result:
                return result['ethereum'].get('transfers', [{}])[0] if result['ethereum'].get('transfers') else {}
            return {}
            
        except Exception as e:
            logger.error(f"Error getting address statistics: {e}")
            return {}
    
    async def get_token_holders(self, token_address: str, limit: int = 100) -> List[Dict]:
        """Get top token holders"""
        try:
            query = f"""
            {{
              ethereum(network: {self.network}) {{
                address(
                  address: {{is: "{token_address}"}}
                ) {{
                  balances(
                    currency: {{is: "{token_address}"}}
                    options: {{limit: {limit}, desc: "value"}}
                  ) {{
                    address {{
                      address
                    }}
                    value
                  }}
                }}
              }}
            }}
            """
            
            result = await self._execute_query(query)
            
            if result and 'ethereum' in result:
                addresses = result['ethereum'].get('address', [])
                if addresses:
                    return addresses[0].get('balances', [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting token holders: {e}")
            return []
    
    async def get_dex_trades(self, token_address: str, limit: int = 100) -> List[Dict]:
        """Get DEX trades for a token"""
        try:
            query = f"""
            {{
              ethereum(network: {self.network}) {{
                dexTrades(
                  baseCurrency: {{is: "{token_address}"}}
                  options: {{limit: {limit}, desc: "block.height"}}
                ) {{
                  block {{
                    height
                    timestamp {{
                      unixtime
                    }}
                  }}
                  transaction {{
                    hash
                  }}
                  smartContract {{
                    address {{
                      address
                    }}
                  }}
                  baseAmount
                  quoteAmount
                  baseCurrency {{
                    symbol
                  }}
                  quoteCurrency {{
                    symbol
                  }}
                  buyer {{
                    address
                  }}
                  seller {{
                    address
                  }}
                }}
              }}
            }}
            """
            
            result = await self._execute_query(query)
            
            if result and 'ethereum' in result:
                return result['ethereum'].get('dexTrades', [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting DEX trades: {e}")
            return []
    
    async def monitor_real_time_transfers(self, token_address: str, callback) -> None:
        """Monitor real-time transfers (webhook/subscription)"""
        # Note: This requires Bitquery's streaming/webhook feature
        # Implementation depends on Bitquery's specific streaming API
        logger.warning("Real-time monitoring requires Bitquery streaming subscription")
        pass