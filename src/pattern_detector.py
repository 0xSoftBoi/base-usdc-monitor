#!/usr/bin/env python3
"""
Pattern Detection Engine
Detects unusual patterns in USDC transactions using ML and statistical methods
"""

import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import os

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Pattern detection will use statistical methods only.")

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Detects anomalous patterns in USDC transactions
    """
    
    def __init__(self):
        self.anomaly_threshold = float(os.getenv('ANOMALY_THRESHOLD', '0.85'))
        self.pattern_window = int(os.getenv('PATTERN_WINDOW', '100'))
        self.frequency_threshold = int(os.getenv('FREQUENCY_SPIKE_THRESHOLD', '5'))
        self.amount_deviation_threshold = float(os.getenv('AMOUNT_DEVIATION_THRESHOLD', '3'))
        
        # Transaction history for pattern analysis
        self.transaction_history = []
        self.address_stats = defaultdict(lambda: {'count': 0, 'amounts': [], 'timestamps': []})
        
        # Initialize ML model if available
        if SKLEARN_AVAILABLE:
            self.isolation_forest = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            self.scaler = StandardScaler()
            self.model_trained = False
        else:
            self.isolation_forest = None
            self.model_trained = False
        
        logger.info("Pattern Detector initialized")
    
    async def analyze_transaction(self, transaction: Dict) -> float:
        """
        Analyze a transaction and return anomaly score (0-1)
        Higher score = more anomalous
        """
        try:
            scores = []
            
            # Update history
            self._update_history(transaction)
            
            # Statistical analysis
            stat_score = self._statistical_analysis(transaction)
            scores.append(stat_score)
            
            # Frequency analysis
            freq_score = self._frequency_analysis(transaction)
            scores.append(freq_score)
            
            # Amount clustering analysis
            amount_score = self._amount_analysis(transaction)
            scores.append(amount_score)
            
            # Timing analysis
            timing_score = self._timing_analysis(transaction)
            scores.append(timing_score)
            
            # ML-based analysis (if available and trained)
            if self.model_trained and len(self.transaction_history) >= self.pattern_window:
                ml_score = self._ml_analysis(transaction)
                scores.append(ml_score)
            
            # Combine scores (weighted average)
            final_score = np.mean(scores)
            
            logger.debug(f"Transaction anomaly score: {final_score:.4f}")
            return float(final_score)
            
        except Exception as e:
            logger.error(f"Error analyzing transaction: {e}", exc_info=True)
            return 0.0
    
    def _update_history(self, transaction: Dict):
        """Update transaction history"""
        self.transaction_history.append(transaction)
        
        # Keep only recent transactions
        if len(self.transaction_history) > self.pattern_window * 2:
            self.transaction_history = self.transaction_history[-self.pattern_window:]
        
        # Update address statistics
        from_addr = transaction.get('from_address')
        to_addr = transaction.get('to_address')
        amount = transaction.get('amount', 0)
        timestamp = transaction.get('timestamp')
        
        for addr in [from_addr, to_addr]:
            if addr:
                self.address_stats[addr]['count'] += 1
                self.address_stats[addr]['amounts'].append(amount)
                self.address_stats[addr]['timestamps'].append(timestamp)
    
    def _statistical_analysis(self, transaction: Dict) -> float:
        """Statistical analysis based on amount deviations"""
        try:
            if len(self.transaction_history) < 10:
                return 0.0
            
            amounts = [t.get('amount', 0) for t in self.transaction_history]
            current_amount = transaction.get('amount', 0)
            
            mean_amount = np.mean(amounts)
            std_amount = np.std(amounts)
            
            if std_amount == 0:
                return 0.0
            
            # Calculate z-score
            z_score = abs((current_amount - mean_amount) / std_amount)
            
            # Convert to 0-1 score
            score = min(z_score / self.amount_deviation_threshold, 1.0)
            
            return score
            
        except Exception as e:
            logger.error(f"Error in statistical analysis: {e}")
            return 0.0
    
    def _frequency_analysis(self, transaction: Dict) -> float:
        """Analyze transaction frequency for addresses"""
        try:
            from_addr = transaction.get('from_address')
            to_addr = transaction.get('to_address')
            
            scores = []
            
            for addr in [from_addr, to_addr]:
                if addr and addr in self.address_stats:
                    stats = self.address_stats[addr]
                    
                    # Check recent transaction frequency
                    recent_timestamps = stats['timestamps'][-10:]
                    if len(recent_timestamps) >= 2:
                        # Calculate average time between transactions
                        time_diffs = []
                        for i in range(1, len(recent_timestamps)):
                            try:
                                t1 = datetime.fromisoformat(recent_timestamps[i-1])
                                t2 = datetime.fromisoformat(recent_timestamps[i])
                                diff = (t2 - t1).total_seconds() / 3600  # hours
                                time_diffs.append(diff)
                            except:
                                continue
                        
                        if time_diffs:
                            avg_hours = np.mean(time_diffs)
                            
                            # High frequency = low hours between transactions
                            if avg_hours < 1:  # Less than 1 hour average
                                frequency_score = 0.8
                            elif avg_hours < 6:  # Less than 6 hours
                                frequency_score = 0.5
                            else:
                                frequency_score = 0.1
                            
                            scores.append(frequency_score)
            
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Error in frequency analysis: {e}")
            return 0.0
    
    def _amount_analysis(self, transaction: Dict) -> float:
        """Analyze if amount is part of unusual clustering"""
        try:
            current_amount = transaction.get('amount', 0)
            
            # Check for exact amount repetition
            recent_amounts = [t.get('amount', 0) for t in self.transaction_history[-20:]]
            exact_matches = sum(1 for amt in recent_amounts if abs(amt - current_amount) < 0.01)
            
            # High repetition of exact amounts is suspicious
            if exact_matches >= 5:
                return 0.9
            elif exact_matches >= 3:
                return 0.6
            
            # Check for round numbers (100, 1000, 10000, etc.)
            if current_amount in [100, 500, 1000, 5000, 10000, 50000, 100000]:
                return 0.7
            
            return 0.2
            
        except Exception as e:
            logger.error(f"Error in amount analysis: {e}")
            return 0.0
    
    def _timing_analysis(self, transaction: Dict) -> float:
        """Analyze transaction timing patterns"""
        try:
            timestamp_str = transaction.get('timestamp')
            if not timestamp_str:
                return 0.0
            
            timestamp = datetime.fromisoformat(timestamp_str)
            hour = timestamp.hour
            
            # Unusual hours (2 AM - 5 AM) get higher score
            if 2 <= hour <= 5:
                return 0.6
            
            # Check if part of rapid succession
            if len(self.transaction_history) >= 2:
                last_tx = self.transaction_history[-2]
                last_timestamp = datetime.fromisoformat(last_tx.get('timestamp'))
                
                time_diff = (timestamp - last_timestamp).total_seconds()
                
                # Transactions within 30 seconds
                if time_diff < 30:
                    return 0.8
                elif time_diff < 300:  # 5 minutes
                    return 0.5
            
            return 0.1
            
        except Exception as e:
            logger.error(f"Error in timing analysis: {e}")
            return 0.0
    
    def _ml_analysis(self, transaction: Dict) -> float:
        """ML-based anomaly detection using Isolation Forest"""
        try:
            if not SKLEARN_AVAILABLE or not self.model_trained:
                return 0.0
            
            # Extract features
            features = self._extract_features(transaction)
            
            # Predict anomaly score
            score = self.isolation_forest.score_samples([features])[0]
            
            # Convert to 0-1 range (lower score = more anomalous)
            normalized_score = (1 - (score + 1) / 2)  # Normalize from [-1, 1] to [0, 1]
            
            return float(normalized_score)
            
        except Exception as e:
            logger.error(f"Error in ML analysis: {e}")
            return 0.0
    
    def _extract_features(self, transaction: Dict) -> List[float]:
        """Extract numerical features from transaction"""
        features = [
            transaction.get('amount', 0),
            transaction.get('gas_used', 0) or 0,
            float(transaction.get('gas_price', 0) or 0),
            transaction.get('block_number', 0),
        ]
        return features
    
    async def train_model(self, historical_transactions: List[Dict]):
        """Train the ML model on historical data"""
        if not SKLEARN_AVAILABLE:
            logger.warning("Cannot train model: scikit-learn not available")
            return
        
        try:
            logger.info(f"Training pattern detection model on {len(historical_transactions)} transactions")
            
            # Extract features
            features = [self._extract_features(tx) for tx in historical_transactions]
            
            # Fit scaler and model
            features_scaled = self.scaler.fit_transform(features)
            self.isolation_forest.fit(features_scaled)
            
            self.model_trained = True
            logger.info("Pattern detection model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training model: {e}", exc_info=True)
    
    def get_statistics(self) -> Dict:
        """Get current pattern detection statistics"""
        return {
            'total_transactions_analyzed': len(self.transaction_history),
            'unique_addresses': len(self.address_stats),
            'model_trained': self.model_trained,
            'anomaly_threshold': self.anomaly_threshold
        }