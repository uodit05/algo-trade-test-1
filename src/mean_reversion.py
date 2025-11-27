from .strategy import Strategy
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

class MeanReversionStrategy(Strategy):
    def __init__(self, rsi_window=14, bb_window=20, bb_std=2.0):
        super().__init__("Mean Reversion (RSI + BB)")
        self.rsi_window = rsi_window
        self.bb_window = bb_window
        self.bb_std = bb_std
        
        # State per ticker
        self.history = {} 
        self.positions = {} 
        self.entry_prices = {}

    def reset(self):
        self.history = {}
        self.positions = {}
        self.entry_prices = {}

    def on_data(self, ticker, candle, portfolio):
        if ticker not in self.history:
            self.history[ticker] = pd.DataFrame()
            self.positions[ticker] = None
            self.entry_prices[ticker] = 0.0
            
        self.history[ticker] = pd.concat([self.history[ticker], candle.to_frame().T])
        
        if len(self.history[ticker]) < self.bb_window:
            return None

        hist = self.history[ticker]
        close_prices = hist['Close'].squeeze()
        
        if isinstance(close_prices, (float, int)):
             return None
             
        rsi = RSIIndicator(close=close_prices, window=self.rsi_window).rsi().iloc[-1]
        bb = BollingerBands(close=close_prices, window=self.bb_window, window_dev=self.bb_std)
        bb_lower = bb.bollinger_lband().iloc[-1]
        bb_upper = bb.bollinger_hband().iloc[-1]
        
        current_price = candle['Close']
        signal = None
        
        # Buy when price < Lower BB AND RSI < 30 (Oversold)
        if self.positions[ticker] is None:
            if current_price < bb_lower and rsi < 30:
                quantity = int(portfolio.cash * 0.05 / current_price) # 5% per trade
                if quantity > 0:
                    signal = {'action': 'BUY', 'quantity': quantity}
                    self.positions[ticker] = 'LONG'
                    self.entry_prices[ticker] = current_price
                    
        # Sell when price > Upper BB OR RSI > 70 (Overbought)
        elif self.positions[ticker] == 'LONG':
            if current_price > bb_upper or rsi > 70:
                signal = {'action': 'SELL', 'quantity': portfolio.positions.get(ticker, 0)}
                self.positions[ticker] = None
                self.entry_prices[ticker] = 0.0
                
        return signal

    def analyze_dataframe(self, df):
        # Placeholder for scanner
        return None
