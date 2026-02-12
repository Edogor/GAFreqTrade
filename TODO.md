# TODO - GAFreqTrade Implementation

## Aktueller Status / Current Status
- [x] Projektstruktur geplant
- [x] README erstellt
- [x] TODO Liste erstellt
- [ ] Verzeichnisstruktur angelegt
- [ ] Core Module implementiert

## Phase 1: Core Framework (Woche 1-2)

### 1.1 Projektstruktur anlegen
- [ ] Verzeichnisse erstellen (ga_core, evaluation, storage, etc.)
- [ ] __init__.py Dateien anlegen
- [ ] requirements.txt erstellen
- [ ] .gitignore konfigurieren

### 1.2 Strategie-Generator (ga_core/strategy_generator.py)
- [ ] Template für Freqtrade-Strategien erstellen
- [ ] Zufällige Strategie-Generierung implementieren
  - [ ] Indikator-Auswahl (RSI, MACD, BB, EMA, etc.)
  - [ ] Entry-Bedingungen generieren
  - [ ] Exit-Bedingungen generieren
  - [ ] Parameter-Ranges definieren
- [ ] Strategie in Python-Datei schreiben
- [ ] Strategie-Validierung (Syntax-Check)

### 1.3 Genetische Operationen (ga_core/genetic_ops.py)
- [ ] Mutation implementieren
  - [ ] Parameter-Mutation (Werte anpassen)
  - [ ] Indikator-Mutation (hinzufügen/entfernen)
  - [ ] Regel-Mutation (Bedingungen ändern)
- [ ] Crossover implementieren
  - [ ] Single-Point Crossover
  - [ ] Multi-Point Crossover
  - [ ] Indikator-Crossover
- [ ] Selektion implementieren
  - [ ] Tournament Selection
  - [ ] Roulette Wheel Selection
  - [ ] Elite Selection

### 1.4 Population Management (ga_core/population.py)
- [ ] Population-Klasse erstellen
- [ ] Initiale Population generieren
- [ ] Population speichern/laden
- [ ] Generation-Tracking
- [ ] Parent-Tracking

## Phase 2: Evaluation System (Woche 3)

### 2.1 Backtesting Integration (evaluation/backtester.py)
- [ ] Freqtrade Backtest-Wrapper
- [ ] Backtest-Konfiguration
- [ ] Parallelisierung für mehrere Strategien
- [ ] Fehlerbehandlung (ungültige Strategien)
- [ ] Timeout-Management

### 2.2 Fitness-Funktion (evaluation/fitness.py)
- [ ] Backtest-Metriken extrahieren
  - [ ] Total Profit
  - [ ] Sharpe Ratio
  - [ ] Max Drawdown
  - [ ] Win Rate
  - [ ] Avg Win/Loss
  - [ ] Trade Count
- [ ] Fitness-Score berechnen
- [ ] Gewichtungs-Parameter konfigurierbar machen
- [ ] Penalty für schlechte Strategien

### 2.3 Performance-Metriken (evaluation/metrics.py)
- [ ] Standard-Metriken implementieren
- [ ] Risiko-Metriken
- [ ] Stabilitäts-Score
- [ ] Vergleichs-Funktionen
- [ ] Statistiken über Generationen

## Phase 3: Storage & Tracking (Woche 3-4)

### 3.1 Strategie-Datenbank (storage/strategy_db.py)
- [ ] SQLite Datenbank-Schema
  - [ ] Strategies-Tabelle
  - [ ] Results-Tabelle
  - [ ] Generations-Tabelle
- [ ] CRUD-Operationen
- [ ] Strategie speichern (Code + Metadata)
- [ ] Strategie laden
- [ ] Suche und Filter

### 3.2 Results Tracking (storage/results_db.py)
- [ ] Backtest-Ergebnisse speichern
- [ ] Metriken-Historie
- [ ] Performance über Zeit
- [ ] Generationen-Statistiken

### 3.3 Leaderboard (storage/leaderboard.py)
- [ ] Top-N Strategien tracken
- [ ] Hall of Fame
- [ ] Ranking-Algorithmus
- [ ] Export-Funktionen

## Phase 4: Orchestration (Woche 4-5)

### 4.1 Evolution Loop (orchestration/evolution_loop.py)
- [ ] Main Evolution Loop
  - [ ] Generation initialisieren
  - [ ] Evaluation durchführen
  - [ ] Fitness berechnen
  - [ ] Selektion durchführen
  - [ ] Genetic Operations
  - [ ] Neue Generation erstellen
- [ ] Checkpointing
- [ ] Resume-Funktionalität
- [ ] Progress-Tracking

### 4.2 Scheduler (orchestration/scheduler.py)
- [ ] Multi-Day Execution
- [ ] Pausieren/Fortsetzen
- [ ] Resource Management
- [ ] Zeitplanung (CPU-Last verteilen)

### 4.3 Monitoring (orchestration/monitor.py)
- [ ] Live-Status anzeigen
- [ ] Fortschritts-Tracking
- [ ] Performance-Plots
- [ ] Logging-Integration

## Phase 5: Configuration & Utils (Woche 5)

### 5.1 Configuration Management (config/)
- [ ] YAML-Config Parser
- [ ] Default-Konfigurationen
- [ ] Config-Validierung
- [ ] Config-Templates

### 5.2 Logging System (utils/logger.py)
- [ ] Strukturiertes Logging
- [ ] Log-Levels
- [ ] File-Rotation
- [ ] Performance-Logging

### 5.3 Visualization (utils/visualization.py)
- [ ] Fitness über Generationen
- [ ] Performance-Vergleiche
- [ ] Population-Diversity
- [ ] Top-Strategien Dashboard

## Phase 6: Main Scripts (Woche 6)

### 6.1 Haupt-Skripte
- [ ] run_evolution.py - Haupt-Entry-Point
- [ ] monitor.py - Live-Monitoring
- [ ] report.py - Report-Generierung
- [ ] show_leaderboard.py - Top-Strategien anzeigen
- [ ] export_strategy.py - Strategie exportieren

### 6.2 CLI Interface
- [ ] argparse für Kommandozeilen-Parameter
- [ ] Help-Texte
- [ ] Config-Override via CLI

## Phase 7: Testing (Woche 6-7)

### 7.1 Unit Tests
- [ ] Tests für strategy_generator
- [ ] Tests für genetic_ops
- [ ] Tests für fitness
- [ ] Tests für population

### 7.2 Integration Tests
- [ ] End-to-End Evolution Test
- [ ] Backtest Integration Test
- [ ] Storage Tests

### 7.3 Validation
- [ ] Strategie-Syntax-Validierung
- [ ] Performance-Tests
- [ ] Memory-Tests (wichtig für Pi)

## Phase 8: Documentation (Woche 7-8)

### 8.1 Code-Dokumentation
- [ ] Docstrings für alle Module
- [ ] Type Hints
- [ ] Inline-Kommentare

### 8.2 User-Dokumentation
- [ ] Installation-Guide
- [ ] Quick-Start Guide
- [ ] Configuration-Guide
- [ ] Troubleshooting

### 8.3 Deployment-Guide
- [ ] Raspberry Pi Setup
- [ ] Service-Konfiguration
- [ ] Monitoring-Setup
- [ ] Backup-Strategie

## Phase 9: Optimization (Woche 8)

### 9.1 Performance
- [ ] Parallelisierung optimieren
- [ ] Memory-Optimierung
- [ ] Caching implementieren
- [ ] Profiling

### 9.2 Raspberry Pi Specific
- [ ] CPU-Throttling beachten
- [ ] Memory-Limits
- [ ] Storage-Optimierung
- [ ] Swap-Konfiguration

## Optionale Erweiterungen (Zukunft)

### ML Integration
- [ ] FreqAI Integration
- [ ] Feature-Engineering
- [ ] ML-basierte Fitness-Vorhersage

### LLM Integration
- [ ] Grok API Integration
- [ ] Strategie-Generierung via LLM
- [ ] Code-Review via LLM

### Island Model
- [ ] Multi-Population Support
- [ ] Migration zwischen Inseln
- [ ] Diversitäts-Tracking

### Advanced Features
- [ ] Dry-Run Integration
- [ ] Live-Trading Vorbereitung
- [ ] Real-Time Performance-Tracking
- [ ] Telegram-Notifications
- [ ] Web-Dashboard

## Prioritäten

### Must Have (MVP)
1. Strategie-Generator (zufällig)
2. Genetische Operationen (Mutation, Crossover, Selection)
3. Backtest-Integration
4. Fitness-Funktion
5. Evolution Loop
6. Basic Storage

### Should Have
7. Monitoring
8. Leaderboard
9. Configuration System
10. Logging

### Nice to Have
11. Visualization
12. Advanced Genetic Ops
13. Multi-day Scheduling
14. CLI Interface

### Future
15. ML Integration
16. LLM Integration
17. Island Model
18. Web Dashboard

## Notizen

### Technische Entscheidungen
- Python 3.9+ (für Type Hints und Performance)
- SQLite für Storage (einfach, keine externe DB nötig)
- YAML für Konfiguration (lesbarer als JSON)
- Multiprocessing für Parallelisierung

### Raspberry Pi Considerations
- Populationsgröße: 50-100 (nicht mehr, wegen Memory)
- Parallelität: 2-4 Prozesse (abhängig von Pi-Modell)
- Checkpointing: Alle 10 Generationen (SD-Karte schonen)
- Monitoring: Minimal (CPU sparen)

### Risiken
- Backtest-Dauer (mitigation: Parallelisierung, kürzere Perioden)
- Overfitting (mitigation: Out-of-Sample Validation)
- Lokale Optima (mitigation: höhere Mutation-Rate, Diversity)
- Memory-Limits (mitigation: kleinere Population, Swap)

---

**Nächste Schritte:**
1. Verzeichnisstruktur anlegen
2. requirements.txt erstellen
3. Strategy Generator implementieren (erste Version)
4. Einfache Fitness-Funktion
5. Ersten Evolution-Test durchführen
