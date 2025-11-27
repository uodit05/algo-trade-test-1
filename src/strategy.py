from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def on_data(self, ticker, candle, portfolio):
        """
        Called when a new candle is received.
        
        Args:
            ticker (str): The ticker symbol.
            candle (pd.Series): The latest candle data (Open, High, Low, Close, Volume).
            portfolio (Portfolio): The current portfolio state.
            
        Returns:
            dict: Trade signal e.g., {'action': 'BUY', 'quantity': 10} or None.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Resets the strategy state.
        """
        pass

    def analyze_dataframe(self, df):
        """
        Analyzes a whole DataFrame and returns the latest signal.
        Optional to implement for optimization.
        """
        return None
