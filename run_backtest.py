import os
import json
import pandas as pd

# Charger les paramètres du backtest
with open("backtest_config.json", "r") as f:
    config = json.load(f)

capital = config.get("capital", 1000)
leverage = config.get("leverage", 1)
fee_rate = config.get("fee_rate", 0.001)
buy_kdj_j_threshold = config.get("buy_kdj_j_threshold", 30)
sell_kdj_j_drop = config.get("sell_kdj_j_drop", True)
csv_path = config.get("csv_path", "binancexrp/xrp_1m_last30days.csv")

# Charger les données CSV
df = pd.read_csv(csv_path, parse_dates=["timestamp"], index_col="timestamp")

# Simuler une stratégie simple
position = 0  # 0 = pas en position, 1 = en position
entry_price = 0
equity = capital

for i in range(1, len(df)):
    j_now = df['J'].iloc[i]
    j_prev = df['J'].iloc[i - 1]
    close = df['close'].iloc[i]

    # Entrée : J < seuil et monte
    if position == 0 and j_now > j_prev and j_now < buy_kdj_j_threshold:
        position = 1
        entry_price = close

    # Sortie : J baisse
    elif position == 1 and j_now < j_prev:
        pct = ((close - entry_price) / entry_price) * leverage
        fees = abs(pct) * fee_rate
        equity *= (1 + pct - fees)
        position = 0

# Si position ouverte à la fin
if position == 1:
    pct = ((df['close'].iloc[-1] - entry_price) / entry_price) * leverage
    fees = abs(pct) * fee_rate
    equity *= (1 + pct - fees)

# Résultat final
print(f"📈 Capital initial : {capital}$")
print(f"🏁 Capital final   : {equity:.2f}$")
print(f"💹 Performance     : {((equity - capital) / capital) * 100:.2f}%")
