@echo off
echo [🟢] Démarrage du script XRP Binance...

REM ==== CONFIGUREZ VOTRE PYTHON CI-DESSOUS ====
SET PYTHON_PATH="C:\Users\That's Me\AppData\Local\Programs\Python\Python313\python.exe"

REM ==== EMPLACEMENT DE VOTRE SCRIPT ====
SET SCRIPT_PATH="C:\Users\That's Me\Desktop\xrp-data\main.py"
SET WORKING_DIR="C:\Users\That's Me\Desktop\xrp-data"

REM ==== LANCEMENT DU SCRIPT ====
cd /d %WORKING_DIR%
%PYTHON_PATH% %SCRIPT_PATH%

echo [✅] Script terminé. Fermeture dans 5 secondes...
timeout /t 5
