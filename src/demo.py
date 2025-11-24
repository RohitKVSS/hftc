# src/run_demo.py

from src.core.engine import SimpleEngine
from src.strategies.dummy_strat import DummyStrategy

if __name__ == "__main__":
    strategy = DummyStrategy(threshold=100)
    engine = SimpleEngine(strategy)

    # Fake market events
    engine.put_market_event("AAPL", bid=99.5, ask=100.0, last=99.8)
    engine.put_market_event("AAPL", bid=100.2, ask=100.4, last=100.3)
    engine.put_market_event("AAPL", bid=101.0, ask=101.2, last=101.1)

    engine.run(max_events=10)
