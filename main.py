import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import subprocess

# === CONFIGURATION GÉNÉRALE ===
symbol = 'XRPUSDT'
timeframes = ['1m','3m','5m','15m','30m','1h','2h','4h','1d']
limit = 1000
days_to_fetch = 30
local_repo_path = "./Binancexrp"

# === CRÉATION DU DOSSIER LOCAL ===
os.makedirs(local_repo_path, exist_ok=True)

# === INDICATEURS TECHNIQUES ===
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

# === RÉCUPÉRATION BINANCE ===
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

# === TRAITEMENT DE TOUS LES TIMEFRAMES ===
for interval in timeframes:
    print(f"▶ Téléchargement : {interval}")
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days_to_fetch)).timestamp() * 1000)
    all_data = []

    while start_time < end_time:
        raw_data = get_klines(symbol, interval, start_time, limit)

# Sécurité : si la réponse est vide ou incorrecte
if not raw_data or not isinstance(raw_data, list) or len(raw_data) == 0:
    print(f"❌ Pas de données reçues pour {interval} à partir de {start_time}")
    break

try:
    df = convert_to_df(raw_data)
    all_data.append(df)
    last_time = raw_data[-1][0]
except Exception as e:
    print(f"⚠️ Erreur lors du traitement des données {interval} : {e}")
    break

        start_time = last_time + 60_000
        time.sleep(0.3)

    if all_data:
        final_df = pd.concat(all_data)
        final_df = final_df[~final_df.index.duplicated(keep='first')]
        final_df.sort_index(inplace=True)

        final_df = add_macd(final_df)
        final_df = add_kdj(final_df)

        filename = f"xrp_{interval}_last30days.csv"
        filepath = os.path.join(local_repo_path, filename)
        final_df.to_csv(filepath)
        print(f"✅ Sauvegardé : {filepath}")
    else:
        print(f"❌ Aucun résultat pour {interval}")

# === GIT : PUSH AUTOMATIQUE VERS LE DÉPÔT ===
github_token = os.getenv("GITHUB_TOKEN")
github_user = "SteBal-star"
repo_name = "xrp-data"
repo_url = f"https://{github_token}@github.com/{github_user}/{repo_name}.git"

# Init repo Git si besoin
if not os.path.exists(os.path.join(local_repo_path, ".git")):
    subprocess.run(["git", "init"], cwd=local_repo_path)
    subprocess.run(["git", "checkout", "-b", "main"], cwd=local_repo_path)

# Config git
subprocess.run(["git", "config", "user.name", "Sydney"], cwd=local_repo_path)
subprocess.run(["git", "config", "user.email", "sydney@example.com"], cwd=local_repo_path)

# Ajouter, commit, push
subprocess.run(["git", "add", "."], cwd=local_repo_path)
commit_msg = f"auto: update CSVs {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
subprocess.run(["git", "commit", "-m", commit_msg], cwd=local_repo_path)

subprocess.run(["git", "remote", "remove", "origin"], cwd=local_repo_path, stderr=subprocess.DEVNULL)
subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=local_repo_path)
subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=local_repo_path)

print("🚀 Fichiers envoyés sur GitHub !")
