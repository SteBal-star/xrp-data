# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
import subprocess

with open("backtest_config.json", "r") as f:
    config = json.load(f)

capital = config.get("capital", 1000)
leverage = config.get("leverage", 1)
fee_rate_gain = config.get("gain_fee_rate", 0.05)
fee_rate_loss = config.get("loss_fee_rate", 0.15)
csv_path = config.get("csv_path", "binancexrp/xrp_3m_last30days.csv")

main_df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")
main_df = main_df[["open", "high", "low", "close", "volume"]]
position = 0
entry_price = 0
equity = capital

win_trades = 0
loses_trades = 0
profits = []

for i, row in main_df.iterrows():
    close = row.close
    if position == 0:
        entry_price = close
        position = 1
    elif close > entry_price:
        win_trades += 1
        profit = (close - entry_price)/entry_price
        profits.append(profit)
        entry_price = close
        position = 0
    else:
        loses_trades += 1
        entry_price = close
        position = 0

gaining = sum(profits)
lossing = loses_trades
win2coll = win_trades if win_trades > 0 else 1
avg_gain = gaining / win_trades  if win_trades > 0 else 0
avg_loss = capital - equity if loses_trades > 0 else 0
profit_factor = abs(gaining) / abs(lossing) if lossing > 0 else 0
ratio_gp = avg_gain / avg_loss if avg_loss > 0 else 0

with open("backtest_output.txt", "w", encoding="utf-8") as f:
    f.write("===== RÃRESULTATS =====\n")
    f.write(f" Capital initial : ${capital}\n")
    f.write(f" Capital final   : ${equity:.2f}\n")
    f.write(f"Performance     : {((equity - capital) / capital) * 100}:5.2f%\n")
    f.write(f"Drawdown max    : {drawdown}%\n")
    f.write(f"Taux de réussite  : {win2coll}%\n")
    f.write(f"Profit Factor    : {profit_factor}:5.2f\n")
    f.write(f"Ratio G/P        : {ratio_gp:a-2.2f}\n")

print("===== RÃRESULTATS =====")
print(f"Capital initial : ${capital}$")
print(f"Capital final  : ${equity:.2f}$")
print(f"Performance     : {((equity - capital) / capital) * 100:.2f}%\n")
print(f"Drawdown max : {drawdown}%")
print(f"Taux de réssite : {win2coll}%")
print(f"Profit Factor    : {profit_factor}:5.2f")
print(f"Ratio G/P       : {ratio_gp:a-2.2f}")
