# GAFreqTrade - Quick Start Guide

## Overview

GAFreqTrade is a Genetic Algorithm system that automatically generates and optimizes trading strategies for Freqtrade. It uses evolutionary algorithms to discover profitable trading strategies through generations of mutation, crossover, and selection.

## Prerequisites

1. Python 3.9+
2. Freqtrade installed (optional for mock testing)
3. Required packages: `pip install -r requirements.txt`

## Quick Start

### 1. Basic Test Run (Mock Mode)

Run a quick test evolution without real backtesting:

```bash
python run_evolution.py --generations 5 --population 10
```

This will:
- Generate 10 random strategies
- Evaluate them using mock fitness scores
- Evolve for 5 generations
- Save results in `strategies/generated/` and `checkpoints/`

### 2. Real Backtesting

Once you have Freqtrade configured with historical data:

```bash
python run_evolution.py --no-mock --generations 20 --population 50
```

This will use real Freqtrade backtesting to evaluate strategies.

### 3. Resume from Checkpoint

If evolution was interrupted, resume from the last checkpoint:

```bash
python run_evolution.py --resume checkpoints/population_gen_0010.pkl
```

### 4. Custom Configuration

Create your own config and use it:

```bash
python run_evolution.py --config config/ga_config.yaml --generations 100
```

## Command Line Options

```
--config CONFIG              Path to configuration file
--population POPULATION      Population size
--generations GENERATIONS    Number of generations
--elite ELITE               Elite size (preserved best strategies)
--resume CHECKPOINT         Resume from checkpoint file
--no-mock                   Use real Freqtrade backtesting
--checkpoint-interval N     Save checkpoint every N generations
--log-level LEVEL           Logging level (DEBUG|INFO|WARNING|ERROR)
--quiet                     Suppress output
```

## Understanding the Output

### During Evolution

```
GENERATION 5
============================================================
Evaluating generation 5...
Evaluating Gen005_Strat_001...
  Fitness: 0.6445, Profit: 15.23%
...

Top 5 Strategies:
  1. Gen005_Strat_012: Fitness=0.7234
  2. Gen004_Strat_007: Fitness=0.7021
  ...
```

### Final Results

```
FINAL TOP 10 STRATEGIES:
  1. Gen050_Strat_034
     Fitness: 0.8123
     Indicators: rsi, macd, bb, ema

EVOLUTION TREND:
  Gen 0: Best=0.6800, Avg=0.4885, Profit=29.86%
  Gen 10: Best=0.7234, Avg=0.6012, Profit=35.42%
  ...
```

## Understanding Fitness Scores

Fitness is calculated from multiple metrics:
- **Profit** (30%): Total profit percentage
- **Sharpe Ratio** (10%): Risk-adjusted returns
- **Drawdown** (25%): Maximum drawdown (lower is better)
- **Win Rate** (15%): Percentage of winning trades
- **Stability** (15%): Consistency metrics
- **Trade Count** (5%): Penalty for too few/many trades

Fitness scores range from 0.0 (worst) to 1.0 (best).

## Generated Strategies

Generated strategies are saved in `strategies/generated/`:

```
strategies/generated/
├── Strategy_Gen000_Strat_001.py
├── Strategy_Gen000_Strat_002.py
├── ...
└── Strategy_Gen050_Strat_100.py
```

Each strategy is a complete Freqtrade strategy that can be:
1. Backtested independently
2. Hyperoptimized with Freqtrade
3. Used for live trading (after thorough validation)

## Checkpoints

Checkpoints are saved in `checkpoints/`:

```
checkpoints/
├── population_gen_0000.pkl  # Binary checkpoint
├── population_gen_0000.json # Human-readable summary
├── population_gen_0010.pkl
├── population_gen_0010.json
└── ...
```

The JSON files show:
- Generation statistics
- Top 10 strategies
- Genealogy information

## Configuration

Edit `config/ga_config.yaml` to customize:

```yaml
# Population Parameters
population_size: 100
elite_size: 10
generations: 1000

# Genetic Operators
mutation_rate: 0.20
crossover_rate: 0.70
tournament_size: 5

# Fitness Weights
fitness_weights:
  profit: 0.30
  sharpe: 0.10
  drawdown: 0.25
  winrate: 0.15
  stability: 0.20
  trade_penalty: 0.05
```

## Tips for Best Results

### 1. Population Size
- Small (10-20): Fast testing, may converge to local optima
- Medium (50-100): Good balance
- Large (200+): Explores more solutions, slower

### 2. Generations
- Quick test: 5-10 generations
- Real optimization: 50-100 generations
- Long-term: 500+ generations

### 3. Elite Size
- Should be ~5-10% of population
- Too small: May lose good strategies
- Too large: Reduces diversity

### 4. Mutation Rate
- Low (0.05-0.10): Conservative, slow evolution
- Medium (0.15-0.25): Balanced
- High (0.30+): Aggressive, high diversity

## Example Workflows

### Development/Testing
```bash
# Quick test with mock data
python run_evolution.py --generations 5 --population 10
```

### Initial Optimization
```bash
# First real run with moderate population
python run_evolution.py --no-mock --generations 50 --population 50
```

### Long-term Evolution
```bash
# Extended run with larger population
python run_evolution.py --no-mock --generations 200 --population 100 \
  --checkpoint-interval 10
```

### Resume After Interruption
```bash
# Resume and continue for 50 more generations
python run_evolution.py --resume checkpoints/population_gen_0100.pkl \
  --generations 150
```

## Monitoring Progress

Watch the logs in real-time:
```bash
tail -f logs/evolution_*.log
```

Check checkpoints:
```bash
cat checkpoints/population_gen_0050.json | jq '.top_10'
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'freqtrade'"
- Install Freqtrade: `pip install freqtrade[all]`
- Or use mock mode: don't pass `--no-mock`

### "Backtest timed out"
- Increase timeout in config: `backtest_timeout: 600`
- Use shorter timeranges
- Reduce data size

### "Out of memory"
- Reduce population size: `--population 50`
- Reduce parallel backtests in config
- Use smaller timeranges

### Evolution not improving
- Increase mutation rate for more diversity
- Increase population size
- Run for more generations
- Adjust fitness weights to prioritize different metrics

## Next Steps

After running evolution:

1. **Analyze Results**: Review top strategies in checkpoints
2. **Manual Review**: Check generated strategies for logic
3. **Further Backtesting**: Test top strategies on different timeframes
4. **Hyperopt**: Fine-tune parameters with Freqtrade hyperopt
5. **Paper Trading**: Test in dry-run mode before live
6. **Live Trading**: Deploy only after thorough validation

## Advanced Usage

### Custom Fitness Weights
Prioritize low drawdown:
```yaml
fitness_weights:
  profit: 0.20
  sharpe: 0.10
  drawdown: 0.40  # Increased
  winrate: 0.15
  stability: 0.15
```

### Island Model (Future)
Run multiple populations in parallel and exchange strategies periodically.

### LLM Integration (Future)
Use AI to suggest indicator combinations and conditions.

## Support

For issues, questions, or contributions:
- Check the ARCHITECTURE.md for system design
- See IMPLEMENTATION_PLAN.md for development roadmap
- Review TODO.md for planned features

---

**Happy evolving! 🧬📈**
