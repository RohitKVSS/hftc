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
        self.realized_pnl = 0.0
        self.total_commission = 0.0

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
        Update positions and cash after a fill.
        """
        sym = fill.symbol
        qty = fill.quantity
        px = fill.fill_price
        comm = fill.commission

        self.total_commission += comm

        # Current position (default 0)
        pos = self.positions.get(sym, 0)

        if fill.direction == "BUY":
            pos += qty
            self.cash -= qty * px + comm
        elif fill.direction == "SELL":
            pos -= qty
            self.cash += qty * px - comm

        self.positions[sym] = pos

    def snapshot(self):
        """
        Small helper to view current portfolio state.
        """
        return {
            "cash": self.cash,
            "positions": dict(self.positions),
            "realized_pnl": self.realized_pnl,
            "total_commission": self.total_commission
        }
