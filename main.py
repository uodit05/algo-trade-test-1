from src.data_loader import DataLoader
from src.portfolio import Portfolio
from src.simulator import Simulator
from src.strategies import TrendFollowingStrategy
import sys

def main():
    ticker = 'AAPL' # Default ticker
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        
    print(f"Initializing simulation for {ticker}...")
    
    # 1. Load Data
    # Fetching 1 year of data to have enough history for indicators
    loader = DataLoader(ticker, interval='1d', period='2y') 
    
    # 2. Initialize Portfolio
    portfolio = Portfolio(initial_cash=100000.0)
    
    # 3. Initialize Strategy
    strategy = TrendFollowingStrategy(short_window=20, long_window=50)
    
    # 4. Run Simulation
    sim = Simulator(loader, strategy, portfolio)
    sim.run()

if __name__ == "__main__":
    main()
