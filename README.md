# GAFreqTrade - Genetic Algorithm Strategy Evolution System

## Übersicht / Overview

Dieses Projekt implementiert ein evolutionäres System zur automatischen Entwicklung, Evaluierung und Optimierung von Freqtrade-Handelsstrategien mittels genetischer Algorithmen.

This project implements an evolutionary system for automatically developing, evaluating, and optimizing Freqtrade trading strategies using genetic algorithms.

## Ziel / Goal

Ein System zu schaffen, das:
- Kontinuierlich Trading-Strategien generiert und testet
- Die besten Strategien durch Evolution verbessert
- Performance über Backtest und Dry-Run validiert
- Risiko, Drawdown und Verluste minimiert
- Die Top 5-10 besten Strategien laufend ausgibt
- Für Live-Trading (zunächst Dry-Mode) vorbereitet

## System-Architektur / System Architecture

### Hauptkomponenten / Main Components

```
GAFreqTrade/
├── ga_core/                    # Genetic Algorithm Core
│   ├── population.py          # Population management
│   ├── fitness.py             # Fitness evaluation
│   ├── genetic_ops.py         # Mutation, crossover, selection
│   └── strategy_generator.py  # Strategy generation
├── evaluation/                 # Strategy Evaluation
│   ├── backtester.py          # Backtesting integration
│   ├── metrics.py             # Performance metrics
│   └── validator.py           # Strategy validation
├── storage/                    # Data Persistence
│   ├── strategy_db.py         # Strategy storage
│   ├── results_db.py          # Results tracking
│   └── leaderboard.py         # Top strategies management
├── orchestration/              # System Orchestration
│   ├── evolution_loop.py      # Main evolution loop
│   ├── scheduler.py           # Multi-day scheduling
│   └── monitor.py             # Progress monitoring
├── config/                     # Configuration
│   ├── ga_config.yaml         # GA parameters
│   └── eval_config.yaml       # Evaluation settings
├── utils/                      # Utilities
│   ├── logger.py              # Logging system
│   └── visualization.py       # Performance visualization
└── strategies/                 # Generated Strategies
    ├── generation_001/        # Strategies by generation
    └── hall_of_fame/          # Best performing strategies
```

## Evolutionärer Prozess / Evolutionary Process

### 1. Initialization (Generation 0)
- Generiere 50-100 initiale Strategien
- Zufällige Parameter und Indikatorkombinationen
- Basis-Template mit bewährten Strukturen

### 2. Evaluation
Jede Strategie wird bewertet durch:
- **Backtest-Performance**: Profit, Sharpe Ratio, Max Drawdown
- **Stabilität**: Konsistenz über verschiedene Zeiträume
- **Risiko-Metriken**: Win-Rate, Avg. Win/Loss, Risk-Reward
- **Fitness-Score**: Gewichtete Kombination aller Metriken

### 3. Selection
- Top 10-20% der Population überleben
- Fitness-proportionale Selektion
- Elite-Strategien werden direkt übernommen

### 4. Genetic Operations
- **Mutation**: Parameter variieren (±5-20%)
- **Crossover**: Indikatoren und Regeln kombinieren
- **Innovation**: Neue Indikatoren hinzufügen

### 5. New Generation
- Auffüllen auf Populationsgröße
- Neue Generation evaluieren
- Zyklus wiederholen

## Fitness-Funktion / Fitness Function

```python
Fitness = w1 * Profit 
        + w2 * (1 / Max_Drawdown) 
        + w3 * Sharpe_Ratio
        + w4 * Win_Rate
        + w5 * Stability_Score
        - w6 * Trade_Count_Penalty
```

Gewichtung optimiert für:
- Profitabilität (30%)
- Risikominimierung (25%)
- Stabilität (20%)
- Win-Rate (15%)
- Sharpe Ratio (10%)

## Verwendung / Usage

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure Freqtrade
cd freqtrade
# Edit user_data/config.json for your exchange
```

### Running the Evolution
```bash
# Start evolution with default settings
python run_evolution.py

# Custom configuration
python run_evolution.py --config config/custom_ga_config.yaml

# Resume from checkpoint
python run_evolution.py --resume --checkpoint checkpoints/gen_050
```

### Monitoring
```bash
# View current progress
python monitor.py --live

# Generate performance report
python report.py --generation 100

# Show top strategies
python show_leaderboard.py --top 10

# Generate visualization plots
python visualize_evolution.py

# Monitor with visualization
python monitor.py --plot
```

### Visualization

The system includes comprehensive visualization tools:

```bash
# Generate all visualization plots
python visualize_evolution.py

# Generate specific plots
python visualize_evolution.py --fitness --dashboard

# Include plots in reports
python report.py --with-plots

# Run demo with sample data
python demo_visualization.py
```

**Available Visualizations:**
- Fitness evolution over generations
- Performance comparisons (profit, Sharpe ratio, drawdown, win rate)
- Population diversity tracking
- Top strategies dashboard

See [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md) for detailed documentation.

## Konfiguration / Configuration

### GA Parameters (`config/ga_config.yaml`)
```yaml
population_size: 100
generations: 1000
elite_size: 10
mutation_rate: 0.2
crossover_rate: 0.7
tournament_size: 5
```

### Evaluation Settings (`config/eval_config.yaml`)
```yaml
backtest_period: "90d"
timeframe: "5m"
starting_balance: 1000
max_trades: 3
stake_amount: "unlimited"
```

## Strategie-Template / Strategy Template

Alle generierten Strategien basieren auf einem modularen Template:
```python
class GeneratedStrategy(IStrategy):
    # Indicators: Auswahl aus 20+ Indikatoren
    # Entry Logic: Kombinationen von Bedingungen
    # Exit Logic: ROI, Stoploss, Exit-Signale
    # Risk Management: Position sizing, Stoploss-Anpassung
```

## Performance Tracking

Für jede Strategie wird getrackt:
- Generation, Parent IDs
- Backtest-Ergebnisse (alle Metriken)
- Dry-Run Performance (wenn aktiviert)
- Genetische Operationen (Mutation/Crossover)
- Zeitstempel und Version

## Deployment auf Raspberry Pi / Raspberry Pi Deployment

### Requirements
- Raspberry Pi 4 (mindestens 4GB RAM empfohlen)
- Python 3.9+
- 32GB+ SD-Karte für Daten
- Stabile Internetverbindung

### Installation
```bash
# System dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv build-essential

# Clone repository
git clone https://github.com/Edogor/GAFreqTrade.git
cd GAFreqTrade

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure as service (optional)
sudo systemctl enable gafreqtrade
sudo systemctl start gafreqtrade
```

## Roadmap

### Phase 1: Core Implementation (Woche 1-2)
- [x] Projektstruktur erstellen
- [ ] Basis-GA Framework
- [ ] Strategie-Generator
- [ ] Backtest-Integration

### Phase 2: Evaluation System (Woche 3)
- [ ] Fitness-Funktion implementieren
- [ ] Performance-Metriken
- [ ] Storage-System

### Phase 3: Evolution Loop (Woche 4)
- [ ] Genetische Operationen
- [ ] Population Management
- [ ] Generationen-Loop

### Phase 4: Monitoring & Optimization (Woche 5-6)
- [ ] Logging und Monitoring
- [ ] Visualisierung
- [ ] Performance-Optimierung

### Phase 5: Testing & Deployment (Woche 7-8)
- [ ] Tests schreiben
- [ ] Dry-Run Validierung
- [ ] Raspberry Pi Deployment

## Erweiterungen / Extensions (Optional)

### Machine Learning Integration
- FreqAI für Feature-Engineering
- ML-basierte Fitness-Vorhersage
- Sentiment-Analysis Integration

### Island Model
- Multiple parallele Populationen
- Verschiedene Fitness-Gewichtungen
- Periodischer Strategie-Austausch

### API Integration
- LLM-gestützte Strategie-Generierung (Grok, OpenAI)
- Automatische Code-Reviews
- Strategie-Erklärungen

## Lizenz / License

MIT License - Siehe LICENSE Datei

## Kontakt / Contact

Bei Fragen oder Problemen bitte ein Issue erstellen.

---

**Hinweis**: Dieses System ist für Lernzwecke gedacht. Trading mit echtem Geld birgt Risiken. Immer zuerst im Dry-Mode testen!
