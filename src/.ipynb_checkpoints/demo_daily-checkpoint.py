# src/demo_daily.py
from src.core.engine import SimpleEngine
from src.data.data_handler import CSVDataHandler
from src.portfolio.portfolio import Portfolio
from src.execution.execution_sim import ExecutionSimulator
from src.strategies.daily_trend import DailyTrendStrategy  # you'll create this later

MAX_BARS = 3000  # maybe allow more bars for daily data

if __name__ == "__main__":
    print("Hello from daily demo")
    print("Starting daily backtest...")

    portfolio = Portfolio(base_quantity=10, initial_capital=1_000_000)
    execution = ExecutionSimulator(commission_per_share=0.01)

    strategy = DailyTrendStrategy(
        portfolio=portfolio,
        # daily-specific params go here
    )

    engine = SimpleEngine(strategy, portfolio, execution)

    dh = CSVDataHandler("data/raw/daily_1d/daily_multi_1d.csv")

    engine.run_from_datahandler(dh, max_rows=MAX_BARS)

    curve = portfolio.equity_curve()

    print("\nLast NAV points:")
    for t, nav in curve[-3:]:
        print(f"  {t} {nav:.2f}")

    print("\nFinal snapshot:")
    print(portfolio.snapshot())
