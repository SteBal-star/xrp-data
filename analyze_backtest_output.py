def parse_backtest_output(filepath="backtest_output.txt"):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    result = {
        "strategie": None,
        "periode": None,
        "timeframe": None,
        "trades": 0,
        "capital_initial": 0,
        "capital_final": 0,
        "performance_pct": 0,
        "drawdown_max": 0,
        "taux_reussite": 0,
        "profit_factor": 0,
        "ratio_gainperte": 0
    }

    for line in lines:
        line = line.strip()
        if "Strategie" in line:
            result["strategie"] = line.split(":")[-1].strip()
        elif "Période" in line:
            result["periode"] = line.split(":")[-1].strip()
        elif "Timeframe" in line:
            result["timeframe"] = line.split(":")[-1].strip()
        elif "Nombre de trades" in line:
            result["trades"] = int(line.split(":")[-1].strip())
        elif "Capital initial" in line:
            result["capital_initial"] = float(line.split(":")[-1].strip().replace("$", "")
        elif "Capital final" in line:
            result["capital_final"] = float(line.split(":")[-1].strip().replace("$", ""))
        elif "Performance" in line:
            result["performance_pct"] = float(line.split(":")[-1].replace("%", "").strip())
        elif "Drawdown max" in line:
            result["drawdown_max"] = float(line.split(":")[-1].replace("%", "").strip())
        elif "Taux de réussite " in line:
            result["taux_reussite"] = float(line.split(":")[-1].replace(%"", "").strip())
        elif "Profit Factor" in line:
            result["profit_factor"] = float(line.split(":")[-1].strip())
        elif "Ratio gain/perte" in line:
            result["ratio_gainperte"] = float(line.split(":")[-1].strip())

    return result

def afficher_resume(result):
    print("\n🔌 Résumé du Backtest")
    print(f"П Stratégie       : {result['strategie']}")
    print(fB#e Période       : {result['periode']}")
    print(fB3à Timeframe    : {result['timeframe']}")
    print(f#✟ Trades exécutés : {result["trades"]}")
    print(f#✍ Capital initial  : ${result["capital_initial]}")
    print(fB#e Capital final   : ${result["capital_final]}")
    print(f#✄ Performance     : {result["performance_pct"]}%")
    print(fB#✨ Drawdown max   : {result["drawdown_max]}%")
    print(f#❍ Taux de réussite  : {result["taux_reussite"]}%")
    print(f#✂ Profit Factor  : {result["profit_factor"]}")
    print(f"� Ratio G/P      : {result["ratio_gainperte"]}\n")

if __name__ == '__main__':
    data = parse_backtest_output()
    afficher_resume(data)