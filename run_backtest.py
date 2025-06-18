import os
import json
import pandas as pd

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

# Filtrer les N derniers jours
start_time = main_df.index[-1] - pd.Timedelta(days=period_days)
main_df = main_df[main_df.index >= start_time]

position = 0
entry_price = 0
equity = capital

win_trades = 0
losses_trades = 0
profits = []
capital_history = [capital]

for i, row in main_df.iterrows():
    close = row.close
    if position == 0:
        entry_price = close
        position = 1
    elif close > entry_price:
        win_trades += 1
        profit = (close - entry_price) / entry_price
        equity *= (1 + profit * (1 - fee_rate_gain))
        profits.append(profit)
        position = 0
    else:
        losses_trades += 1
        loss = (entry_price - close) / entry_price
        equity *= (1 - loss * (1 + fee_rate_loss))
        position = 0
    capital_history.append(equity)

gaining = sum(profits)
losing = losses_trades
nb_trades = win_trades + losses_trades
win_rate = (win_trades / nb_trades) * 100 if nb_trades > 0 else 0
avg_gain = gaining / win_trades if win_trades > 0 else 0
avg_loss = capital - equity if losses_trades > 0 else 0
profit_factor = abs(gaining) / abs(losses_trades) if losses_trades > 0 else 0
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

# Enregistre l'évolution du capital
pd.DataFrame({"capital": capital_history}).to_csv("capital_history.csv", index=False)

print("======= RÉSULTATS =======")
print(f"Capital initial       : {capital}$")
print(f"Capital final         : {equity:.2f}$")
print(f"Performance           : {performance:.2f}%")
print(f"Drawdown max          : {drawdown:.2f}%")
print(f"Taux de réussite       : {win_rate:.2f}%")
print(f"Profit Factor         : {profit_factor:.2f}")
print(f"Ratio G/P             : {ratio_gp:.2f}")
print(f"Nombre de trades      : {nb_trades}")
