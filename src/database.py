#!/usr/bin/env python3
"""
Supabase Database Manager
Handles all database operations for storing transactions and alerts
"""

import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SupabaseManager:
    """
    Manages Supabase database operations
    """
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.table_transactions = os.getenv('SUPABASE_TABLE_TRANSACTIONS', 'transactions')
        self.table_alerts = os.getenv('SUPABASE_TABLE_ALERTS', 'alerts')
        
        if not self.url or not self.key:
            logger.error("Supabase credentials not configured")
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("✓ Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    async def insert_transaction(self, transaction: Dict) -> Dict:
        """
        Insert a new transaction record
        
        Args:
            transaction: Transaction data dictionary
        
        Returns:
            Inserted record
        """
        try:
            # Prepare data
            data = {
                'tx_hash': transaction.get('tx_hash'),
                'block_number': transaction.get('block_number'),
                'timestamp': transaction.get('timestamp', datetime.now().isoformat()),
                'from_address': transaction.get('from_address'),
                'to_address': transaction.get('to_address'),
                'amount': float(transaction.get('amount', 0)),
                'gas_used': transaction.get('gas_used'),
                'gas_price': str(transaction.get('gas_price', 0)),
                'status': transaction.get('status', 'confirmed'),
                'is_flagged': transaction.get('is_flagged', False),
                'pattern_score': float(transaction.get('pattern_score', 0))
            }
            
            # Insert into database
            result = self.client.table(self.table_transactions).insert(data).execute()
            
            logger.info(f"✓ Transaction saved to database: {transaction.get('tx_hash')}")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error inserting transaction: {e}", exc_info=True)
            return {}
    
    async def insert_alert(self, alert: Dict) -> Dict:
        """
        Insert a new alert record
        
        Args:
            alert: Alert data dictionary
        
        Returns:
            Inserted record
        """
        try:
            data = {
                'transaction_id': alert.get('transaction_id'),
                'alert_type': alert.get('alert_type'),
                'severity': alert.get('severity'),
                'message': alert.get('message'),
                'sent_at': datetime.now().isoformat(),
                'channels': alert.get('channels', [])
            }
            
            result = self.client.table(self.table_alerts).insert(data).execute()
            
            logger.debug(f"✓ Alert saved to database")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error inserting alert: {e}")
            return {}
    
    async def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction by hash"""
        try:
            result = self.client.table(self.table_transactions).select("*").eq('tx_hash', tx_hash).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            return None
    
    async def get_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """Get recent transactions"""
        try:
            result = self.client.table(self.table_transactions).select("*").order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []
    
    async def get_flagged_transactions(self, limit: int = 50) -> List[Dict]:
        """Get flagged transactions"""
        try:
            result = self.client.table(self.table_transactions).select("*").eq('is_flagged', True).order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting flagged transactions: {e}")
            return []
    
    async def get_transactions_by_address(self, address: str, limit: int = 100) -> List[Dict]:
        """Get transactions for a specific address"""
        try:
            # Query for both from and to addresses
            result = self.client.table(self.table_transactions).select("*").or_(f"from_address.eq.{address},to_address.eq.{address}").order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting transactions for address: {e}")
            return []
    
    async def get_transactions_by_amount(self, amount: float, tolerance: float = 0.01, limit: int = 100) -> List[Dict]:
        """Get transactions with specific amount"""
        try:
            min_amount = amount - tolerance
            max_amount = amount + tolerance
            
            result = self.client.table(self.table_transactions).select("*").gte('amount', min_amount).lte('amount', max_amount).order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting transactions by amount: {e}")
            return []
    
    async def get_alerts(self, limit: int = 100) -> List[Dict]:
        """Get recent alerts"""
        try:
            result = self.client.table(self.table_alerts).select("*").order('sent_at', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            # Count total transactions
            total_txs = self.client.table(self.table_transactions).select('id', count='exact').execute()
            
            # Count flagged transactions
            flagged_txs = self.client.table(self.table_transactions).select('id', count='exact').eq('is_flagged', True).execute()
            
            # Count alerts
            total_alerts = self.client.table(self.table_alerts).select('id', count='exact').execute()
            
            return {
                'total_transactions': total_txs.count,
                'flagged_transactions': flagged_txs.count,
                'total_alerts': total_alerts.count
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def close(self):
        """Close database connection"""
        logger.info("Closing database connection")