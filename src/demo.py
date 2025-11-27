from src.core.engine import SimpleEngine
from src.core.data_handler import CSVDataHandler
from src.strategies.dummy_strat import DummyStrategy
from src.portfolio.portfolio import Portfolio
from src.execution.execution_sim import ExecutionSimulator


if __name__ == "__main__":
    print("Hello from demo")
    print("Starting HFTC demo...")
    portfolio = Portfolio(base_quantity=10, initial_capital=1_000_000)
    execution = ExecutionSimulator(commission_per_share=0.01)
    strategy = DummyStrategy(
        portfolio=portfolio,
        sma_window=20,
        ema_period=10,
    )
    
   

    engine = SimpleEngine(strategy, portfolio, execution)

    # dh = CSVDataHandler("data/raw/demo_intraday_multi.csv")
    dh = CSVDataHandler("data/raw/intraday_multi.csv")
    
    engine.run_from_datahandler(dh)

    curve = portfolio.equity_curve()

    print("\nLast NAV points:")
    for t, nav in curve[-3:]:
        print(f"  {t} {nav:.2f}")

    print("\nFinal snapshot:")
    print(portfolio.snapshot())
