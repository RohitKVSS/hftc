# src/strategies/dummy_strat.py

from src.core.events import SignalEvent
from src.strategies.indicators import RollingSMA, EMA


class DummyStrategy:
    """
    SMA/EMA crossover strategy with state:

    - Keeps per-symbol SMA and EMA.
    - BUY once when EMA crosses above SMA (FLAT -> LONG).
    - SELL once when EMA crosses below SMA (LONG -> FLAT).
    """

    def __init__(self, portfolio, sma_window: int = 20, ema_period: int = 10):
        self.portfolio = portfolio
        self.sma_window = sma_window
        self.ema_period = ema_period

        self.sma = {}           # symbol -> RollingSMA
        self.ema = {}           # symbol -> EMA
        self.state = {}         # symbol -> "FLAT" or "LONG"

    def _price(self, event):
        price = event.last
        if price is None and event.bid is not None and event.ask is not None:
            price = (event.bid + event.ask) / 2.0
        return price

    def _get_indicators(self, symbol):
        if symbol not in self.sma:
            self.sma[symbol] = RollingSMA(self.sma_window)
        if symbol not in self.ema:
            self.ema[symbol] = EMA(self.ema_period)
        return self.sma[symbol], self.ema[symbol]

    def on_market_event(self, event):
        symbol = event.symbol
        price = self._price(event)
        if price is None:
            return None

        sma_obj, ema_obj = self._get_indicators(symbol)
        sma_val = sma_obj.update(price)
        ema_val = ema_obj.update(price)

        # wait until SMA is fully "warmed up"
        if sma_val is None or ema_val is None:
            return None

        prev_state = self.state.get(symbol, "FLAT")
        pos = self.portfolio.positions.get(symbol, 0)

        # CROSS UP: FLAT -> LONG
        if ema_val > sma_val and prev_state != "LONG":
            self.state[symbol] = "LONG"

            if pos <= 0:  # only enter if not already long
                return SignalEvent(
                    symbol=symbol,
                    timestamp=event.timestamp,
                    signal_type="BUY",
                    strength=1.0,
                )

        # CROSS DOWN: LONG -> FLAT
        if ema_val < sma_val and prev_state != "FLAT":
            self.state[symbol] = "FLAT"

            if pos > 0:  # only exit if currently long
                return SignalEvent(
                    symbol=symbol,
                    timestamp=event.timestamp,
                    signal_type="SELL",
                    strength=1.0,
                )

        return None
