# src/core/engine.py

from queue import Queue, Empty
from datetime import datetime

from src.core.events import MarketEvent


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

    # -----------------------
    # Inject market events
    # -----------------------
    def put_market_event(self, symbol, bid, ask, last=None, volume=None, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()

        me = MarketEvent(
            symbol=symbol,
            timestamp=timestamp,
            bid=bid,
            ask=ask,
            last=last,
            volume=volume
        )
        self.events.put(me)

    # -----------------------
    # Helper: decide fill price
    # -----------------------
    def _get_fill_price(self, order_event):
        """
        Realistic market-order fill:
          - BUY at ask
          - SELL at bid
        Falls back to last if bid/ask missing.
        """
        symbol = order_event.symbol
        side = getattr(order_event, "direction", None)
    
        s = self.market_state.get(symbol)
        if s is None:
            return None
    
        bid, ask, last = s.get("bid"), s.get("ask"), s.get("last")
    
        # If we have a proper book:
        if bid is not None and ask is not None:
            if side == "BUY":
                return ask
            elif side == "SELL":
                return bid
            # Fallback: unknown side -> mid
            return (bid + ask) / 2.0
    
        # If only last is known:
        return last

    # -----------------------
    # Main event loop
    # -----------------------
    def run(self, max_events: int = 100, max_idle_timeouts: int = 3, print_summary: bool = True):
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
                    if print_summary:
                        print("No new events. Stopping engine.")
                    break
                continue

            processed += 1

            # 1) MARKET
            if event.type == "MARKET":
                self.market_state[event.symbol] = {
                    "bid": event.bid,
                    "ask": event.ask,
                    "last": event.last
                }

                # mark-to-market using this market event's timestamp
                mid_px = (event.bid + event.ask) / 2.0 if event.bid and event.ask else event.last
                if mid_px is not None:
                    self.portfolio.mark_to_market(event.symbol, mid_px, event.timestamp)

                # strategy reacts
                signal = self.strategy.on_market_event(event)
                if signal is not None:
                    self.events.put(signal)

            # 2) SIGNAL -> ORDER
            elif event.type == "SIGNAL":
                order = self.portfolio.on_signal(event)
                if order is not None:
                    self.events.put(order)

                print(
                    f"[SIGNAL] {event.timestamp} {event.symbol} "
                    f"{event.signal_type} strength={event.strength}"
                )

            # 3) ORDER -> FILL
            elif event.type == "ORDER":
                fill_px = self._get_fill_price(event)
                if fill_px is None:
                    continue
            
                fill = self.execution.on_order(event, fill_px)
                self.events.put(fill)
            
                print(
                    f"[ORDER]  {event.timestamp} {event.symbol} "
                    f"{event.direction} qty={event.quantity} type={event.order_type} "
                    f"fill_px~{fill_px:.2f}"
                )


            # 4) FILL -> portfolio update
            elif event.type == "FILL":
                self.portfolio.on_fill(event)

                print(
                    f"[FILL]   {event.timestamp} {event.symbol} "
                    f"{event.direction} qty={event.quantity} px={event.fill_price:.2f} "
                    f"comm={event.commission:.2f}"
                )

        if print_summary:
            print("Engine stopped.")
            print("Portfolio snapshot:", self.portfolio.snapshot())

    # -----------------------
    # DataHandler-driven run
    # -----------------------
    def run_from_datahandler(self, datahandler, max_rows: int = None):
        """
        Stream data row-by-row:
        For each CSV row:
          - create a MarketEvent
          - run the engine just enough to process resulting events
        """
        rows = 0

        while True:
            row = datahandler.stream_next()
            if row is None:
                break

            # Put one MarketEvent for this row
            self.put_market_event(
                symbol=row["symbol"],
                bid=row["bid"],
                ask=row["ask"],
                last=row["last"],
                volume=row["volume"],
                timestamp=row["timestamp"]
            )

            # Process all events generated from this MarketEvent
            self.run(max_events=1000, max_idle_timeouts=1, print_summary=False)

            rows += 1
            if max_rows is not None and rows >= max_rows:
                break
