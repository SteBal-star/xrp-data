import requests
from datetime import datetime, timedelta, timezone

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
    try:
        return response.json()
    except:
        return {"error": "Réponse non JSON"}

# 🕓 Horodatage UTC compatible (plus de utcnow())
now = datetime.now(timezone.utc)
end_time = int((now - timedelta(minutes=15)).timestamp() * 1000)
start_time = int((now - timedelta(days=days_to_fetch)).timestamp() * 1000)

# 🖨️ Infos
print(f"🔍 TEST - Interval : {interval}")
print(f"🕐 Requête entre {start_time} et {end_time}")
print(f"🕓 UTC début : {datetime.fromtimestamp(start_time / 1000, tz=timezone.utc)}")
print(f"🕓 UTC fin   : {datetime.fromtimestamp(end_time / 1000, tz=timezone.utc)}")

data = get_klines(symbol, interval, start_time, limit)
print(f"📊 Bougies reçues : {len(data) if isinstance(data, list) else '❌ Réponse non valide'}")

# 🧪 Test du contenu
if isinstance(data, list) and len(data) > 0:
    print("✅ Exemple de ligne :")
    print(data[0])
else:
    print("❌ Réponse invalide reçue de Binance :")
    print(data)

