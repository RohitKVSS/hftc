# src/run_demo.py

from src.core.engine import SimpleEngine
from src.core.data_handler import CSVDataHandler
from src.strategies.dummy_strat import DummyStrategy
from src.portfolio.portfolio import Portfolio
from src.execution.execution_sim import ExecutionSimulator

if __name__ == "__main__":
    strategy = DummyStrategy(threshold=100)
    portfolio = Portfolio(base_quantity=10, initial_capital=1_000_000)
    execution = ExecutionSimulator(commission_per_share=0.01)

    engine = SimpleEngine(strategy, portfolio, execution)

    dh = CSVDataHandler("data/raw/demo_intraday.csv")

    engine.run_from_datahandler(dh)

    # show last few NAV points
    curve = portfolio.equity_curve()
    print("Last NAV points:", curve[-3:])
    print("Final snapshot:", portfolio.snapshot())
