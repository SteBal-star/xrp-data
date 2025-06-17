## Protocole de stratégie - v1.0

Ce protocole définit la méthodologie de traitement automatisé lors du backtest.

- [x] Exécution automatique lors de la demande :
      "Test une nouvelle stratégie avec les caractéristiques : ..."
- [x] Sans confirmation complémentaire, il exécute les tâches suivantes
- [x] Fournit un résultat structuré (tableau, résumé, logging préparé)

### 🔗 Fichier de résultats standard

Tous les résultats de backtest sont disponibles dans ce fichier :
📄 [backtest_output.txt](https://github.com/SteBal-star/xrp-data/blob/master/backtest_output.txt)

---

### 🧠 Étapes après chaque backtest (procédure de sauvegarde)

1. 📝 **Demander à l'utilisateur s'il souhaite enregistrer la stratégie dans `logbook.json`**
   - Si la réponse est **non**, aucun enregistrement n’est effectué
   - Si la réponse est **oui**, passer à l’étape suivante

2. 📘 **Demander s’il souhaite générer un fichier de trades détaillé**
   - Le fichier est créé dans `logbook/`, nommé :
     `strategie_<date>_<nom>.json`
   - Il contient :
     - Les horodatages d’entrée et de sortie
     - Les prix d’entrée et de sortie
     - L’effet de levier
     - Le % brut, les frais, et le % net
     - Le capital cumulé après chaque opération
