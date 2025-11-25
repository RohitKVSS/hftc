# src/core/engine.py

from queue import Queue, Empty
from datetime import datetime

from src.core.events import MarketEvent
from src.strategies.dummy_strat import DummyStrategy
from src.portfolio.portfolio import Portfolio
from src.execution.execution_sim import ExecutionSimulator


class SimpleEngine:
    """
    Event-driven engine:
    MARKET -> Strategy -> SIGNAL -> Portfolio -> ORDER -> Execution -> FILL -> Portfolio update
    """

    def __init__(self, strategy, portfolio, execution):
        self.events = Queue()
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution = execution

        self.running = False
        self.market_state = {}  # symbol -> {"bid":..., "ask":..., "last":...}

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

    def _get_fill_price(self, symbol: str):
        """
        For now, fill market orders at mid price if bid/ask exist,
        else fall back to last.
        """
        s = self.market_state.get(symbol)
        if s is None:
            return None

        bid, ask, last = s.get("bid"), s.get("ask"), s.get("last")

        if bid is not None and ask is not None:
            return (bid + ask) / 2.0
        return last

    def run(self, max_events: int = 100, max_idle_timeouts: int = 3):
        self.running = True
        processed = 0
        idle_timeouts = 0
    
        while self.running and processed < max_events:
            try:
                event = self.events.get(timeout=1)
                idle_timeouts = 0  # reset because we got something
            except Empty:
                idle_timeouts += 1
                if idle_timeouts >= max_idle_timeouts:
                    print("No new events. Stopping engine.")
                    break
                continue
    
            processed += 1
    
            if event.type == "MARKET":
                self.market_state[event.symbol] = {
                    "bid": event.bid,
                    "ask": event.ask,
                    "last": event.last
                }
            
                # NEW: mark-to-market on every tick/bar
                mid_px = (event.bid + event.ask) / 2.0 if event.bid and event.ask else event.last
                if mid_px is not None:
                    self.portfolio.mark_to_market(event.symbol, mid_px)
            
                signal = self.strategy.on_market_event(event)
                if signal is not None:
                    self.events.put(signal)

    
            elif event.type == "SIGNAL":
                order = self.portfolio.on_signal(event)
                if order is not None:
                    self.events.put(order)
    
                print(
                    f"[SIGNAL] {event.timestamp} {event.symbol} "
                    f"{event.signal_type} strength={event.strength}"
                )
    
            elif event.type == "ORDER":
                fill_px = self._get_fill_price(event.symbol)
                if fill_px is None:
                    continue
    
                fill = self.execution.on_order(event, fill_px)
                self.events.put(fill)
    
                print(
                    f"[ORDER]  {event.timestamp} {event.symbol} "
                    f"{event.direction} qty={event.quantity} type={event.order_type} "
                    f"fill_px~{fill_px:.2f}"
                )
    
            elif event.type == "FILL":
                self.portfolio.on_fill(event)
    
                print(
                    f"[FILL]   {event.timestamp} {event.symbol} "
                    f"{event.direction} qty={event.quantity} px={event.fill_price:.2f} "
                    f"comm={event.commission:.2f}"
                )
    
        print("Engine stopped.")
        print("Portfolio snapshot:", self.portfolio.snapshot())
