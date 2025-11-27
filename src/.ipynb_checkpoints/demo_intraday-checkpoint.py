# src/demo_intraday.py
from src.core.engine import SimpleEngine
from src.data.data_handler import CSVDataHandler
from src.portfolio.portfolio import Portfolio
from src.execution.execution_sim import ExecutionSimulator
from src.strategies.dummy_strat import DummyStrategy  # SMA/EMA crossover

MAX_BARS = 2000  # limit intraday backtest length

if __name__ == "__main__":
    print("Hello from intraday demo")
    print("Starting 1-minute backtest...")

    portfolio = Portfolio(base_quantity=10, initial_capital=1_000_000)
    execution = ExecutionSimulator(commission_per_share=0.01)

    strategy = DummyStrategy(
        portfolio=portfolio,
        sma_window=20,
        ema_period=10,
    )

    engine = SimpleEngine(strategy, portfolio, execution)
    MAX_BARS = 2000

    dh = CSVDataHandler("data/raw/intraday_1m/intraday_multi_1m.csv")

    engine.run_from_datahandler(dh, max_rows=MAX_BARS)

    curve = portfolio.equity_curve()

    print("\nLast NAV points:")
    for t, nav in curve[-3:]:
        print(f"  {t} {nav:.2f}")

    print("\nFinal snapshot:")
    print(portfolio.snapshot())
