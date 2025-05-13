# Crypto DCA Alert Bot

A Python-based cryptocurrency trading bot that monitors multiple crypto pairs on Binance and sends DCA (Dollar Cost Average) entry signals via Telegram when specific technical conditions are met.

## Features

- Multi-symbol monitoring (Currently configured for BTCUSDT and PAXGUSDT)
- Technical analysis using multiple indicators:
  - EMA (7, 14, and 50 periods)
  - RSI (Relative Strength Index)
  - ATR (Average True Range) for volatility measurement
- Buy signals with DCA (Dollar Cost Average) level calculations
- Sell signals for taking profits
- Real-time Telegram notifications for both buy and sell signals
- Configurable parameters for strategy customization
- Timezone-aware timestamps (Asia/Jakarta - UTC+7)

## Prerequisites

- Python 3.8 or higher
- Binance Account with API access
- Telegram Bot Token and Chat ID

## Dependencies

The project requires the following Python packages:
- pandas >= 2.0.0
- numpy >= 1.24.0
- python-binance >= 1.0.19
- python-telegram-bot >= 20.6
- TA-Lib >= 0.4.28
- requests >= 2.31.0
- certifi >= 2025.4.26
- python-dotenv >= 1.0.0
- pytz >= 2023.3

## Installing TA-Lib and Setting Up Environment

TA-Lib is required for technical analysis calculations. Follow these steps carefully for your operating system:

### Windows

1. Set up Python Virtual Environment:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Upgrade pip
python -m pip install --upgrade pip
```

2. Download and Install TA-Lib:
   - Download the TA-Lib installer from [ta-lib.org](https://ta-lib.org/install.html)
   - Run the installer (`ta-lib-0.4.0-msvc.zip`)
   - Extract the zip file
   - Copy the extracted files to `C:\ta-lib`

3. Install Python TA-Lib wrapper:
```powershell
pip install TA-Lib
```

### Ubuntu/Debian

1. Set up Python Virtual Environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

2. Install TA-Lib system dependencies:
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xvzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure
make
sudo make install
sudo ldconfig
```

3. Install Python TA-Lib wrapper:
```bash
pip install TA-Lib
```

4. If you encounter any issues, you might need to install additional dependencies:
```bash
sudo apt-get install python3-dev
```

### Verify Installation

After installation, you can verify that TA-Lib is working correctly:
```python
python -c "import talib; print(talib.__version__)"
```

## Project Installation

After setting up TA-Lib and activating your virtual environment:

1. Clone the repository or download the source code

2. Install the required packages:
```powershell
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root directory with the following variables:
```
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

2. Adjust the strategy parameters in `main.py` if needed:
- `RSI_BUY_THRESHOLD`: RSI level for buy signals (default: 30)
- `RSI_SELL_THRESHOLD`: RSI level for sell signals (default: 80)
- `DCA_LEVELS`: Number of DCA levels (default: 3)
- `DCA_PERCENTAGE`: Percentage difference between DCA levels (default: 5.0%)
- `SYMBOLS`: List of cryptocurrency pairs to monitor
- `INTERVAL`: Timeframe for analysis (default: 4 hours)

## Usage

Run the bot using:
```powershell
python main.py
```

The bot will:
1. Monitor the specified cryptocurrency pairs
2. Calculate technical indicators
3. Check for entry conditions
4. Send Telegram alerts when conditions are met
5. Include DCA levels in the alerts

## Alert Conditions

The bot generates two types of alerts:

### Buy Signals
Triggered when:
1. Price is below EMA7 and EMA14
2. RSI is below the buy threshold (default: 30)
3. No buy alert has been sent for the same symbol in the last hour

### Sell Signals
Triggered when:
1. Price is above EMA7 and EMA14
2. RSI is above the sell threshold (default: 80)
3. No sell alert has been sent for the same symbol in the last hour

## Telegram Alert Format

### Buy Alerts (🚨)
- Symbol and timeframe
- Current price
- Technical indicator values (EMAs, RSI)
- Volatility measurement
- DCA entry levels

### Sell Alerts (💰)
- Symbol and timeframe
- Current price
- Technical indicator values (EMAs, RSI)
- Volatility measurement

## Error Handling

- Comprehensive error logging
- Automatic retry mechanism
- Connection error handling for both Binance and Telegram APIs

## Notes

- The bot uses proper SSL verification for Binance API connections
- Timestamps are converted to Asia/Jakarta timezone (UTC+7)
- The bot includes a cooldown period of 1 hour between alerts for the same symbol
- Data is checked every 5 minutes for new signals

## Disclaimer

This bot is for educational purposes only. Always do your own research and use at your own risk. Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors.
