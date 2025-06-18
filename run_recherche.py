import json
import pandas as pd
import os

# Lire la configuration de recherche
with open("recherche_config.json", "r") as f:
    config = json.load(f)

results = []

for req in config["requete"]:
    try:
        tf_list = req.get("timeframes", [])
        indicator = req["indicateur"]
        op = req["condition"]
        val = req["valeur"]

        for tf in tf_list:
            filename = f"binancexrp/xrp_{tf}_last30days.csv"
            df = pd.read_csv(filename)
            expr = f"{indicator} {op} {val}"
            count = df.query(expr).shape[0]
            label = f"{indicator} {op} {val} ({tf})"
            results.append((label, count))
    except Exception as e:
        results.append((label, f"Erreur: {e}"))

# Écriture des résultats
exit_text = "**===== RÉSULTATS RECHERCHE =====**"
with open("recherche_output.txt", "w", encoding="utf-8") as n:
    n.write(exit_text + "\n")
    for label, count in results:
        n.write(f"🔹 {label} : {count}\n")

# Affichage console sur GitHub
print(exit_text)
for label, count in results:
    print(f"🔹 {label} : {count}")
