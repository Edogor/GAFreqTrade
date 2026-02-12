# Architecture Overview - GAFreqTrade

## System Design

Das GAFreqTrade-System besteht aus mehreren miteinander verbundenen Komponenten, die zusammen ein evolutionäres Framework zur Strategie-Entwicklung bilden.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Evolution Controller                      │
│  (orchestration/evolution_loop.py)                          │
│  - Generationen-Management                                   │
│  - Checkpoint/Resume                                         │
│  - Progress Tracking                                         │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌────────────────────────────┐
│  Population Manager      │    │   Evaluation Engine        │
│  (ga_core/population.py) │    │   (evaluation/)            │
│                          │    │                            │
│  - Population Storage    │    │  - Backtester             │
│  - Generation Tracking   │    │  - Fitness Calculator      │
│  - Elite Management      │    │  - Metrics Collector       │
└──────────┬───────────────┘    └─────────────┬──────────────┘
           │                                   │
           ▼                                   │
┌──────────────────────────┐                  │
│  Genetic Operations      │                  │
│  (ga_core/genetic_ops.py)│                  │
│                          │                  │
│  - Mutation              │                  │
│  - Crossover             │                  │
│  - Selection             │                  │
└──────────┬───────────────┘                  │
           │                                   │
           ▼                                   │
┌──────────────────────────┐                  │
│  Strategy Generator      │                  │
│  (ga_core/               │                  │
│   strategy_generator.py) │                  │
│                          │                  │
│  - Template Engine       │◄─────────────────┘
│  - Random Generation     │
│  - Code Synthesis        │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│            Storage Layer                      │
│            (storage/)                         │
│                                               │
│  - Strategy Database (strategy_db.py)        │
│  - Results Database (results_db.py)          │
│  - Leaderboard (leaderboard.py)              │
└───────────────────────────────────────────────┘
```

## Datenfluss / Data Flow

### 1. Initialization Phase
```
User Input (Config)
    ↓
Evolution Controller creates Initial Population
    ↓
Strategy Generator creates N random strategies
    ↓
Strategies saved to Storage
```

### 2. Evaluation Phase
```
Population of Strategies
    ↓
For each Strategy:
    ↓
    Backtester runs strategy
    ↓
    Metrics Collector gathers results
    ↓
    Fitness Calculator computes fitness score
    ↓
Results saved to Storage
```

### 3. Selection Phase
```
Evaluated Population + Fitness Scores
    ↓
Genetic Operations: Selection
    ↓
Top N% strategies selected (Elite)
    ↓
Elite strategies saved
```

### 4. Reproduction Phase
```
Selected Strategies
    ↓
Genetic Operations:
    ├─→ Mutation (modify parameters)
    ├─→ Crossover (combine strategies)
    └─→ New Random (maintain diversity)
    ↓
New Generation Population
    ↓
Cycle repeats from Evaluation Phase
```

## Module Details

### 1. Strategy Generator (ga_core/strategy_generator.py)

**Verantwortlichkeit:**
- Erstellen von Freqtrade-konformen Strategien
- Zufällige und gezielte Generierung
- Template-basierte Code-Synthese

**Klassen:**
- `StrategyTemplate`: Basis-Template für alle Strategien
- `IndicatorLibrary`: Bibliothek verfügbarer Indikatoren
- `StrategyGenerator`: Haupt-Generator-Klasse

**Key Methods:**
```python
def generate_random_strategy() -> Strategy
def generate_from_genes(genes: dict) -> Strategy
def validate_strategy(strategy: Strategy) -> bool
def write_strategy_file(strategy: Strategy, path: str) -> None
```

**Strategy Structure:**
```python
Strategy = {
    'name': str,
    'genes': {
        'indicators': List[Indicator],
        'entry_conditions': List[Condition],
        'exit_conditions': List[Condition],
        'parameters': Dict[str, Any]
    },
    'metadata': {
        'generation': int,
        'parents': List[str],
        'created': datetime
    }
}
```

### 2. Genetic Operations (ga_core/genetic_ops.py)

**Verantwortlichkeit:**
- Implementierung genetischer Operatoren
- Mutation und Crossover
- Selektionsalgorithmen

**Key Functions:**
```python
def mutate(strategy: Strategy, rate: float) -> Strategy
def crossover(parent1: Strategy, parent2: Strategy) -> Tuple[Strategy, Strategy]
def tournament_selection(population: List[Strategy], k: int) -> Strategy
def elite_selection(population: List[Strategy], n: int) -> List[Strategy]
```

**Mutation Types:**
- Parameter Mutation: Werte innerhalb Range anpassen
- Indicator Mutation: Indikatoren hinzufügen/entfernen/austauschen
- Condition Mutation: Bedingungen ändern (AND/OR, Vergleichsoperatoren)

**Crossover Types:**
- Single-Point: Teile Indikatoren an einem Punkt
- Multi-Point: Teile an mehreren Punkten
- Uniform: Zufällige Gen-Auswahl von beiden Eltern

### 3. Fitness Function (evaluation/fitness.py)

**Verantwortlichkeit:**
- Bewertung der Strategie-Performance
- Berechnung des Fitness-Scores
- Multi-Objective Optimization

**Fitness Formula:**
```python
fitness = (
    w_profit * normalize(total_profit) +
    w_sharpe * normalize(sharpe_ratio) +
    w_drawdown * (1 - normalize(max_drawdown)) +
    w_winrate * normalize(win_rate) +
    w_stability * stability_score -
    w_trades * normalize(trade_count_penalty)
)
```

**Metriken:**
- `total_profit`: Gesamtgewinn in %
- `sharpe_ratio`: Risk-adjusted return
- `max_drawdown`: Maximaler Verlust
- `win_rate`: Gewinnrate der Trades
- `avg_trade_duration`: Durchschnittliche Trade-Dauer
- `profit_factor`: Gewinn/Verlust Ratio
- `stability_score`: Varianz der monatlichen Returns

### 4. Population Manager (ga_core/population.py)

**Verantwortlichkeit:**
- Verwaltung der Strategie-Population
- Generationen-Tracking
- Genealogie-Management

**Klasse: Population**
```python
class Population:
    def __init__(self, size: int, generation: int = 0)
    def add_strategy(self, strategy: Strategy)
    def get_strategy(self, name: str) -> Strategy
    def get_top_n(self, n: int) -> List[Strategy]
    def get_statistics() -> PopulationStats
    def save_checkpoint(self, path: str)
    def load_checkpoint(self, path: str)
```

### 5. Backtester (evaluation/backtester.py)

**Verantwortlichkeit:**
- Integration mit Freqtrade Backtesting
- Parallele Ausführung mehrerer Backtests
- Error Handling für fehlerhafte Strategien

**Klasse: Backtester**
```python
class Backtester:
    def __init__(self, config: dict)
    def run_backtest(self, strategy: Strategy) -> BacktestResults
    def run_parallel(self, strategies: List[Strategy]) -> List[BacktestResults]
    def validate_results(self, results: BacktestResults) -> bool
```

### 6. Storage Layer (storage/)

**Verantwortlichkeit:**
- Persistierung von Strategien und Ergebnissen
- Abfrage und Filterung
- Leaderboard-Management

**Database Schema:**

```sql
-- Strategies Table
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    generation INTEGER,
    genes TEXT,  -- JSON
    code TEXT,
    parent1_id INTEGER,
    parent2_id INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY (parent1_id) REFERENCES strategies(id),
    FOREIGN KEY (parent2_id) REFERENCES strategies(id)
);

-- Results Table
CREATE TABLE results (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER,
    fitness_score REAL,
    total_profit REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    win_rate REAL,
    trade_count INTEGER,
    backtest_start DATE,
    backtest_end DATE,
    evaluated_at TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);

-- Generations Table
CREATE TABLE generations (
    id INTEGER PRIMARY KEY,
    generation_number INTEGER,
    population_size INTEGER,
    avg_fitness REAL,
    best_fitness REAL,
    diversity_score REAL,
    completed_at TIMESTAMP
);
```

### 7. Evolution Controller (orchestration/evolution_loop.py)

**Verantwortlichkeit:**
- Orchestrierung des gesamten evolutionären Prozesses
- Checkpoint/Resume Management
- Progress Tracking

**Main Loop:**
```python
def run_evolution(config: dict):
    population = initialize_population(config)
    
    for generation in range(config.max_generations):
        # 1. Evaluate
        results = evaluate_population(population)
        
        # 2. Calculate Fitness
        fitness_scores = calculate_fitness(results)
        
        # 3. Update Leaderboard
        update_leaderboard(population, fitness_scores)
        
        # 4. Select Elite
        elite = select_elite(population, fitness_scores, config.elite_size)
        
        # 5. Create New Generation
        offspring = create_offspring(elite, config)
        
        # 6. Form New Population
        population = elite + offspring
        
        # 7. Checkpoint
        if generation % config.checkpoint_interval == 0:
            save_checkpoint(population, generation)
        
        # 8. Report Progress
        report_progress(generation, population, fitness_scores)
```

## Configuration System

### GA Config (config/ga_config.yaml)
```yaml
# Population Parameters
population_size: 100
elite_size: 10
generations: 1000

# Genetic Operators
mutation_rate: 0.2
mutation_strength: 0.15  # How much to change parameters
crossover_rate: 0.7
new_random_rate: 0.1  # Rate of completely new strategies

# Selection
selection_method: "tournament"  # or "roulette", "rank"
tournament_size: 5

# Fitness Weights
fitness_weights:
  profit: 0.30
  sharpe: 0.10
  drawdown: 0.25
  winrate: 0.15
  stability: 0.20
  trade_penalty: 0.05

# Performance
parallel_backtests: 4
backtest_timeout: 300  # seconds
```

### Evaluation Config (config/eval_config.yaml)
```yaml
# Backtesting Parameters
backtest_period: "90d"
timeframe: "5m"
starting_balance: 1000
fee: 0.001

# Strategy Constraints
max_open_trades: 3
stake_amount: "unlimited"
min_trades_required: 30  # Minimum trades for valid strategy

# Risk Management
max_drawdown_threshold: 0.5  # 50%
min_win_rate: 0.40  # 40%
```

## Performance Considerations

### Raspberry Pi Optimization
1. **Memory Management:**
   - Kleinere Populationen (50-100 statt 200+)
   - Strategien nicht alle gleichzeitig im RAM
   - Lazy Loading von Backtest-Daten

2. **CPU Optimization:**
   - Begrenzte Parallelität (2-4 Prozesse)
   - Längere Backtest-Zeiträume nachts
   - CPU-Throttling beachten

3. **Storage:**
   - SQLite statt großer In-Memory Structures
   - Regelmäßiges Cleanup alter Generationen
   - Komprimierung von Strategie-Code

4. **Networking:**
   - Caching von Exchange-Daten
   - Offline-Modus für Backtests
   - Rate Limiting für API-Calls

## Error Handling

### Common Issues:
1. **Invalid Strategy Code:** Syntax-Validierung vor Evaluation
2. **Backtest Failure:** Timeout und Retry-Mechanismus
3. **Insufficient Trades:** Markiere Strategie als ungültig
4. **Memory Issues:** Checkpoint und Resume
5. **File System Errors:** Robuste Fehlerbehandlung

## Monitoring & Logging

### Log Levels:
- **DEBUG:** Detaillierte Genetic Operations
- **INFO:** Generation Progress, Fitness Scores
- **WARNING:** Failed Backtests, Low Performance
- **ERROR:** System Errors, Critical Failures

### Metrics to Track:
- Generation Progress (current/total)
- Best Fitness Score
- Average Fitness Score
- Population Diversity
- Evaluation Time per Strategy
- Success/Failure Rates

## Extension Points

### 1. Custom Fitness Functions
```python
def custom_fitness(results: BacktestResults) -> float:
    # Implementiere eigene Fitness-Logik
    pass
```

### 2. Custom Genetic Operators
```python
def custom_mutation(strategy: Strategy) -> Strategy:
    # Implementiere eigene Mutation
    pass
```

### 3. LLM Integration
```python
def llm_generate_strategy(prompt: str) -> Strategy:
    # Nutze LLM zur Strategie-Generierung
    pass
```

### 4. FreqAI Integration
```python
def train_ml_model(strategies: List[Strategy]) -> Model:
    # Trainiere ML-Modell auf erfolgreichen Strategien
    pass
```

## Deployment Architecture

```
Raspberry Pi
├── GAFreqTrade Process
│   ├── Evolution Loop (Main Process)
│   ├── Backtest Workers (2-4 Processes)
│   └── Monitor Service
├── SQLite Database
│   ├── strategies.db
│   └── checkpoints/
├── Freqtrade
│   └── user_data/
│       ├── strategies/ (Generated)
│       └── backtest_results/
└── Logs
    ├── evolution.log
    ├── backtest.log
    └── monitor.log
```

---

**Next Steps:** Siehe TODO.md für Implementation-Schritte
