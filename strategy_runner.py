import pandas as pd
import talib
import yaml
from datetime import timedelta

# === Charger la stratégie YAML ===
with open("strategy.yaml", "r") as f:
    strategy = yaml.safe_load(f)

capital = strategy.get("capital", 1000)
equity = capital
leverage = strategy.get("leverage", 1)
fee_gain = strategy.get("fees", {}).get("gain", 0.05)
fee_loss = strategy.get("fees", {}).get("loss", 0.15)
entry = strategy["entry"]
exit_ = strategy["exit"]
duration_limit = strategy.get("max_duration", None)

timeframe = entry["timeframe"]
csv_path = f"binancexrp/xrp_{timeframe}_last30days.csv"
main_df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")

# === Ajouter les indicateurs nécessaires ===
if entry["indicator"] == "macd" or exit_["indicator"] == "macd":
    main_df["MACD_DIF"], main_df["MACD_DEA"], _ = talib.MACD(main_df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
if entry.get("indicator") == "rsi" or exit_.get("indicator") == "rsi":
    main_df["RSI"] = talib.RSI(main_df["close"], timeperiod=14)
if entry.get("indicator") == "ema" or exit_.get("indicator") == "ema":
    main_df["EMA"] = talib.EMA(main_df["close"], timeperiod=14)
if entry.get("indicator") == "kdj" or exit_.get("indicator") == "kdj":
    low_min = main_df['low'].rolling(window=9).min()
    high_max = main_df['high'].rolling(window=9).max()
    rsv = (main_df['close'] - low_min) / (high_max - low_min) * 100
    main_df['K'] = rsv.ewm(com=2).mean()
    main_df['D'] = main_df['K'].ewm(com=2).mean()
    main_df['J'] = 3 * main_df['K'] - 2 * main_df['D']

# === Initialisation ===
position = 0
entry_price = 0
entry_time = None
trade_log = []

# === Boucle de trading ===
for i in range(1, len(main_df)):
    row_prev = main_df.iloc[i-1]
    row = main_df.iloc[i]

    cross_above = row["MACD_DIF"] > row["MACD_DEA"] and row_prev["MACD_DIF"] <= row_prev["MACD_DEA"]
    cross_below = row["MACD_DIF"] < row["MACD_DEA"] and row_prev["MACD_DIF"] >= row_prev["MACD_DEA"]

    if position == 0:
        if entry["indicator"] == "macd" and entry["condition"] == "cross_above" and row["MACD_DIF"] < 0 and cross_above:
            entry_price = row["close"]
            entry_time = row.name
            position = 1
    else:
        timed_out = duration_limit and (row.name - entry_time) > timedelta(minutes=duration_limit)
        if (exit_["indicator"] == "macd" and exit_["condition"] == "cross_below" and cross_below) or timed_out:
            exit_price = row["close"]
            pnl = (exit_price - entry_price) * leverage
            fee = pnl * fee_gain if pnl > 0 else abs(pnl) * fee_loss
            net_pnl = pnl - fee if pnl > 0 else pnl - fee
            equity += net_pnl

            trade_log.append({
                "timestamp": row.name,
                "entry_price": round(entry_price, 4),
                "exit_price": round(exit_price, 4),
                "pnl": round(net_pnl, 2),
                "fee": round(fee, 2),
                "capital": round(equity, 2),
                "duration": str(row.name - entry_time)
            })
            position = 0

# === Sauvegarde ===
pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)
print("✅ Backtest terminé. Trade log sauvegardé.")
