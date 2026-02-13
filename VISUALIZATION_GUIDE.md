# GAFreqTrade Visualization Guide

## Overview

The GAFreqTrade visualization system provides comprehensive tools for monitoring and analyzing the genetic algorithm evolution process. This guide explains how to use the visualization features to gain insights into strategy evolution.

## Features

### 1. Fitness Evolution Plot
Tracks how fitness scores improve over generations.

**Features:**
- Best fitness per generation
- Average fitness per generation
- Optional population diversity overlay
- Trend analysis with moving averages

**Use Case:** Monitor overall evolution progress and identify convergence patterns.

### 2. Performance Comparison
Compares multiple performance metrics across top strategies.

**Metrics Displayed:**
- Total Profit (%)
- Sharpe Ratio
- Maximum Drawdown (%)
- Win Rate (%)

**Use Case:** Identify strengths and weaknesses across different strategies.

### 3. Population Diversity
Visualizes genetic diversity within the population over time.

**Features:**
- Diversity score tracking
- Rolling average for trend analysis
- Population size correlation
- Convergence detection

**Use Case:** Ensure the algorithm maintains sufficient diversity and doesn't converge prematurely.

### 4. Top Strategies Dashboard
Comprehensive overview of the best performing strategies.

**Components:**
- Fitness score rankings
- Profit distribution histogram
- Risk-return scatter plot (Sharpe vs Drawdown)
- Win rate distribution
- Trading activity analysis
- Generation distribution
- Summary statistics table

**Use Case:** Get a complete picture of top performers and identify patterns.

## Usage

### Method 1: Using visualize_evolution.py (Recommended)

The easiest way to generate visualizations:

```bash
# Generate all plots with default settings
python visualize_evolution.py

# Specify custom database and output directory
python visualize_evolution.py --db my_db.db --output my_plots

# Generate specific plots only
python visualize_evolution.py --fitness --dashboard

# Customize number of top strategies
python visualize_evolution.py --top-n 20

# Show diversity on fitness plot
python visualize_evolution.py --fitness --show-diversity
```

**Options:**
- `--db PATH`: Database file path (default: storage/strategies.db)
- `--output DIR`: Output directory for plots (default: plots)
- `--fitness`: Generate fitness evolution plot only
- `--performance`: Generate performance comparison only
- `--diversity`: Generate diversity plot only
- `--dashboard`: Generate dashboard only
- `--all`: Generate all plots (default if no specific plot selected)
- `--top-n N`: Number of top strategies to include (default: 10)
- `--show-diversity`: Show diversity on fitness plot

### Method 2: Using monitor.py

Generate plots while monitoring evolution:

```bash
# Display statistics and generate plots
python monitor.py --plot

# Specify custom output directory
python monitor.py --plot --output-dir custom_plots

# Live monitoring with periodic plot updates
python monitor.py --live --plot
```

### Method 3: Using report.py

Include visualizations in reports:

```bash
# Generate text report with plots
python report.py --with-plots

# Save report to file and generate plots
python report.py --output report.txt --with-plots --plot-dir results

# Plots will be organized in timestamped subdirectories
```

### Method 4: Using Python API

For custom integrations:

```python
from storage.strategy_db import StrategyDB
from utils.visualization import EvolutionVisualizer

# Initialize
db = StrategyDB("storage/strategies.db")
visualizer = EvolutionVisualizer(db, output_dir="plots")

# Generate specific plot
plot_path = visualizer.plot_fitness_over_generations(
    show_diversity=True
)

# Generate all plots
plots = visualizer.generate_all_plots()

# Customize plots
plot_path = visualizer.plot_performance_comparison(
    metrics=['profit', 'sharpe_ratio', 'win_rate'],
    top_n=20
)

# Create dashboard
dashboard_path = visualizer.create_top_strategies_dashboard(
    top_n=15
)
```

## Demo and Examples

### Running the Demo

Test the visualization system with sample data:

```bash
python demo_visualization.py
```

This creates:
- Sample database with 25 generations
- 10 strategies per generation
- Simulated evolution with improving fitness
- All 4 visualization types in `plots/demo/`

### Example Output

After running the demo or visualizing real data, you'll find:

```
plots/
├── demo/
│   ├── fitness_evolution_YYYYMMDD_HHMMSS.png
│   ├── performance_comparison_YYYYMMDD_HHMMSS.png
│   ├── population_diversity_YYYYMMDD_HHMMSS.png
│   └── dashboard_YYYYMMDD_HHMMSS.png
└── report_YYYYMMDD_HHMMSS/
    ├── fitness_evolution.png
    ├── performance_comparison.png
    ├── population_diversity.png
    └── dashboard.png
```

## Interpreting Visualizations

### Fitness Evolution Plot

**Healthy Evolution:**
- Best fitness: Steady upward trend
- Average fitness: Following best fitness with some lag
- Diversity: Gradually decreasing but not to zero

**Warning Signs:**
- Flat lines: Population converged, no improvement
- High diversity with no fitness improvement: Random search, not evolution
- Sudden fitness drops: Possible bug or data issue

### Performance Comparison

**What to Look For:**
- Balance across metrics (avoid single-metric optimization)
- Consistent performers (good across multiple metrics)
- Trade-offs (high profit with higher drawdown is acceptable if intentional)

### Population Diversity

**Optimal Patterns:**
- High diversity at start (exploration)
- Gradual decrease (exploitation)
- Never reaching zero (avoiding premature convergence)

**Problems:**
- Rapid diversity loss: Increase mutation rate
- No diversity loss: Increase selection pressure

### Dashboard

**Key Insights:**
- Generation distribution: Are recent generations producing better strategies?
- Risk-return scatter: Identify Pareto-optimal strategies
- Profit vs Win Rate: High win rate doesn't guarantee high profit
- Summary statistics: Quick overview of average performance

## Best Practices

### 1. Regular Monitoring

```bash
# Set up periodic visualization generation
*/10 * * * * cd /path/to/GAFreqTrade && python visualize_evolution.py
```

### 2. Comparative Analysis

Generate plots at different stages to compare:

```bash
# After 50 generations
python visualize_evolution.py --output plots/gen_050

# After 100 generations  
python visualize_evolution.py --output plots/gen_100

# Compare side-by-side to assess progress
```

### 3. Custom Metrics

Extend the visualizer for your specific needs:

```python
class CustomVisualizer(EvolutionVisualizer):
    def plot_custom_metric(self, metric_name):
        # Your custom visualization logic
        pass
```

### 4. Export for Presentation

Plots are high-resolution (150 DPI) PNG files suitable for:
- Reports and documentation
- Presentations
- Academic papers
- Blog posts

## Troubleshooting

### No Data Available

**Error:** "No generation data available"

**Solution:** Run evolution first to generate data:
```bash
python run_evolution.py
```

### Import Errors

**Error:** "ModuleNotFoundError: No module named 'matplotlib'"

**Solution:** Install required dependencies:
```bash
pip install -r requirements.txt
```

### Database Not Found

**Error:** "Database not found at storage/strategies.db"

**Solution:** Check database path or create it:
```bash
# Check if database exists
ls -l storage/strategies.db

# If not, run evolution
python run_evolution.py
```

### Empty Plots

**Issue:** Plots are generated but show no data

**Cause:** Database exists but has no data

**Solution:** 
1. Run evolution to populate database
2. Check that evolution is saving data correctly
3. Verify database has data: `sqlite3 storage/strategies.db "SELECT COUNT(*) FROM generations;"`

## Advanced Usage

### Batch Processing

Generate plots for multiple databases:

```bash
for db in storage/*.db; do
    python visualize_evolution.py --db "$db" --output "plots/$(basename $db .db)"
done
```

### Automation

Integrate into evolution loop:

```python
from orchestration.evolution_loop import EvolutionLoop
from utils.visualization import EvolutionVisualizer

loop = EvolutionLoop(config)
visualizer = EvolutionVisualizer(loop.db, "plots")

# Generate plots every 10 generations
if loop.generation % 10 == 0:
    visualizer.generate_all_plots(
        output_subdir=f"gen_{loop.generation:04d}"
    )
```

### Integration with Other Tools

Export data for external analysis:

```python
import pandas as pd

# Get data from database
generations = db.get_generations_stats()
df = pd.DataFrame(generations)

# Export to CSV for Excel, R, etc.
df.to_csv('evolution_data.csv', index=False)
```

## Performance Considerations

### Large Datasets

For evolution runs with hundreds of generations:

1. **Generate plots less frequently**
   ```python
   # Only every 25 generations
   if generation % 25 == 0:
       visualizer.generate_all_plots()
   ```

2. **Limit data points**
   ```python
   # Show only last 100 generations
   recent_generations = generations[-100:]
   ```

3. **Use sampling**
   ```python
   # Sample every 5th generation for very long runs
   df_sampled = df[::5]
   ```

### Memory Usage

- Plots are generated one at a time and closed immediately
- Non-interactive backend (Agg) is used to save memory
- Database queries are optimized with row_factory

## Future Enhancements

Planned features:
- [ ] Interactive plots with Plotly
- [ ] Web-based dashboard
- [ ] Real-time streaming updates
- [ ] Comparison mode (multiple runs)
- [ ] Animation of evolution process
- [ ] Export to video format
- [ ] Integration with TensorBoard

## Support

For issues or questions:
1. Check this guide
2. Review the demo: `python demo_visualization.py`
3. Check unit tests: `tests/unit/test_visualization.py`
4. Open an issue on GitHub

## Related Documentation

- [README.md](README.md) - Project overview
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - General usage
- [TODO.md](TODO.md) - Development progress
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
