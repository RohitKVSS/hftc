# src/core/events.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class Event:
    """
    Base class for all events.
    Every event has a 'type' so the event loop can route it.
    """
    type: str


@dataclass
class MarketEvent(Event):
    """
    Represents new market data (tick / quote / bar).
    """
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    last: Optional[float] = None
    volume: Optional[int] = None

    def __post_init__(self):
        self.type = "MARKET"


@dataclass
class SignalEvent(Event):
    """
    Strategy-generated signal.
    Example: BUY/SELL with optional strength.
    """
    symbol: str
    timestamp: datetime
    signal_type: str  # "BUY" or "SELL" or "EXIT"
    strength: float = 1.0  # confidence / size multiplier

    def __post_init__(self):
        self.type = "SIGNAL"


@dataclass
class OrderEvent(Event):
    """
    Order sent to execution layer.
    """
    symbol: str
    timestamp: datetime
    order_type: str   # "MKT" or "LMT"
    direction: str    # "BUY" or "SELL"
    quantity: int
    price: Optional[float] = None  # needed for limit orders

    def __post_init__(self):
        self.type = "ORDER"


@dataclass
class FillEvent(Event):
    """
    Fill returned from execution layer.
    Includes fees, price, quantity, etc.
    """
    symbol: str
    timestamp: datetime
    direction: str
    quantity: int
    fill_price: float
    commission: float = 0.0

    def __post_init__(self):
        self.type = "FILL"
