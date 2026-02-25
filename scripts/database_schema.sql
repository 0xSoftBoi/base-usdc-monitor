-- Base USDC Monitor Database Schema
-- Run this in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tx_hash TEXT UNIQUE NOT NULL,
    block_number BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    amount NUMERIC(36, 18) NOT NULL,
    amount_usd NUMERIC(18, 2),
    gas_used BIGINT,
    gas_price NUMERIC(36, 18),
    status TEXT DEFAULT 'confirmed',
    is_flagged BOOLEAN DEFAULT FALSE,
    pattern_score NUMERIC(5, 4) DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id TEXT,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    channels TEXT[],
    metadata JSONB
);

-- Addresses table (for tracking monitored addresses)
CREATE TABLE IF NOT EXISTS monitored_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT UNIQUE NOT NULL,
    label TEXT,
    added_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

-- Pattern detections table
CREATE TABLE IF NOT EXISTS pattern_detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id TEXT,
    pattern_type TEXT NOT NULL,
    score NUMERIC(5, 4) NOT NULL,
    details JSONB,
    detected_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_tx_hash ON transactions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_block_number ON transactions(block_number);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_from_address ON transactions(from_address);
CREATE INDEX IF NOT EXISTS idx_transactions_to_address ON transactions(to_address);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);
CREATE INDEX IF NOT EXISTS idx_transactions_is_flagged ON transactions(is_flagged);

CREATE INDEX IF NOT EXISTS idx_alerts_transaction_id ON alerts(transaction_id);
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_sent_at ON alerts(sent_at DESC);

CREATE INDEX IF NOT EXISTS idx_monitored_addresses_address ON monitored_addresses(address);
CREATE INDEX IF NOT EXISTS idx_monitored_addresses_is_active ON monitored_addresses(is_active);

-- Views for common queries

-- Recent 100 USDC transactions
CREATE OR REPLACE VIEW recent_100_usdc_transfers AS
SELECT *
FROM transactions
WHERE amount >= 99.99 AND amount <= 100.01
ORDER BY timestamp DESC
LIMIT 100;

-- Flagged transactions summary
CREATE OR REPLACE VIEW flagged_transactions_summary AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as count,
    SUM(amount) as total_amount,
    AVG(pattern_score) as avg_pattern_score
FROM transactions
WHERE is_flagged = TRUE
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Alert statistics
CREATE OR REPLACE VIEW alert_statistics AS
SELECT 
    alert_type,
    severity,
    COUNT(*) as count,
    DATE(sent_at) as date
FROM alerts
GROUP BY alert_type, severity, DATE(sent_at)
ORDER BY date DESC, count DESC;

-- Functions

-- Function to clean old records
CREATE OR REPLACE FUNCTION cleanup_old_records()
RETURNS void AS $$
BEGIN
    -- Delete transactions older than 1 year
    DELETE FROM transactions
    WHERE created_at < NOW() - INTERVAL '365 days';
    
    -- Delete alerts older than 90 days
    DELETE FROM alerts
    WHERE sent_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS) - Optional
-- Enable RLS if you want to restrict access
-- ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE monitored_addresses ENABLE ROW LEVEL SECURITY;

-- Create policies as needed
-- CREATE POLICY "Allow authenticated users" ON transactions
--   FOR ALL USING (auth.role() = 'authenticated');

-- Comments
COMMENT ON TABLE transactions IS 'Stores all USDC transaction records';
COMMENT ON TABLE alerts IS 'Stores alert records sent by the monitoring system';
COMMENT ON TABLE monitored_addresses IS 'List of addresses being monitored';
COMMENT ON TABLE pattern_detections IS 'Records of detected patterns in transactions';