@echo off
cd /d "C:\Users\That's Me\Desktop\xrp-data"
echo Lancement du script Python...
python main.py

if %ERRORLEVEL% neq 0 (
    echo Une erreur est survenue lors de l'exécution du script Python.
) else (
    echo Script exécuté avec succès.
)
pause
