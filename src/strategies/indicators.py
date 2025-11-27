from collections import deque


class RollingSMA:
    """
    Streaming Simple Moving Average.
    """
    def __init__(self, window: int):
        if window <= 0:
            raise ValueError("window must be > 0")
        self.window = window
        self.values = deque(maxlen=window)
        self._sum = 0.0

    def update(self, x: float):
        """
        Add new value x. Returns SMA or None if window not full.
        """
        if len(self.values) == self.window:
            self._sum -= self.values[0]

        self.values.append(x)
        self._sum += x

        if len(self.values) < self.window:
            return None

        return self._sum / self.window

    @property
    def value(self):
        if len(self.values) < self.window:
            return None
        return self._sum / self.window


class EMA:
    """
    Streaming Exponential Moving Average.
    """
    def __init__(self, period: int):
        if period <= 0:
            raise ValueError("period must be > 0")
        self.period = period
        self.alpha = 2.0 / (period + 1.0)
        self._value = None

    def update(self, x: float):
        if self._value is None:
            self._value = x
        else:
            self._value = self.alpha * x + (1 - self.alpha) * self._value
        return self._value

    @property
    def value(self):
        return self._value
