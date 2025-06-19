import os
import json
import pandas as pd
from datetime import timedelta

with open("backtest_config.json", "r") as f:
    config = json.load(f)

capital = config.get("capital", 1000)
leverage = config.get("leverage", 1)
fee_rate_gain = config.get("gain_fee_rate", 0.05)
fee_rate_loss = config.get("loss_fee_rate", 0.15)
csv_path = config.get("csv_path", "binancexrp/xrp_3m_last30days.csv")
period_days = config.get("period_days", 30)

main_df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")
main_df = main_df[["open", "high", "low", "close", "volume"]]

start_time = main_df.index[-1] - timedelta(days=period_days)
main_df = main_df[main_df.index >= start_time]

position = 0
entry_price = 0
entry_time = None
equity = capital

win_trades = 0
losses_trades = 0
profits = []
trade_log = []

for i, row in main_df.iterrows():
    close = row.close
    timestamp = i

    if position == 0:
        entry_price = close
        entry_time = timestamp
        position = 1
    else:
        if close > entry_price:
            win_trades += 1
            raw_profit = (close - entry_price) * leverage
            fee = raw_profit * fee_rate_gain
            net_profit = raw_profit - fee
            equity += net_profit
            profits.append(net_profit)
        else:
            losses_trades += 1
            raw_loss = (entry_price - close) * leverage
            fee = raw_loss * fee_rate_loss
            net_loss = raw_loss + fee
            equity -= net_loss
            profits.append(-net_loss)

        trade_log.append({
            "timestamp": timestamp,
            "entry_price": round(entry_price, 4),
            "exit_price": round(close, 4),
            "pnl": round(net_profit if close > entry_price else -net_loss, 2),
            "fee": round(fee, 2),
            "capital": round(equity, 2)
        })

        entry_price = close
        entry_time = timestamp
        position = 0

capital_history = [capital] + [trade["capital"] for trade in trade_log]
pd.Series(capital_history).to_csv("capital_history.csv", index=False, header=["capital"])
pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)

gaining = sum([p for p in profits if p > 0])
losing = -sum([p for p in profits if p < 0])
nb_trades = len(trade_log)
win_rate = (win_trades / nb_trades) * 100 if nb_trades > 0 else 0
avg_gain = gaining / win_trades if win_trades > 0 else 0
avg_loss = losing / losses_trades if losses_trades > 0 else 0
profit_factor = abs(gaining) / abs(losing) if losing > 0 else 0
ratio_gp = avg_gain / avg_loss if avg_loss > 0 else 0
drawdown = max(0, 100 * (capital - equity) / capital) if capital > equity else 0
performance = ((equity - capital) / capital) * 100

with open("backtest_output.txt", "w", encoding="utf-8") as f:
    f.write("======= RÉSULTATS =======\n")
    f.write(f"Capital initial       : {capital}\n")
    f.write(f"Capital final         : {equity:.2f}\n")
    f.write(f"Performance           : {performance:.2f}%\n")
    f.write(f"Drawdown max          : {drawdown:.2f}%\n")
    f.write(f"Taux de réussite       : {win_rate:.2f}%\n")
    f.write(f"Profit Factor         : {profit_factor:.2f}\n")
    f.write(f"Ratio G/P             : {ratio_gp:.2f}\n")
    f.write(f"Nombre de trades      : {nb_trades}\n")

print("======= RÉSULTATS =======")
print(f"Capital initial       : {capital}$")
print(f"Capital final         : {equity:.2f}$")
print(f"Performance           : {performance:.2f}%")
print(f"Drawdown max          : {drawdown:.2f}%")
print(f"Taux de réussite       : {win_rate:.2f}%")
print(f"Profit Factor         : {profit_factor:.2f}")
print(f"Ratio G/P             : {ratio_gp:.2f}")
print(f"Nombre de trades      : {nb_trades}")
