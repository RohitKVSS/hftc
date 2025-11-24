# src/core/engine.py

from queue import Queue, Empty
from datetime import datetime

from src.core.events import MarketEvent
from src.strategies.dummy_strat import DummyStrategy
from src.portfolio.portfolio import Portfolio


class SimpleEngine:
    """
    Event-driven engine:
    MARKET -> Strategy -> SIGNAL -> Portfolio -> ORDER -> print/log
    """

    def __init__(self, strategy, portfolio):
        self.events = Queue()
        self.strategy = strategy
        self.portfolio = portfolio
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

            # 1) MARKET -> Strategy
            if event.type == "MARKET":
                signal = self.strategy.on_market_event(event)
                if signal is not None:
                    self.events.put(signal)

            # 2) SIGNAL -> Portfolio -> ORDER
            elif event.type == "SIGNAL":
                order = self.portfolio.on_signal(event)
                if order is not None:
                    self.events.put(order)

                print(
                    f"[SIGNAL] {event.timestamp} {event.symbol} "
                    f"{event.signal_type} strength={event.strength}"
                )

            # 3) ORDER -> log only (execution next step)
            elif event.type == "ORDER":
                print(
                    f"[ORDER]  {event.timestamp} {event.symbol} "
                    f"{event.direction} qty={event.quantity} type={event.order_type}"
                )

        print("Engine stopped.")
