from datetime import datetime, timezone
from freqtrade.strategy import IStrategy
from pandas import DataFrame


class Blink5s(IStrategy):
    timeframe = "1m"
    process_only_new_candles = False  # allow loop checks every throttle tick

    # Disable ROI/stoploss exits - we control exit via custom_exit
    minimal_roi = {"0": 1000}
    stoploss = -0.99
    trailing_stop = False

    startup_candle_count = 1

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Always signal entry (freqtrade will still respect max_open_trades etc.)
        dataframe.loc[:, "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # exits handled in custom_exit
        dataframe.loc[:, "exit_long"] = 0
        return dataframe

    def custom_exit(self, pair: str, trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
        # Sell 5 seconds after entry
        now = current_time
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        opened = trade.open_date_utc
        if opened.tzinfo is None:
            opened = opened.replace(tzinfo=timezone.utc)

        age_s = (now - opened).total_seconds()
        if age_s >= 5:
            return "blink_5s"

        return None
