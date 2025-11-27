# src/core/data_handler.py

import pandas as pd
from datetime import datetime
from typing import Iterator, Dict, Any, Optional


class CSVDataHandler:
    """
    Minimal CSV DataHandler:
    - Loads intraday data from CSV
    - Yields dicts containing symbol, bid, ask, last, timestamp

    Expected CSV columns (minimum):
      timestamp, symbol, last
    Optional:
      bid, ask, volume

    timestamp can be:
      - ISO string like "2025-11-25 09:30:00"
      - or epoch int/float
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data = self._load_csv()
        self._iter = self._row_iterator()

    def _load_csv(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path)

        # Basic sanity checks
        required = {"timestamp", "symbol", "last"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"CSV missing required columns: {missing}")

        # Sort by time (important for intraday)
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def _parse_ts(self, ts_val) -> datetime:
        # If numeric, treat as epoch seconds
        if isinstance(ts_val, (int, float)):
            return datetime.fromtimestamp(ts_val)
        # Else parse string
        return pd.to_datetime(ts_val).to_pydatetime()

    def _row_iterator(self) -> Iterator[Dict[str, Any]]:
        for _, row in self.data.iterrows():
            ts = self._parse_ts(row["timestamp"])
            sym = row["symbol"]

            last = float(row["last"])
            bid = float(row["bid"]) if "bid" in row and pd.notna(row["bid"]) else last
            ask = float(row["ask"]) if "ask" in row and pd.notna(row["ask"]) else last
            vol = int(row["volume"]) if "volume" in row and pd.notna(row["volume"]) else None

            yield {
                "timestamp": ts,
                "symbol": sym,
                "bid": bid,
                "ask": ask,
                "last": last,
                "volume": vol
            }

    def stream_next(self) -> Optional[Dict[str, Any]]:
        """
        Returns next market row dict, or None if data exhausted.
        """
        try:
            return next(self._iter)
        except StopIteration:
            return None
