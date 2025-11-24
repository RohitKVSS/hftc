# src/core/engine.py

from queue import Queue, Empty
from datetime import datetime

from src.core.events import MarketEvent, SignalEvent, OrderEvent
from src.strategies.dummy_strat import DummyStrategy  # <-- your filename


class SimpleEngine:
    """
    Minimal event-driven engine:
    MARKET -> Strategy -> SIGNAL -> Engine -> ORDER -> print/log
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

    def _signal_to_order(self, signal: SignalEvent) -> OrderEvent:
        """
        Temporary conversion logic (engine-level for now).
        Later this moves into Portfolio class.
        """
        direction = signal.signal_type  # "BUY" or "SELL"
        qty = int(10 * signal.strength)  # naive sizing for demo

        return OrderEvent(
            symbol=signal.symbol,
            timestamp=datetime.utcnow(),
            order_type="MKT",
            direction=direction,
            quantity=qty
        )

    def run(self, max_events: int = 100):
        self.running = True
        processed = 0

        while self.running and processed < max_events:
            try:
                event = self.events.get(timeout=1)
            except Empty:
                continue

            processed += 1

            # 1) MARKET events go to strategy
            if event.type == "MARKET":
                signal = self.strategy.on_market_event(event)

                if signal is not None:
                    # push SIGNAL back into queue
                    self.events.put(signal)

            # 2) SIGNAL events become ORDER events
            elif event.type == "SIGNAL":
                order = self._signal_to_order(event)
                self.events.put(order)

                print(
                    f"[SIGNAL] {event.timestamp} {event.symbol} "
                    f"{event.signal_type} strength={event.strength}"
                )

            # 3) ORDER events are just logged for now
            elif event.type == "ORDER":
                print(
                    f"[ORDER]  {event.timestamp} {event.symbol} "
                    f"{event.direction} qty={event.quantity} type={event.order_type}"
                )

        print("Engine stopped.")
