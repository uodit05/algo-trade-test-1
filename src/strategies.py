from .strategy import Strategy
import pandas as pd
# import pandas_ta as ta # Removed as we are using 'ta' library
# I installed 'ta' library.
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

class TrendFollowingStrategy(Strategy):
    def __init__(self, short_window=20, long_window=50, rsi_window=14, stop_loss_atr_multiplier=2.0):
        super().__init__("Trend Following with Volatility Filter")
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_window = rsi_window
        self.stop_loss_atr_multiplier = stop_loss_atr_multiplier
        
        # State per ticker
        self.history = {} # ticker -> DataFrame
        self.positions = {} # ticker -> 'LONG' or None
        self.entry_prices = {} # ticker -> float
        self.stop_losses = {} # ticker -> float

    def reset(self):
        self.history = {}
        self.positions = {}
        self.entry_prices = {}
        self.stop_losses = {}

    def on_data(self, ticker, candle, portfolio):
        # Initialize state for ticker if not exists
        if ticker not in self.history:
            self.history[ticker] = pd.DataFrame()
            self.positions[ticker] = None
            self.entry_prices[ticker] = 0.0
            self.stop_losses[ticker] = 0.0
            
        # Append new candle to history
        self.history[ticker] = pd.concat([self.history[ticker], candle.to_frame().T])
        
        # Need enough data
        if len(self.history[ticker]) < self.long_window:
            return None

        # Calculate Indicators
        hist = self.history[ticker]
        close_prices = hist['Close'].squeeze()
        high_prices = hist['High'].squeeze()
        low_prices = hist['Low'].squeeze()
        
        # Handle scalar case
        if isinstance(close_prices, (float, int)):
             return None
             
        sma_short = SMAIndicator(close=close_prices, window=self.short_window).sma_indicator().iloc[-1]
        sma_long = SMAIndicator(close=close_prices, window=self.long_window).sma_indicator().iloc[-1]
        rsi = RSIIndicator(close=close_prices, window=self.rsi_window).rsi().iloc[-1]
        atr = AverageTrueRange(high=high_prices, low=low_prices, close=close_prices, window=14).average_true_range().iloc[-1]
        
        current_price = candle['Close']
        
        # Trading Logic
        signal = None
        
        # Check for Exit
        if self.positions[ticker] == 'LONG':
            # Exit if trend reverses or stop loss hit
            if sma_short < sma_long or current_price < self.stop_losses[ticker]:
                signal = {'action': 'SELL', 'quantity': portfolio.positions.get(ticker, 0)} # Sell all
                self.positions[ticker] = None
                self.entry_prices[ticker] = 0.0
                self.stop_losses[ticker] = 0.0
        
        # Check for Entry
        elif self.positions[ticker] is None:
            # Enter if Short SMA > Long SMA AND RSI is not overbought (< 70)
            if sma_short > sma_long and rsi < 70:
                # Position Sizing: Risk 2% of equity per trade
                risk_per_share = atr * self.stop_loss_atr_multiplier
                if risk_per_share > 0:
                    risk_amount = portfolio.cash * 0.02
                    quantity = int(risk_amount / risk_per_share)
                    
                    if quantity > 0 and (quantity * current_price) <= portfolio.cash:
                        signal = {'action': 'BUY', 'quantity': quantity}
                        self.positions[ticker] = 'LONG'
                        self.entry_prices[ticker] = current_price
                        self.stop_losses[ticker] = current_price - (atr * self.stop_loss_atr_multiplier)
        
        return signal

    def analyze_dataframe(self, df):
        """
        Vectorized analysis for the scanner.
        """
        if len(df) < self.long_window:
            return None
            
        close_prices = df['Close']
        high_prices = df['High']
        low_prices = df['Low']
        
        sma_short = SMAIndicator(close=close_prices, window=self.short_window).sma_indicator()
        sma_long = SMAIndicator(close=close_prices, window=self.long_window).sma_indicator()
        rsi = RSIIndicator(close=close_prices, window=self.rsi_window).rsi()
        atr = AverageTrueRange(high=high_prices, low=low_prices, close=close_prices, window=14).average_true_range()
        
        # Check latest values
        latest_sma_short = sma_short.iloc[-1]
        latest_sma_long = sma_long.iloc[-1]
        latest_rsi = rsi.iloc[-1]
        
        # Signal Logic (Buy Only for Scanner)
        if latest_sma_short > latest_sma_long and latest_rsi < 70:
            return {'action': 'BUY', 'atr': atr.iloc[-1], 'price': close_prices.iloc[-1]}
            
        return None
