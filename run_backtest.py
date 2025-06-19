import pandas as pd
import pandas_ta as ta
from datetime import timedelta

# === CONFIGURATION MANUELLE POUR TEST LOCAL ===
capital = 1000
equity = capital
leverage = 1
fee_gain = 0.05
fee_loss = 0.15
period_days = 14
csv_path = "binancexrp/xrp_3m_last30days.csv"

# === CHARGEMENT DES DONNÉES ===
df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")
df = df[df.index >= df.index[-1] - timedelta(days=period_days)]

# === INDICATEURS ===
macd = ta.macd(df["close"])
kdj = ta.kdj(df["high"], df["low"], df["close"])
df = pd.concat([df, macd, kdj], axis=1)

# === STRAT SIMPLE : achat croisement MACD haussier en bas de 0, vente si J baisse ===
position = 0
entry_price = 0
entry_time = None
trades = []

for i in range(1, len(df)):
    row = df.iloc[i]
    prev = df.iloc[i - 1]

    cross_up = row["MACD_1"] > row["MACDs_1"] and prev["MACD_1"] <= prev["MACDs_1"]
    cross_down = row["MACD_1"] < row["MACDs_1"] and prev["MACD_1"] >= prev["MACDs_1"]
    j_decreasing = row["J_9_3"] < prev["J_9_3"]

    if position == 0 and cross_up and row["MACD_1"] < 0:
        entry_price = row["close"]
        entry_time = row.name
        position = 1

    elif position == 1 and j_decreasing:
        exit_price = row["close"]
        pnl = (exit_price - entry_price) * leverage
        fee = pnl * fee_gain if pnl > 0 else abs(pnl) * fee_loss
        net = pnl - fee if pnl > 0 else pnl - fee
        equity += net

        trades.append({
            "timestamp": row.name,
            "entry_price": round(entry_price, 4),
            "exit_price": round(exit_price, 4),
            "pnl": round(net, 2),
            "fee": round(fee, 2),
            "capital": round(equity, 2)
        })
        position = 0

# === EXPORT CSV ===
pd.DataFrame(trades).to_csv("trade_log.csv", index=False)
print("✅ Backtest terminé avec pandas_ta.")

