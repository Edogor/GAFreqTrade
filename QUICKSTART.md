# Quick Start Guide - GAFreqTrade

## Schnellstart für die Entwicklung

### 1. Repository-Übersicht

Nach dem Setup haben Sie folgende Struktur:

```
GAFreqTrade/
├── README.md                    # Projekt-Übersicht
├── TODO.md                      # Aufgaben-Liste
├── ARCHITECTURE.md              # System-Architektur
├── IMPLEMENTATION_PLAN.md       # Detaillierter Implementierungsplan
├── QUICKSTART.md               # Diese Datei
├── requirements.txt             # Python-Abhängigkeiten
├── .gitignore                  # Git-Ignore-Regeln
│
├── config/                      # Konfigurationsdateien
│   ├── ga_config.yaml          # Genetischer Algorithmus Config
│   └── eval_config.yaml        # Evaluation Config
│
├── ga_core/                     # Kern des GA-Systems
│   ├── __init__.py
│   ├── strategy_generator.py   # [TODO] Strategie-Generator
│   ├── genetic_ops.py          # [TODO] Genetische Operationen
│   └── population.py           # [TODO] Population Management
│
├── evaluation/                  # Bewertungs-System
│   ├── __init__.py
│   ├── backtester.py           # [TODO] Backtest-Integration
│   ├── fitness.py              # [TODO] Fitness-Funktion
│   └── metrics.py              # [TODO] Performance-Metriken
│
├── storage/                     # Datenspeicherung
│   ├── __init__.py
│   ├── strategy_db.py          # [TODO] Strategie-Datenbank
│   ├── results_db.py           # [TODO] Ergebnis-Speicherung
│   └── leaderboard.py          # [TODO] Top-Strategien
│
├── orchestration/               # System-Orchestrierung
│   ├── __init__.py
│   ├── evolution_loop.py       # [TODO] Haupt-Evolution
│   ├── scheduler.py            # [TODO] Scheduling
│   └── monitor.py              # [TODO] Monitoring
│
├── utils/                       # Hilfsfunktionen
│   ├── __init__.py
│   ├── logger.py               # [TODO] Logging
│   ├── config_loader.py        # [TODO] Config-Loader
│   └── visualization.py        # [TODO] Visualisierung
│
├── strategies/                  # Generierte Strategien
│   ├── generated/              # Auto-generierte Strategien
│   └── hall_of_fame/           # Beste Strategien
│
├── checkpoints/                 # Evolution Checkpoints
├── logs/                        # Log-Dateien
│
└── freqtrade/                   # Freqtrade Installation
    └── user_data/
        ├── strategies/         # Freqtrade Strategien
        ├── config.json         # Freqtrade Config
        └── backtest_results/   # Backtest Ergebnisse
```

### 2. Was wurde bereits erstellt?

✅ **Dokumentation:**
- README.md mit Projekt-Übersicht
- TODO.md mit detaillierter Aufgabenliste
- ARCHITECTURE.md mit System-Design
- IMPLEMENTATION_PLAN.md mit Implementierungs-Roadmap

✅ **Struktur:**
- Alle Hauptverzeichnisse erstellt
- __init__.py Dateien für Python-Module
- .gitignore für sauberes Repository

✅ **Konfiguration:**
- ga_config.yaml - GA-Parameter
- eval_config.yaml - Evaluierungs-Einstellungen
- requirements.txt - Python-Dependencies

✅ **Freqtrade:**
- Basis-Installation vorhanden
- Beispiel-Strategien (MyStrat.py, Blink5s.py)
- Config-Datei konfiguriert

### 3. Nächste Schritte (für Entwicklung)

#### Phase 1: Core Implementation

**Schritt 1: Utils implementieren**
```bash
# Erstelle utils/logger.py
# Erstelle utils/config_loader.py
```

**Schritt 2: Strategy Generator (Erste Version)**
```bash
# Erstelle ga_core/strategy_generator.py
# Basis-Funktionalität:
# - Template laden
# - Zufällige Indikatoren wählen
# - Strategie-Code generieren
# - In Datei schreiben
```

**Schritt 3: Backtester**
```bash
# Erstelle evaluation/backtester.py
# Integration mit Freqtrade CLI
# Backtest ausführen und Ergebnisse parsen
```

**Schritt 4: Fitness Function**
```bash
# Erstelle evaluation/fitness.py
# Bewertung basierend auf Backtest-Metriken
```

**Schritt 5: Test**
```bash
# Generiere 10 Strategien
# Backteste sie
# Berechne Fitness
```

### 4. Development Workflow

#### Virtual Environment Setup
```bash
cd /home/runner/work/GAFreqTrade/GAFreqTrade
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Arbeiten an einem Modul
```bash
# 1. Erstelle/Editiere Datei
# 2. Teste das Modul einzeln
python -m ga_core.strategy_generator  # Wenn __main__ Block vorhanden

# 3. Integration Test
# 4. Commit
git add .
git commit -m "Implement strategy generator"
```

#### Testing
```bash
# Unit tests
pytest tests/test_strategy_generator.py

# Integration test
python test_evolution.py --generations 5
```

### 5. Entwicklungs-Reihenfolge (Priorität)

**SEHR HOCH (für MVP):**
1. ⏳ utils/logger.py
2. ⏳ utils/config_loader.py
3. ⏳ ga_core/strategy_generator.py
4. ⏳ evaluation/backtester.py
5. ⏳ evaluation/fitness.py
6. ⏳ ga_core/genetic_ops.py
7. ⏳ ga_core/population.py
8. ⏳ orchestration/evolution_loop.py
9. ⏳ storage/strategy_db.py
10. ⏳ run_evolution.py

**HOCH:**
11. ⏳ storage/leaderboard.py
12. ⏳ monitor.py
13. ⏳ show_leaderboard.py

**MITTEL:**
14. ⏳ orchestration/scheduler.py
15. ⏳ orchestration/monitor.py
16. ⏳ utils/visualization.py

### 6. Konfiguration anpassen

#### GA-Parameter (`config/ga_config.yaml`)
```yaml
# Für erste Tests: kleinere Population
population_size: 20        # Statt 100
generations: 50            # Statt 1000
elite_size: 3              # Statt 10
```

#### Evaluation (`config/eval_config.yaml`)
```yaml
# Für schnellere Backtests
backtest:
  period: "30d"            # Statt 90d
  timeframe: "15m"         # Statt 5m (weniger Daten)
```

### 7. Freqtrade Setup prüfen

```bash
cd freqtrade
# Check Freqtrade installation
freqtrade --version

# Download test data (if needed)
freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframe 5m --days 90

# Test existing strategy
freqtrade backtesting --strategy MyStrat --timeframe 5m --timerange 20240101-20240201
```

### 8. Erste Tests

#### Test 1: Strategy Generator
```python
# test_generator.py
from ga_core.strategy_generator import StrategyGenerator

gen = StrategyGenerator()
strategy = gen.generate_random()
print(f"Generated: {strategy['name']}")
print(f"Indicators: {strategy['indicators']}")
```

#### Test 2: Backtester
```python
# test_backtest.py
from evaluation.backtester import Backtester

bt = Backtester(config_path='freqtrade/user_data/config.json')
results = bt.run_backtest('MyStrat')
print(f"Profit: {results['total_profit']}%")
```

#### Test 3: Mini Evolution
```python
# test_mini_evolution.py
# Run 5 generations with 10 strategies
python run_evolution.py --config config/test_config.yaml
```

### 9. Monitoring während Entwicklung

#### Logs checken
```bash
tail -f logs/evolution.log
```

#### Database checken
```bash
sqlite3 strategies.db
sqlite> SELECT name, fitness_score FROM results ORDER BY fitness_score DESC LIMIT 10;
```

#### Generierte Strategien ansehen
```bash
ls -la strategies/generated/
cat strategies/generated/Gen001_Strat_001.py
```

### 10. Troubleshooting

#### Problem: Freqtrade nicht gefunden
```bash
# Check PATH
which freqtrade

# Wenn in anderem Verzeichnis:
export PATH=$PATH:/path/to/freqtrade
```

#### Problem: Backtest schlägt fehl
```bash
# Test manuell
cd freqtrade
freqtrade backtesting --strategy MyStrat --timeframe 5m

# Check logs
cat user_data/logs/freqtrade.log
```

#### Problem: Memory issues
```bash
# Reduce population size in config
# Use checkpointing more frequently
# Clear old strategies
rm -rf strategies/generated/Gen0[0-5]*
```

### 11. Git Workflow

```bash
# Status checken
git status

# Änderungen committen
git add .
git commit -m "Implement [module name]"
git push origin main

# Neuer Branch für Feature
git checkout -b feature/strategy-generator
# ... work ...
git commit -m "Add strategy generator"
git push origin feature/strategy-generator
```

### 12. Performance Optimization (für Raspberry Pi)

#### Config für Pi
```yaml
# config/pi_config.yaml
population_size: 50       # Kleiner für Pi
parallel_backtests: 2     # Max 2-4 auf Pi
backtest_timeout: 600     # Länger für Pi
checkpoint_interval: 5    # Häufiger speichern
```

#### Resource Monitoring
```bash
# CPU & Memory
htop

# Temperature (wichtig für Pi!)
vcgencmd measure_temp

# Storage
df -h
```

### 13. Wichtige Befehle - Cheat Sheet

```bash
# Development
source venv/bin/activate          # Activate venv
pip install -r requirements.txt   # Install deps
python run_evolution.py           # Run evolution

# Testing
pytest tests/                     # Run all tests
python -m pytest tests/test_*.py  # Run specific test

# Monitoring
tail -f logs/evolution.log        # Watch logs
python monitor.py --live          # Live monitoring
python show_leaderboard.py        # Show top strategies

# Database
sqlite3 strategies.db             # Open DB
.schema                           # Show schema
.tables                           # List tables

# Cleanup
rm -rf strategies/generated/*     # Clear generated
rm -rf checkpoints/*              # Clear checkpoints
rm strategies.db                  # Reset database
```

### 14. Resources & Links

- **Freqtrade Docs:** https://www.freqtrade.io/en/stable/
- **Genetic Algorithms:** https://en.wikipedia.org/wiki/Genetic_algorithm
- **DEAP Framework:** https://deap.readthedocs.io/

### 15. Support

Bei Fragen oder Problemen:
1. Check TODO.md für aktuelle Tasks
2. Check IMPLEMENTATION_PLAN.md für Details
3. Check ARCHITECTURE.md für System-Design
4. Create GitHub Issue

---

**Viel Erfolg beim Entwickeln! 🚀**

**Status:** Projekt-Struktur erstellt, bereit für Implementierung
**Nächster Schritt:** Implementiere `ga_core/strategy_generator.py`
