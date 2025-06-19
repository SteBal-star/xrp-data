import pandas as pd
import pandas_ta as ta
import yaml
from datetime import timedelta

with open("strategy.yaml", "r") as f:
    strategy = yaml.safe_load(f)

capital = strategy.get("capital", 1000)
equity = capital
leverage = strategy.get("leverage", 1)
fee_gain = strategy["fees"]["gain"]
fee_loss = strategy["fees"]["loss"]
entry = strategy["entry"]
exit_ = strategy["exit"]
duration_limit = strategy.get("max_duration", None)
period_days = strategy.get("period_days", 14)

timeframe = entry["timeframe"]
csv_path = f"binancexrp/xrp_{timeframe}_last30days.csv"
main_df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")
main_df = main_df[main_df.index >= main_df.index[-1] - timedelta(days=period_days)]

# Ajouter les indicateurs demandés
if "macd" in [entry["indicator"], exit_["indicator"]]:
    macd = ta.macd(main_df["close"])
    main_df = pd.concat([main_df, macd], axis=1)
if "kdj" in [entry["indicator"], exit_["indicator"]]:
    kdj = ta.kdj(main_df["high"], main_df["low"], main_df["close"])
    main_df = pd.concat([main_df, kdj], axis=1)

position = 0
entry_price = 0
entry_time = None
trade_log = []

for i in range(1, len(main_df)):
    row = main_df.iloc[i]
    prev = main_df.iloc[i - 1]

    cross_above = row["MACD_1"] > row["MACDs_1"] and prev["MACD_1"] <= prev["MACDs_1"]
    cross_below = row["MACD_1"] < row["MACDs_1"] and prev["MACD_1"] >= prev["MACDs_1"]
    j_decreasing = row["J_9_3"] < prev["J_9_3"]

    if position == 0 and cross_above and row["MACD_1"] < 0:
        entry_price = row["close"]
        entry_time = row.name
        position = 1

    elif position == 1 and (j_decreasing or (duration_limit and (row.name - entry_time > timedelta(minutes=duration_limit)))):
        exit_price = row["close"]
        pnl = (exit_price - entry_price) * leverage
        fee = pnl * fee_gain if pnl > 0 else abs(pnl) * fee_loss
        net = pnl - fee if pnl > 0 else pnl - fee
        equity += net

        trade_log.append({
            "timestamp": row.name,
            "entry_price": round(entry_price, 4),
            "exit_price": round(exit_price, 4),
            "pnl": round(net, 2),
            "fee": round(fee, 2),
            "capital": round(equity, 2),
            "duration": str(row.name - entry_time)
        })
        position = 0

# Sauvegarde
pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)
print("✅ Backtest terminé avec pandas_ta.")
