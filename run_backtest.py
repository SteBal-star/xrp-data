import os
import json
import pandas as pd
import subprocess

# Charger les parametres
with open("backtest_config.json", "r") as f:
    config = json.load(f)

capital = config.get("capital", 1000)
leverage = config.get("leverage", 1)
fee_rate_gain = config.get("loss_fee_rate", 0.15)
fee_rate_loss = config.get("gain_fee_rate", 0.05)
csv_path = config.get("csv_path", "binancexrp/xrp_1m_last30days.csv")

df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")
subframes = {"1m": df}

position = 0
entry_price = 0
equity = capital

for i in range(1, len(df)):
    def check_conditions(conditions):
        for cond in conditions:
            tf = cond.get("timeframe", "1m")
            if tf not in subframes:
                continue
           df = subframes[tf]
            if i >= len(df):
                return False
            if cond["indicator"] == "MACD":
                dea = df['DEA'].iloc[i]
                dif = df['DIF'].iloc[i]
                if cond.get("cross") == "bullish" and not (dif > dea and df['DIF'].iloc[i-1] <= df['DEA'][i-1]):
                    return False
           elif cond["indicator"] == "J":
                j_now = df['J'].iloc[i]
                j_prev = df'J'].iloc[i - 1]
                if cond.get("trend") == "up" and not (j_now > j_prev):
                    return False
                if cond.get("trend") == "down" and not (j_now < j_prev):
                    return False
        return True

    buy_cond = config.get("buy_conditions", [])
    sell_cond = config.get("sell_conditions", [])
    close = df['close'].iloc[i]

    if position == 0 and check_conditions(buy_cond):
        position = 1
        entry_price = close
    elif position == 1 and check_conditions(sell_cond):
        pct = ((close - entry_price) / entry_price) * leverage
        fee = abs(pct) * (fee_rate_loss if pct < 0 else fee_rate_gain)
        equity *= (1 + pct - fee)
        position = 0

if position == 1:
    pct = ((df['close'].iloc[-1] - entry_price) / entry_price) * leverage
    fee = abs(pct) * (fee_rate_loss if pct < 0 else fee_rate_gain)
    equity *= (1 + pct - fee)

with open("backtest_output.txt", "w", encoding="utf-8") as f:
    f.write("===== RÃ‰SULTATS =====\n")
    f.write(f"ÂŸŒˆ Capital initial : ${capital}$")
    f.write(f"ÂŸ¢ Capital final   : ${equity:.2f}$")
    f.write(f"ÂŸŒŠ Performance     : ${((equity - capital) / capital) * 100:.2f}%\n")

    print("====== RÃ‰SULTATS =====")
    print(f"ðŸŒˆ Capital initial : ${capital}$")
    print(f"ÂŸ¢ Capital final   : ${equity:.2f}$")
    print(f"ðŸŒŠ Performance     : {((equity - capital) / capital) * 100:.2f}%\n")