from .data_loader import DataLoader
import pandas as pd

class MarketScanner:
    def __init__(self, universe, strategy):
        self.universe = universe
        self.strategy = strategy
        self.data_loader = DataLoader(universe, interval='1d', period='1y')

    def scan(self):
        """
        Scans the universe and returns a list of tickers with BUY signals.
        """
        print("Scanning market...")
        # Fetch history for analysis
        self.data_loader.fetch_history()
        
        candidates = []
        
        for ticker, df in self.data_loader.data.items():
            if df.empty:
                continue
                
            signal = self.strategy.analyze_dataframe(df)
            
            if signal and signal['action'] == 'BUY':
                candidates.append({
                    'ticker': ticker,
                    'price': signal['price'],
                    'atr': signal['atr']
                })
                
        # Sort by some metric? Maybe just return all candidates.
        print(f"Found {len(candidates)} candidates.")
        return candidates
