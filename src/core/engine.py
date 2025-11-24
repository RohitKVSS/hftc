# src/core/engine.py

from queue import Queue, Empty
from datetime import datetime
from src.core.events import MarketEvent
from src.strategies.dummy_strategy import DummyStrategy


class SimpleEngine:
    """
    A minimal event-driven engine:
    - Takes MarketEvents in a queue
    - Routes them to a strategy
    - If strategy generates SignalEvent, prints it
    """

    def __init__(self, strategy):
        self.events = Queue()
        self.strategy = strategy
        self.running = False

    def put_market_event(self, symbol, bid, ask, last=None, volume=None):
        me = MarketEvent(
            symbol=symbol,
            timestamp=datetime.utcnow(),
            bid=bid,
            ask=ask,
            last=last,
            volume=volume
        )
        self.events.put(me)

    def run(self, max_events: int = 100):
        self.running = True
        processed = 0

        while self.running and processed < max_events:
            try:
                event = self.events.get(timeout=1)
            except Empty:
                continue

            processed += 1

            if event.type == "MARKET":
                signal = self.strategy.on_market_event(event)

                if signal is not None:
                    print(f"[SIGNAL] {signal.timestamp} {signal.symbol} {signal.signal_type} strength={signal.strength}")

        print("Engine stopped.")
