# src/portfolio/portfolio.py

from datetime import datetime
from src.core.events import SignalEvent, OrderEvent, FillEvent


class Portfolio:
    """
    Minimal Portfolio v2:
    - Converts Signal -> Order
    - Tracks cash + positions
    - Updates holdings on Fill events

    Later we add:
    - unrealized PnL
    - risk limits
    - inventory targets
    """

    def __init__(self, base_quantity: int = 10, initial_capital: float = 1_000_000):
        self.base_quantity = base_quantity
        self.initial_capital = initial_capital

        self.cash = initial_capital
        self.positions = {}  # symbol -> shares
        self.avg_cost = {}
        self.realized_pnl = 0.0
        self.total_commission = 0.0
        self.last_prices = {}      # symbol -> last mid/last price
        self.unrealized_pnl = 0.0
        self.nav = initial_capital
        self.history = []

    def on_signal(self, signal: SignalEvent):
        """
        Convert SignalEvent into OrderEvent.
        """
        if signal.signal_type not in ["BUY", "SELL"]:
            return None

        qty = int(self.base_quantity * signal.strength)

        order = OrderEvent(
            symbol=signal.symbol,
            timestamp=datetime.utcnow(),
            order_type="MKT",
            direction=signal.signal_type,
            quantity=qty
        )
        return order

    def on_fill(self, fill: FillEvent):
        """
        Update positions, cash, avg cost, and realized PnL after a fill.
        """
        sym = fill.symbol
        qty = fill.quantity
        px = fill.fill_price
        comm = fill.commission
    
        self.total_commission += comm
    
        pos = self.positions.get(sym, 0)
        avg = self.avg_cost.get(sym, 0.0)
    
        if fill.direction == "BUY":
            # New position after buy
            new_pos = pos + qty
    
            # Update average cost only if position increases
            if new_pos != 0:
                # Weighted average price
                new_avg = (pos * avg + qty * px) / new_pos
            else:
                new_avg = 0.0
    
            self.positions[sym] = new_pos
            self.avg_cost[sym] = new_avg
    
            self.cash -= qty * px + comm
    
        elif fill.direction == "SELL":
            new_pos = pos - qty
    
            # Realized PnL only happens when you reduce/close a position
            # We assume you are selling from an existing long.
            realized = qty * (px - avg)
            self.realized_pnl += realized
    
            self.positions[sym] = new_pos
    
            # If position is fully closed, reset avg cost
            if new_pos == 0:
                self.avg_cost[sym] = 0.0
    
            self.cash += qty * px - comm

    def mark_to_market(self, symbol: str, price: float, timestamp):
        self.last_prices[symbol] = price
    
        unreal = 0.0
        mkt_value = 0.0
    
        for sym, qty in self.positions.items():
            px = self.last_prices.get(sym)
            if px is None:
                continue
    
            mkt_value += qty * px
    
            avg = self.avg_cost.get(sym, 0.0)
            unreal += qty * (px - avg)
    
        self.unrealized_pnl = unreal
        self.nav = self.cash + mkt_value
    
        self.history.append({
            "timestamp": timestamp,
            "symbol": symbol,
            "price": price,
            "cash": self.cash,
            "positions": dict(self.positions),
            "avg_cost": dict(self.avg_cost),
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "nav": self.nav,
            "total_commission": self.total_commission
        })



    def equity_curve(self):
        """
        Return list of (timestamp, nav).
        """
        return [(h["timestamp"], h["nav"]) for h in self.history]

    def snapshot(self):
        return {
            "cash": round(self.cash, 2),
            "positions": dict(self.positions),
            "avg_cost": {k: round(v, 2) for k, v in self.avg_cost.items()},
            "last_prices": {k: round(v, 2) for k, v in self.last_prices.items()},
            "unrealized_pnl": round(self.unrealized_pnl, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "nav": round(self.nav, 2),
            "total_commission": round(self.total_commission, 2),
        }


