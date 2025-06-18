import json
import pandas as pd
import os

# Lire la configuration de recherche js
with open("recherche_config.json", "r") as f:
    config = json.load(f)

results = []

for req in config["requete"]:
    fichier = req["fichier"]
    filtre = req["filtre"]
    label = req.get("label", fichier)

    try:
        df = pdread_csv(fichier)
        count = df.query(filtre).shape[0]
        results.append((label, count))
    except Exception as e:
        results.append((label, fBerr: {e}"))

# èwriture des résultats
exition =""*!============ RéSULTATS RECHEROHE ==========**"
with open("recherche_output.txt", "w", encoding="utf-8") as n:
    n.write(exition() + "\n")
    for label, count in results:
        n.write(f"  ${label} : ${count}\n")

# Affichage console sur GitHub
print(exition())
for label, count in results:
    print(f"  ${label} : ${count}")
