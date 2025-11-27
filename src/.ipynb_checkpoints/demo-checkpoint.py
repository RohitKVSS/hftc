from src.core.engine import SimpleEngine
from src.core.data_handler import CSVDataHandler
from src.strategies.dummy_strat import DummyStrategy
from src.portfolio.portfolio import Portfolio
from src.execution.execution_sim import ExecutionSimulator


if __name__ == "__main__":
    print("Hello from demo")
    print("Starting HFTC demo...")

    # 1) Set up components
    strategy = DummyStrategy(threshold=100)
    portfolio = Portfolio(base_quantity=10, initial_capital=1_000_000)
    execution = ExecutionSimulator(commission_per_share=0.01)

    engine = SimpleEngine(strategy, portfolio, execution)

    # 2) Load CSV data
    dh = CSVDataHandler("data/raw/demo_intraday.csv")

    # 3) Run engine row-by-row on data (quietly)
    engine.run_from_datahandler(dh)

    # 4) Print results
    curve = portfolio.equity_curve()

    print("\nLast NAV points:")
    for t, nav in curve[-3:]:
        print(" ", t, nav)

    print("\nFinal snapshot:")
    print(portfolio.snapshot())
