from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from src.data_loader import DataLoader
from src.portfolio import Portfolio
from src.strategies import TrendFollowingStrategy
from src.mean_reversion import MeanReversionStrategy
from src.scanner import MarketScanner

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

from pydantic import BaseModel

# Global State
portfolio = Portfolio(initial_cash=100000.0)
strategies = {
    "TrendFollowing": TrendFollowingStrategy(),
    "MeanReversion": MeanReversionStrategy()
}
active_strategy_name = "TrendFollowing"
strategy = strategies[active_strategy_name]

# Universe of stocks
# Universe of stocks
universe = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD', 'NFLX', 'INTC']
# yfinance limitation: 1h data is available for last 730 days, but let's use 60d to be safe and fast
data_loader = DataLoader(universe, interval='1h', period='60d')
scanner = MarketScanner(universe, strategy)

connected_clients = []
simulation_task = None
is_running = False

class StrategyRequest(BaseModel):
    name: str

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection open
    except:
        connected_clients.remove(websocket)

async def broadcast(message):
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            pass

async def run_simulation_loop():
    """
    Runs the simulation step-by-step and broadcasts updates.
    """
    global is_running
    print("Starting simulation loop...")
    is_running = True
    candle_stream = data_loader.get_latest_candles()
    
    try:
        for timestamp, snapshot in candle_stream:
            if not is_running:
                break
                
            # 1. Update Portfolio Equity
            current_prices = {ticker: candle['Close'] for ticker, candle in snapshot.items()}
            portfolio.update_equity(current_prices)
            
            # 2. Run Strategy
            trades = []
            for ticker, candle in snapshot.items():
                signal = strategy.on_data(ticker, candle, portfolio)
                if signal:
                    action = signal['action']
                    quantity = signal['quantity']
                    price = candle['Close']
                    if portfolio.execute_trade(ticker, action, quantity, price, timestamp):
                        trades.append({
                            'ticker': ticker,
                            'action': action,
                            'quantity': quantity,
                            'price': price,
                            'timestamp': str(timestamp)
                        })
            
            # 3. Broadcast Update
            update = {
                'type': 'update',
                'timestamp': str(timestamp),
                'equity': portfolio.equity_curve[-1],
                'cash': portfolio.cash,
                'positions': portfolio.positions,
                'trades': trades,
                'prices': {t: c['Close'] for t, c in snapshot.items()}
            }
            await broadcast(update)
            
            # Simulate delay for visual effect
            await asyncio.sleep(0.1) 
            
        print("Simulation finished.")
        await broadcast({'type': 'finished'})
    except asyncio.CancelledError:
        print("Simulation cancelled.")
    finally:
        is_running = False

class StartSimulationRequest(BaseModel):
    initial_cash: float = 100000.0
    enable_broker_charges: bool = False

@app.post("/api/start")
async def start_simulation(req: StartSimulationRequest):
    global simulation_task, is_running, portfolio
    if is_running:
        return {"status": "already_running"}
    
    # Re-initialize portfolio with user settings
    commission_rate = 0.001 if req.enable_broker_charges else 0.0
    portfolio = Portfolio(initial_cash=req.initial_cash, commission_rate=commission_rate)
    
    # Reset strategy state
    strategy.reset()
    
    simulation_task = asyncio.create_task(run_simulation_loop())
    return {"status": "started", "config": req.dict()}

@app.post("/api/stop")
async def stop_simulation():
    global simulation_task, is_running
    if not is_running:
        return {"status": "not_running"}
    
    is_running = False
    if simulation_task:
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass
    return {"status": "stopped"}

@app.post("/api/strategy")
async def set_strategy(req: StrategyRequest):
    global strategy, active_strategy_name
    if req.name in strategies:
        active_strategy_name = req.name
        strategy = strategies[active_strategy_name]
        return {"status": "ok", "strategy": active_strategy_name}
    return {"status": "error", "message": "Strategy not found"}

@app.get("/api/status")
def get_status():
    return {
        "is_running": is_running,
        "active_strategy": active_strategy_name,
        "strategies": list(strategies.keys())
    }

# @app.on_event("startup")
# async def startup_event():
#     # Start simulation in background
#     asyncio.create_task(run_simulation_loop())

@app.get("/")
def read_root():
    return {"status": "ok"}
