# src/strategies/dummy_strategy.py

from datetime import datetime
from src.core.events import SignalEvent, MarketEvent

class DummyStrategy:
    """
    Minimal strategy:
    - If last price is above a threshold, BUY
    - Otherwise do nothing
    """

    def __init__(self, threshold: float = 100.0):
        self.threshold = threshold

    def on_market_event(self, event: MarketEvent):
        """
        Called by the engine whenever a MarketEvent arrives.
        Returns a SignalEvent or None.
        """
        price = event.last if event.last is not None else (event.bid + event.ask) / 2.0

        if price > self.threshold:
            return SignalEvent(
                symbol=event.symbol,
                timestamp=datetime.utcnow(),
                signal_type="BUY",
                strength=1.0
            )

        return None
