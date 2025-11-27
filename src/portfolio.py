class Portfolio:
    def __init__(self, initial_cash=10000.0, commission_rate=0.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.positions = {}  # ticker -> quantity
        self.trade_history = []
        self.equity_curve = []

    def update_equity(self, current_prices):
        equity = self.cash
        for ticker, quantity in self.positions.items():
            if ticker in current_prices:
                equity += quantity * current_prices[ticker]
        self.equity_curve.append(equity)
        return equity

    def execute_trade(self, ticker, action, quantity, price, timestamp):
        trade_value = quantity * price
        commission = trade_value * self.commission_rate
        
        if action == 'BUY':
            total_cost = trade_value + commission
            if self.cash >= total_cost:
                self.cash -= total_cost
                self.positions[ticker] = self.positions.get(ticker, 0) + quantity
                self.trade_history.append({
                    'timestamp': timestamp,
                    'ticker': ticker,
                    'action': 'BUY',
                    'quantity': quantity,
                    'price': price,
                    'cost': total_cost,
                    'commission': commission
                })
                print(f"[{timestamp}] BOUGHT {quantity} {ticker} @ {price:.2f} (Comm: {commission:.2f})")
                return True
            else:
                print(f"[{timestamp}] INSUFFICIENT FUNDS to BUY {quantity} {ticker}")
                return False
                
        elif action == 'SELL':
            current_qty = self.positions.get(ticker, 0)
            if current_qty >= quantity:
                total_revenue = trade_value - commission
                self.cash += total_revenue
                self.positions[ticker] -= quantity
                if self.positions[ticker] == 0:
                    del self.positions[ticker]
                self.trade_history.append({
                    'timestamp': timestamp,
                    'ticker': ticker,
                    'action': 'SELL',
                    'quantity': quantity,
                    'price': price,
                    'revenue': total_revenue,
                    'commission': commission
                })
                print(f"[{timestamp}] SOLD {quantity} {ticker} @ {price:.2f} (Comm: {commission:.2f})")
                return True
            else:
                print(f"[{timestamp}] INSUFFICIENT POSITIONS to SELL {quantity} {ticker}")
                return False
        return False

class RiskManager:
    def __init__(self, max_position_size=0.1, stop_loss_pct=0.02):
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct

    def validate_order(self, portfolio, action, quantity, price):
        # Simple validation logic
        if action == 'BUY':
            cost = quantity * price
            if cost > portfolio.cash:
                return False
            # Check if position size is too large relative to portfolio
            # (Simplified for now)
        return True
