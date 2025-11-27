# Algorithmic Trading System

A real-time algorithmic trading simulation platform with a premium web-based dashboard. This system monitors multiple stocks, executes trades based on configurable strategies, and provides live visualization of portfolio performance.

## Features

### 🎯 Core Capabilities
- **Real-time Simulation**: Streams historical data candle-by-candle to simulate live trading
- **Hourly Resolution**: Uses 1-hour candles for precise market analysis
- **Multi-Asset Support**: Monitors and trades across a universe of stocks simultaneously
- **Market Scanner**: Identifies trading opportunities across the entire watchlist

### 📊 Trading Strategies
- **Trend Following**: SMA crossovers (20/50) with RSI filter and ATR-based stop loss
- **Mean Reversion**: Bollinger Bands with RSI for oversold/overbought detection

### 🎨 Premium Web UI
- **Interactive Controls**: Start/Stop simulation, switch strategies on the fly
- **Configurable Settings**: Set initial investment and toggle broker fees
- **Real-time Dashboard**: Live updates of equity, P&L, positions, and trade log
- **Dark Mode Design**: Modern glassmorphism UI with smooth animations

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Create and activate virtual environment**
```bash
python -m venv algo-trade-test-1_venv
source algo-trade-test-1_venv/bin/activate  # On Windows: algo-trade-test-1_venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn yfinance pandas numpy ta websockets
```

## Usage

### Starting the Server

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Accessing the Dashboard

Open your browser and navigate to:
```
http://localhost:8000/static/index.html
```

### Running a Simulation

1. **Configure Settings**:
   - Set your **Initial Investment** (e.g., $100,000)
   - Toggle **Broker Fees** (0.1% commission per trade)
   - Select a **Strategy** (Trend Following or Mean Reversion)

2. **Start Simulation**:
   - Click the **Start** button
   - Watch real-time updates on the dashboard

3. **Monitor Performance**:
   - Track equity curve and P&L
   - View active positions
   - Review trade history

4. **Stop/Restart**:
   - Click **Stop** to pause
   - Adjust settings and restart with new configuration

## Project Structure

```
algo-trade/test-1/
├── server.py                 # FastAPI backend and simulation runner
├── src/
│   ├── data_loader.py       # Fetches and streams market data
│   ├── strategy.py          # Abstract strategy interface
│   ├── strategies.py        # Trend Following strategy
│   ├── mean_reversion.py    # Mean Reversion strategy
│   ├── portfolio.py         # Portfolio and risk management
│   ├── simulator.py         # Simulation engine
│   └── scanner.py           # Market scanner for opportunity detection
├── static/
│   ├── index.html           # Dashboard UI
│   ├── style.css            # Premium dark mode styling
│   └── app.js               # Frontend logic and WebSocket handling
└── README.md
```

## Configuration

### Universe of Stocks
Default watchlist (configurable in `server.py`):
```python
universe = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD', 'NFLX', 'INTC']
```

### Data Settings
- **Interval**: 1 hour (`1h`)
- **Period**: 60 days (`60d`)
- **Source**: Yahoo Finance via `yfinance`

### Strategy Parameters

#### Trend Following
- Short SMA: 20 periods
- Long SMA: 50 periods
- RSI Window: 14 periods
- Stop Loss: 2x ATR

#### Mean Reversion
- Bollinger Bands: 20 periods, 2 std dev
- RSI Window: 14 periods
- Entry: Price < Lower BB and RSI < 30
- Exit: Price > Upper BB or RSI > 70

## API Endpoints

### WebSocket
- `ws://localhost:8000/ws` - Real-time simulation updates

### REST API
- `POST /api/start` - Start simulation with configuration
  ```json
  {
    "initial_cash": 100000.0,
    "enable_broker_charges": false
  }
  ```
- `POST /api/stop` - Stop running simulation
- `POST /api/strategy` - Change active strategy
  ```json
  {
    "name": "TrendFollowing"
  }
  ```
- `GET /api/status` - Get current simulation status

## Performance Metrics

The dashboard displays:
- **Equity**: Total portfolio value (cash + positions)
- **P&L**: Profit/Loss in dollars
- **Return**: Percentage return on initial investment
- **Active Positions**: Current holdings with quantities and values
- **Trade Log**: Complete history of all executed trades

## Risk Management

### Position Sizing
- Trend Following: Risks 2% of equity per trade based on ATR
- Mean Reversion: Allocates 5% of cash per trade

### Broker Fees
When enabled, applies 0.1% commission on both buy and sell orders:
- Buy: `total_cost = (quantity × price) + commission`
- Sell: `total_revenue = (quantity × price) - commission`

## Limitations

### Data Constraints
- `yfinance` provides hourly data for the last 730 days
- Current configuration uses 60 days for faster loading
- Rate limits may apply for frequent requests

### Simulation vs Live Trading
- This is a **backtesting/simulation** system
- Does not connect to real brokers or execute live trades
- Assumes perfect order execution at closing prices

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use a different port
uvicorn server:app --host 0.0.0.0 --port 8080
```

### No data loading
- Check internet connection
- Verify `yfinance` is installed: `pip install yfinance`
- Try reducing the universe size or period

### UI not updating
- Ensure WebSocket connection is established (check browser console)
- Verify simulation is running (check terminal logs)
- Refresh the page and restart simulation

## Future Enhancements

- [ ] Add more trading strategies (Momentum, Pairs Trading, etc.)
- [ ] Implement backtesting with historical date ranges
- [ ] Add performance analytics (Sharpe ratio, max drawdown, etc.)
- [ ] Support for custom stock universes
- [ ] Export trade history and reports
- [ ] Paper trading mode with live data
- [ ] Multi-timeframe analysis

## License

This project is for educational and research purposes only. Not intended for live trading.

## Acknowledgments

- Market data provided by [Yahoo Finance](https://finance.yahoo.com/)
- Technical indicators from [ta](https://github.com/bukosabino/ta) library
- Built with [FastAPI](https://fastapi.tiangolo.com/) and vanilla JavaScript