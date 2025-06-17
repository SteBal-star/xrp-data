import requests
import pandas as pd
from datetime import datetime, timedelta

symbol = 'XRPUSDT'
interval = '1m'
limit = 1000
days_to_fetch = 1

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

print(f"🔍 TEST - Interval : {interval}")

end_time = int((datetime.utcnow() - timedelta(minutes=15)).timestamp() * 1000)
start_time = int((datetime.utcnow() - timedelta(days=days_to_fetch)).timestamp() * 1000)

print(f"🕐 Requête entre {start_time} et {end_time}")
print(f"🕓 UTC début : {datetime.utcfromtimestamp(start_time / 1000)}")
print(f"🕓 UTC fin   : {datetime.utcfromtimestamp(end_time / 1000)}")

data = get_klines(symbol, interval, start_time, limit)
print(f"📊 Bougies reçues : {len(data)}")

# Vérification simple
if len(data) > 0:
    print("✅ Exemple de ligne :")
    print(data[0])
else:
    print("❌ Aucune donnée retournée")
