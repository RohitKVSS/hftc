# src/execution/execution_sim.py

from datetime import datetime
from src.core.events import OrderEvent, FillEvent


class ExecutionSimulator:
    """
    Minimal execution simulator:
    - Takes OrderEvent
    - Fills immediately at a given price
    - Returns FillEvent

    Later we will add:
    - partial fills
    - slippage
    - queue position
    - maker/taker fees
    """

    def __init__(self, commission_per_share: float = 0.0):
        self.commission_per_share = commission_per_share

    def on_order(self, order: OrderEvent, fill_price: float):
        """
        Convert an OrderEvent into a FillEvent at fill_price.
        """
        commission = self.commission_per_share * order.quantity

        fill = FillEvent(
            symbol=order.symbol,
            timestamp=datetime.utcnow(),
            direction=order.direction,
            quantity=order.quantity,
            fill_price=fill_price,
            commission=commission
        )
        return fill
