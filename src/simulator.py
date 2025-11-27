import pandas as pd
import time

class Simulator:
    def __init__(self, data_loader, strategy, portfolio):
        self.data_loader = data_loader
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self):
        print("Starting simulation...")
        # Use get_latest_candles which yields (timestamp, snapshot_dict)
        candle_stream = self.data_loader.get_latest_candles()
        
        for timestamp, snapshot in candle_stream:
            # Update portfolio equity based on current prices of all tickers in snapshot
            current_prices = {ticker: candle['Close'] for ticker, candle in snapshot.items()}
            self.portfolio.update_equity(current_prices)
            
            # For each ticker in the snapshot, run the strategy
            for ticker, candle in snapshot.items():
                signal = self.strategy.on_data(ticker, candle, self.portfolio)
                
                if signal:
                    action = signal['action']
                    quantity = signal['quantity']
                    price = candle['Close']
                    
                    self.portfolio.execute_trade(ticker, action, quantity, price, timestamp)
                
        print("Simulation finished.")
        self.print_summary()

    def print_summary(self):
        final_equity = self.portfolio.equity_curve[-1] if self.portfolio.equity_curve else self.portfolio.initial_cash
        pnl = final_equity - self.portfolio.initial_cash
        return_pct = (pnl / self.portfolio.initial_cash) * 100
        
        print("\n--- Performance Summary ---")
        print(f"Initial Cash: ${self.portfolio.initial_cash:.2f}")
        print(f"Final Equity: ${final_equity:.2f}")
        print(f"Total P&L: ${pnl:.2f} ({return_pct:.2f}%)")
        print(f"Total Trades: {len(self.portfolio.trade_history)}")
