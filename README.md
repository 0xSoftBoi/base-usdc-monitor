# Base USDC Monitor 🔍

A comprehensive wallet monitoring system for tracking USDC transfers on the Base network (Coinbase Layer 2). This system monitors transactions, detects unusual patterns, sends real-time alerts, and stores data in Supabase.

## Features ✨

- 🌐 **Base Network Integration**: Direct RPC connection to Base mainnet
- 💰 **USDC Transaction Monitoring**: Real-time tracking of USDC (ERC-20) transfers
- 🎯 **100 USDC Detection**: Special focus on 100 USDC transactions
- 🔔 **Multi-Channel Alerts**: Telegram, Email, Discord, and Webhook notifications
- 🧠 **Pattern Detection**: ML-based anomaly detection for unusual transaction patterns
- 📊 **Supabase Integration**: Automatic database updates with transaction data
- 🔗 **API Integrations**: Basescan and Bitquery API support
- 📈 **Real-time Dashboard**: Web interface for monitoring (optional)

## Architecture 🏗️

```
base-usdc-monitor/
├── src/
│   ├── monitor.py              # Main monitoring script
│   ├── rpc_connector.py        # Base network RPC connection
│   ├── usdc_tracker.py         # USDC transfer detection
│   ├── pattern_detector.py     # Anomaly detection engine
│   ├── alert_manager.py        # Alert system (Telegram, Email, etc.)
│   ├── database.py             # Supabase integration
│   ├── basescan_api.py         # Basescan API client
│   └── bitquery_api.py         # Bitquery GraphQL client
├── config/
│   ├── config.yaml             # Configuration file
│   └── contracts.json          # USDC contract addresses
├── data/
│   └── patterns/               # Stored pattern models
├── logs/                       # Application logs
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── docker-compose.yml          # Docker setup
└── README.md                   # This file
```

## Quick Start 🚀

### Prerequisites

- Python 3.9+
- Base RPC endpoint (Alchemy, Infura, or public)
- Supabase account and API keys
- Basescan API key
- Bitquery API key
- Telegram Bot Token (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/0xSoftBoi/base-usdc-monitor.git
cd base-usdc-monitor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Set up Supabase database**
```sql
-- Run the SQL schema in scripts/database_schema.sql
```

5. **Run the monitor**
```bash
python src/monitor.py
```

### Docker Setup

```bash
docker-compose up -d
```

## Configuration ⚙️

### Environment Variables

Create a `.env` file with the following variables:

```env
# Base Network
BASE_RPC_URL=https://mainnet.base.org
BASE_CHAIN_ID=8453

# USDC Contract (Base mainnet)
USDC_CONTRACT_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

# Monitoring Configuration
MONITOR_ADDRESSES=0xAddress1,0xAddress2
TARGET_AMOUNT=100
POLL_INTERVAL=12

# Supabase
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key

# Basescan API
BASESCAN_API_KEY=your-basescan-api-key
BASESCAN_API_URL=https://api.basescan.org/api

# Bitquery API
BITQUERY_API_KEY=your-bitquery-api-key
BITQUERY_ENDPOINT=https://graphql.bitquery.io

# Alert Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=recipient@email.com

# Discord Webhook (optional)
DISCORD_WEBHOOK_URL=your-discord-webhook-url

# Pattern Detection
ANOMALY_THRESHOLD=0.85
PATTERN_WINDOW=100
```

### Monitoring Specific Wallets

Edit `config/config.yaml` to specify wallets to monitor:

```yaml
wallet_monitoring:
  enabled: true
  addresses:
    - "0xYourWalletAddress1"
    - "0xYourWalletAddress2"
  
transaction_filters:
  min_amount: 50  # Minimum USDC amount to track
  max_amount: 10000  # Maximum USDC amount to track
  target_amount: 100  # Special attention to this amount
  
pattern_detection:
  enabled: true
  algorithms:
    - isolation_forest
    - statistical_threshold
  thresholds:
    frequency_spike: 5  # transactions per hour
    amount_deviation: 3  # standard deviations
```

## Usage 📖

### Basic Monitoring

```python
from src.monitor import USDCMonitor

# Initialize monitor
monitor = USDCMonitor()

# Start monitoring
monitor.start()
```

### Monitor Specific Address

```python
from src.usdc_tracker import USDCTracker

tracker = USDCTracker()
tracker.track_address("0xYourAddress")
```

### Query Historical Data

```python
from src.basescan_api import BasescanAPI

api = BasescanAPI()
transactions = api.get_erc20_transfers(
    contract_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    address="0xYourAddress",
    start_block=0,
    end_block=99999999
)
```

### Pattern Detection

```python
from src.pattern_detector import PatternDetector

detector = PatternDetector()
anomalies = detector.detect_anomalies(transactions)
```

## Alert Types 🔔

1. **100 USDC Transaction Alert**: Immediate notification when exactly 100 USDC is transferred
2. **Large Transfer Alert**: Notifications for transfers above threshold
3. **Frequency Alert**: Unusual transaction frequency detected
4. **Pattern Alert**: Suspicious patterns identified
5. **New Address Alert**: First-time interactions with monitored addresses

## API Integration Details 🔌

### Basescan API

Supported endpoints:
- Get ERC-20 token transfers
- Get transaction details
- Get account balance
- Get contract ABI

### Bitquery API

GraphQL queries for:
- Real-time transfer monitoring
- Historical data analysis
- Token holder information
- DEX trade tracking

## Database Schema 📊

### Transactions Table

```sql
CREATE TABLE transactions (
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
    status TEXT,
    is_flagged BOOLEAN DEFAULT FALSE,
    pattern_score NUMERIC(5, 4),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Alerts Table

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID REFERENCES transactions(id),
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    channels TEXT[]
);
```

## Pattern Detection 🧠

The system uses multiple algorithms to detect unusual patterns:

1. **Isolation Forest**: Detects outliers in transaction behavior
2. **Statistical Analysis**: Z-score and standard deviation checks
3. **Time-based Patterns**: Identifies unusual timing patterns
4. **Amount Clustering**: Groups similar transaction amounts
5. **Velocity Checks**: Monitors transaction frequency

## Monitoring Dashboard 📈

(Optional) A web dashboard is available for real-time monitoring:

```bash
cd dashboard
npm install
npm start
```

Access at: `http://localhost:3000`

## Testing 🧪

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_usdc_tracker.py

# Run with coverage
pytest --cov=src tests/
```

## Deployment 🚢

### AWS EC2

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Clone and setup
git clone https://github.com/0xSoftBoi/base-usdc-monitor.git
cd base-usdc-monitor
pip install -r requirements.txt

# Run as service
sudo systemctl enable base-usdc-monitor
sudo systemctl start base-usdc-monitor
```

### Docker

```bash
docker build -t base-usdc-monitor .
docker run -d --env-file .env base-usdc-monitor
```

## Performance 🚄

- **Latency**: < 3 seconds for transaction detection
- **Throughput**: 1000+ transactions/minute
- **Memory**: ~200MB typical usage
- **CPU**: Low (< 5% on modern hardware)

## Troubleshooting 🔧

### RPC Connection Issues

```bash
# Test RPC connection
python scripts/test_rpc.py
```

### Database Connection

```bash
# Test Supabase connection
python scripts/test_database.py
```

### Alert System

```bash
# Test alert delivery
python scripts/test_alerts.py
```

## Security 🔒

- Never commit `.env` file or API keys
- Use read-only RPC endpoints when possible
- Implement rate limiting for API calls
- Regular security audits recommended
- Keep dependencies updated

## Contributing 🤝

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap 🗺️

- [ ] Support for multiple tokens (USDT, DAI, etc.)
- [ ] Machine learning model improvements
- [ ] Mobile app for alerts
- [ ] Advanced analytics dashboard
- [ ] Multi-chain support (Optimism, Arbitrum)
- [ ] Webhook API for integrations
- [ ] Historical data export

## License 📄

MIT License - see LICENSE file for details

## Support 💬

- GitHub Issues: Report bugs or request features
- Discord: Join our community (link)
- Email: support@example.com

## Acknowledgments 🙏

- Base Network by Coinbase
- Supabase for database infrastructure
- Basescan for blockchain explorer API
- Bitquery for GraphQL analytics
- Web3.py community

## Disclaimer ⚠️

This tool is for monitoring and educational purposes. Always verify transactions independently. Not financial advice.

---

**Built with ❤️ by [0xSoftBoi](https://github.com/0xSoftBoi)**

**Star ⭐ this repo if you find it useful!**