# Implementation Plan - GAFreqTrade

## Übersicht

Dieses Dokument beschreibt den konkreten Implementierungsplan für das GAFreqTrade-System, basierend auf der Architektur und den Zielen.

## Phasenweise Implementierung

### Phase 1: Foundation (Woche 1-2)

#### 1.1 Core Infrastructure
**Ziel:** Grundlegende Struktur und Hilfsfunktionen

**Dateien zu erstellen:**
1. `utils/logger.py` - Logging-System
2. `utils/config_loader.py` - YAML Config Loader
3. `ga_core/strategy_template.py` - Basis-Template für Strategien

**Priorität:** HOCH
**Geschätzte Zeit:** 2-3 Tage

#### 1.2 Strategy Generator (Minimal Version)
**Ziel:** Erste funktionierende Version, die Strategien generieren kann

**Kern-Funktionalität:**
- Template-basierte Generierung
- 5-10 Standard-Indikatoren (RSI, MACD, BB, EMA, SMA)
- Einfache Entry/Exit-Bedingungen
- Zufällige Parameter-Wahl

**Datei:** `ga_core/strategy_generator.py`

**Beispiel-Output:**
```python
class Gen001_Strat_001(IStrategy):
    # Auto-generated strategy
    buy_rsi = IntParameter(20, 40, default=30)
    sell_rsi = IntParameter(60, 80, default=70)
    
    def populate_indicators(self, dataframe, metadata):
        dataframe['rsi'] = ta.RSI(dataframe)
        # ... weitere Indikatoren
        return dataframe
    
    def populate_entry_trend(self, dataframe, metadata):
        dataframe.loc[(dataframe['rsi'] < self.buy_rsi.value), 'enter_long'] = 1
        return dataframe
```

**Priorität:** SEHR HOCH
**Geschätzte Zeit:** 3-4 Tage

#### 1.3 Basic Storage
**Ziel:** SQLite-Datenbank für Strategien und Ergebnisse

**Dateien:**
- `storage/database.py` - SQLAlchemy Models & Setup
- `storage/strategy_db.py` - Strategy CRUD operations

**Schema:** Siehe ARCHITECTURE.md

**Priorität:** HOCH
**Geschätzte Zeit:** 2 Tage

### Phase 2: Evaluation Engine (Woche 2-3)

#### 2.1 Backtesting Integration
**Ziel:** Strategien mit Freqtrade backtesten

**Datei:** `evaluation/backtester.py`

**Kern-Funktionalität:**
```python
class Backtester:
    def run_backtest(self, strategy_file: str) -> dict:
        # 1. Prepare Freqtrade command
        cmd = f"freqtrade backtesting --strategy {strategy_name} ..."
        
        # 2. Execute with timeout
        result = subprocess.run(cmd, timeout=300, capture_output=True)
        
        # 3. Parse JSON output
        results = parse_backtest_results(result.stdout)
        
        # 4. Return metrics
        return {
            'total_profit': ...,
            'sharpe_ratio': ...,
            'max_drawdown': ...,
            # ...
        }
```

**Priorität:** SEHR HOCH
**Geschätzte Zeit:** 3-4 Tage

#### 2.2 Fitness Function
**Ziel:** Bewertung der Strategie-Performance

**Datei:** `evaluation/fitness.py`

**Implementierung:**
```python
def calculate_fitness(backtest_results: dict, weights: dict) -> float:
    # Normalize metrics to 0-1 range
    norm_profit = normalize(backtest_results['total_profit'], 0, 100)
    norm_sharpe = normalize(backtest_results['sharpe_ratio'], -2, 4)
    norm_drawdown = 1 - normalize(backtest_results['max_drawdown'], 0, 1)
    # ...
    
    # Weighted sum
    fitness = (
        weights['profit'] * norm_profit +
        weights['sharpe'] * norm_sharpe +
        weights['drawdown'] * norm_drawdown +
        # ...
    )
    
    return fitness
```

**Priorität:** SEHR HOCH
**Geschätzte Zeit:** 2 Tage

#### 2.3 Metrics Collector
**Ziel:** Sammlung und Speicherung von Performance-Metriken

**Datei:** `evaluation/metrics.py`

**Priorität:** MITTEL
**Geschätzte Zeit:** 1-2 Tage

### Phase 3: Genetic Operations (Woche 3-4)

#### 3.1 Mutation
**Ziel:** Strategien mutieren

**Datei:** `ga_core/genetic_ops.py`

**Mutation-Typen:**

1. **Parameter Mutation:**
```python
def mutate_parameters(strategy: dict, rate: float) -> dict:
    for param, value in strategy['parameters'].items():
        if random.random() < rate:
            # Change value by ±mutation_strength
            new_value = value * (1 + random.uniform(-0.15, 0.15))
            strategy['parameters'][param] = new_value
    return strategy
```

2. **Indicator Mutation:**
```python
def mutate_indicators(strategy: dict, rate: float) -> dict:
    if random.random() < rate:
        # Add, remove, or replace an indicator
        action = random.choice(['add', 'remove', 'replace'])
        # ... implementation
    return strategy
```

**Priorität:** SEHR HOCH
**Geschätzte Zeit:** 3 Tage

#### 3.2 Crossover
**Ziel:** Zwei Strategien kombinieren

```python
def crossover(parent1: dict, parent2: dict) -> tuple:
    # Single-point crossover on indicators
    split_point = len(parent1['indicators']) // 2
    
    child1_indicators = parent1['indicators'][:split_point] + parent2['indicators'][split_point:]
    child2_indicators = parent2['indicators'][:split_point] + parent1['indicators'][split_point:]
    
    # ... create child strategies
    return child1, child2
```

**Priorität:** HOCH
**Geschätzte Zeit:** 2 Tage

#### 3.3 Selection
**Ziel:** Beste Strategien auswählen

```python
def tournament_selection(population: list, fitness_scores: list, k: int) -> dict:
    # Select k random strategies
    tournament = random.sample(list(zip(population, fitness_scores)), k)
    
    # Return the best one
    return max(tournament, key=lambda x: x[1])[0]
```

**Priorität:** HOCH
**Geschätzte Zeit:** 1 Tag

### Phase 4: Population & Evolution (Woche 4-5)

#### 4.1 Population Manager
**Ziel:** Verwaltung der Strategie-Population

**Datei:** `ga_core/population.py`

**Klasse:**
```python
class Population:
    def __init__(self, size: int, generation: int = 0):
        self.size = size
        self.generation = generation
        self.strategies = []
        self.fitness_scores = {}
    
    def initialize_random(self):
        """Create initial random population"""
        for i in range(self.size):
            strategy = generate_random_strategy()
            self.strategies.append(strategy)
    
    def get_top_n(self, n: int) -> list:
        """Get top N strategies by fitness"""
        sorted_pop = sorted(
            self.strategies, 
            key=lambda s: self.fitness_scores.get(s['name'], 0),
            reverse=True
        )
        return sorted_pop[:n]
    
    def save_checkpoint(self, path: str):
        """Save population state"""
        # ... implementation
```

**Priorität:** SEHR HOCH
**Geschätzte Zeit:** 2-3 Tage

#### 4.2 Evolution Loop
**Ziel:** Haupt-Evolutionsschleife

**Datei:** `orchestration/evolution_loop.py`

**Pseudo-Code:**
```python
def run_evolution(config):
    # 1. Initialize
    population = Population(size=config.population_size)
    population.initialize_random()
    
    for generation in range(config.max_generations):
        logger.info(f"Starting Generation {generation}")
        
        # 2. Evaluate all strategies
        for strategy in population.strategies:
            results = backtester.run_backtest(strategy)
            fitness = calculate_fitness(results, config.fitness_weights)
            population.fitness_scores[strategy['name']] = fitness
            
            # Save to database
            db.save_results(strategy, results, fitness)
        
        # 3. Select elite
        elite = population.get_top_n(config.elite_size)
        logger.info(f"Best fitness: {max(population.fitness_scores.values())}")
        
        # 4. Create offspring
        offspring = []
        while len(offspring) < (config.population_size - config.elite_size):
            # Selection
            parent1 = tournament_selection(population, config.tournament_size)
            parent2 = tournament_selection(population, config.tournament_size)
            
            # Crossover
            if random.random() < config.crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if random.random() < config.mutation_rate:
                child1 = mutate(child1)
            if random.random() < config.mutation_rate:
                child2 = mutate(child2)
            
            offspring.extend([child1, child2])
        
        # 5. Form new generation
        population.strategies = elite + offspring[:config.population_size - len(elite)]
        population.generation += 1
        
        # 6. Checkpoint
        if generation % config.checkpoint_interval == 0:
            population.save_checkpoint(f"checkpoints/gen_{generation:04d}")
        
        # 7. Update leaderboard
        update_leaderboard(elite)
```

**Priorität:** SEHR HOCH
**Geschätzte Zeit:** 3-4 Tage

### Phase 5: Utilities & Tools (Woche 5-6)

#### 5.1 Main Entry Point
**Datei:** `run_evolution.py`

```python
#!/usr/bin/env python3
import argparse
from utils.config_loader import load_config
from orchestration.evolution_loop import run_evolution

def main():
    parser = argparse.ArgumentParser(description='GAFreqTrade Evolution')
    parser.add_argument('--config', default='config/ga_config.yaml')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--checkpoint', type=str)
    args = parser.parse_args()
    
    config = load_config(args.config)
    run_evolution(config, resume=args.resume, checkpoint=args.checkpoint)

if __name__ == '__main__':
    main()
```

**Priorität:** HOCH
**Geschätzte Zeit:** 1 Tag

#### 5.2 Monitoring Tools
**Dateien:**
- `monitor.py` - Live progress monitoring
- `show_leaderboard.py` - Display top strategies
- `report.py` - Generate reports

**Priorität:** MITTEL
**Geschätzte Zeit:** 2-3 Tage

#### 5.3 Visualization
**Datei:** `utils/visualization.py`

**Features:**
- Fitness over generations
- Population diversity
- Performance comparison

**Priorität:** NIEDRIG (Nice to have)
**Geschätzte Zeit:** 2 Tage

### Phase 6: Testing & Validation (Woche 6-7)

#### 6.1 Unit Tests
- Test strategy generator
- Test genetic operations
- Test fitness calculation

**Priorität:** MITTEL
**Geschätzte Zeit:** 3-4 Tage

#### 6.2 Integration Tests
- End-to-end evolution test (10 generations)
- Checkpoint/resume test
- Database operations test

**Priorität:** MITTEL
**Geschätzte Zeit:** 2 Tage

### Phase 7: Documentation & Deployment (Woche 7-8)

#### 7.1 Documentation
- Usage guide
- API documentation
- Troubleshooting guide

**Priorität:** MITTEL
**Geschätzte Zeit:** 2-3 Tage

#### 7.2 Raspberry Pi Deployment
- Installation script
- Systemd service
- Performance optimization

**Priorität:** HOCH
**Geschätzte Zeit:** 2-3 Tage

## Minimal Viable Product (MVP)

**Was wird für MVP benötigt:**

1. ✅ Projektstruktur und Config-Dateien
2. ⏳ Strategy Generator (basic version)
3. ⏳ Backtester Integration
4. ⏳ Fitness Function
5. ⏳ Genetic Operations (Mutation, Crossover, Selection)
6. ⏳ Population Manager
7. ⏳ Evolution Loop (basic version)
8. ⏳ Storage (SQLite)
9. ⏳ run_evolution.py Entry Point

**Nicht für MVP:**
- Visualization
- Advanced monitoring
- LLM integration
- Island model
- Web dashboard

## Timeline Summary

| Phase | Dauer | Priorität |
|-------|-------|-----------|
| Phase 1: Foundation | 1-2 Wochen | SEHR HOCH |
| Phase 2: Evaluation | 1-2 Wochen | SEHR HOCH |
| Phase 3: Genetic Ops | 1-2 Wochen | SEHR HOCH |
| Phase 4: Evolution | 1-2 Wochen | SEHR HOCH |
| Phase 5: Utilities | 1-2 Wochen | HOCH |
| Phase 6: Testing | 1 Woche | MITTEL |
| Phase 7: Docs & Deploy | 1 Woche | HOCH |

**Gesamt-Zeit für MVP:** 6-8 Wochen
**Gesamt-Zeit mit allen Features:** 8-10 Wochen

## Nächste konkrete Schritte

1. **JETZT:** Commit der Projekt-Struktur und Dokumentation
2. **Tag 1-2:** Implementiere `utils/logger.py` und `utils/config_loader.py`
3. **Tag 3-5:** Implementiere `ga_core/strategy_generator.py` (erste Version)
4. **Tag 6-7:** Test: Generiere 10 Strategien und validiere sie
5. **Tag 8-10:** Implementiere `evaluation/backtester.py`
6. **Tag 11-12:** Implementiere `evaluation/fitness.py`
7. **Tag 13-15:** Test: Backteste generierte Strategien und berechne Fitness
8. **Woche 3:** Genetic Operations
9. **Woche 4:** Evolution Loop
10. **Woche 5+:** Polishing, Testing, Documentation

## Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Backtest dauert zu lange | Hoch | Hoch | Parallelisierung, kürzere Perioden |
| Strategien overfitten | Hoch | Mittel | Out-of-sample validation |
| Memory Issues auf Pi | Mittel | Hoch | Kleinere Population, Checkpointing |
| Freqtrade API ändert sich | Niedrig | Hoch | Wrapper-Layer, Version-Lock |
| Lokale Optima | Mittel | Mittel | Höhere Diversity, neue Random |

---

**Status:** 2024-02-12
**Erstellt von:** GAFreqTrade Development Plan
**Version:** 1.0
