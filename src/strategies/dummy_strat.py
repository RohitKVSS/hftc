from src.core.events import SignalEvent
from src.strategies.indicators import RollingSMA, EMA


class DummyStrategy:
    """
    SMA/EMA crossover strategy:

    - Maintains per-symbol SMA and EMA.
    - BUY when EMA > SMA and currently flat.
    - SELL when EMA < SMA and currently long.
    - Ignores signals until SMA is "warmed up" (enough data).
    """

    def __init__(
        self,
        portfolio,
        sma_window: int = 20,
        ema_period: int = 10,
    ):
        self.portfolio = portfolio

        # indicator settings
        self.sma_window = sma_window
        self.ema_period = ema_period

        # indicators per symbol
        self.sma = {}  # symbol -> RollingSMA
        self.ema = {}  # symbol -> EMA

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

        # --- update indicators ---
        sma_obj, ema_obj = self._get_indicators(symbol)
        sma_val = sma_obj.update(price)
        ema_val = ema_obj.update(price)

        # Need both indicators and a *full* SMA window before we trade
        if sma_val is None or ema_val is None:
            return None

        pos = self.portfolio.positions.get(symbol, 0)

        # ENTRY: flat -> long when fast EMA > slow SMA
        if pos == 0 and ema_val > sma_val:
            return SignalEvent(
                symbol=symbol,
                timestamp=event.timestamp,
                signal_type="BUY",
                strength=1.0,
            )

        # EXIT: long -> flat when fast EMA < slow SMA
        if pos > 0 and ema_val < sma_val:
            return SignalEvent(
                symbol=symbol,
                timestamp=event.timestamp,
                signal_type="SELL",
                strength=1.0,
            )

        return None
