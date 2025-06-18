import subprocess

def update_local_repo():
    try:
        subprocess.run(["git", "checkout", "master"], check=True)
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(["git", "pull", "origin", "master", "--rebase"], check=True)
        print("✅ Dépôt local synchronisé avec GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la synchronisation Git : {e}")

update_local_repo()

import subprocess
import os
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# === CONFIGURATION ===
symbol = 'XRPUSDT'
timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '1d']
limit = 1000
days_to_fetch = 30

# ✅ Chemin universel
dest_folder = os.path.join(os.getcwd(), "binancexrp")
os.makedirs(dest_folder, exist_ok=True)

# === INDICATEURS ===
def add_macd(df, fast=12, slow=26, signal=9):
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    df['MACD_DIF'] = exp1 - exp2
    df['MACD_DEA'] = df['MACD_DIF'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD_DIF'] - df['MACD_DEA']
    return df

def add_kdj(df, period=9, k_smooth=3, d_smooth=3):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
    k = rsv.ewm(com=k_smooth - 1).mean()
    d = k.ewm(com=d_smooth - 1).mean()
    j = 3 * k - 2 * d
    df['K'] = k
    df['D'] = d
    df['J'] = j
    return df

# === API Binance ===
def get_klines(symbol, interval, start_time, limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit,
        'startTime': int(start_time)
    }
    response = requests.get(url, params=params)
    return response.json()

def convert_to_df(data):
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

# === TÉLÉCHARGEMENT DES DONNÉES ===
for interval in timeframes:
    print(f"Téléchargement : {interval}")
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days_to_fetch)).timestamp() * 1000)
    all_data = []

    while start_time < end_time:
        raw_data = get_klines(symbol, interval, start_time, limit)
        if not raw_data:
            break
        df = convert_to_df(raw_data)
        all_data.append(df)

        last_time = raw_data[-1][0]
        start_time = last_time + 60_000
        time.sleep(0.3)

    if all_data:
        final_df = pd.concat(all_data)
        final_df = final_df[~final_df.index.duplicated(keep='first')]
        final_df.sort_index(inplace=True)

        final_df = add_macd(final_df)
        final_df = add_kdj(final_df)

        filename = f"xrp_{interval}_last30days.csv"
        filepath = os.path.join(dest_folder, filename)
        final_df.to_csv(filepath, encoding='utf-8')
        print(f"✅ Sauvegardé : {filepath}")
    else:
        print(f"❌ Aucun résultat pour {interval}")

# === PUSH AUTOMATIQUE VERS GITHUB ===
def push_to_github():
    try:
        subprocess.run(["git", "checkout", "master"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Update CSV data"], check=True)
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("✅ Données poussées sur GitHub (branche 'master') avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du push Git : {e}")

push_to_github()
