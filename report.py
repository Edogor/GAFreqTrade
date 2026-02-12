#!/usr/bin/env python3
"""
Report Generator - Create detailed evolution reports.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from pathlib import Path
from datetime import datetime
from storage.strategy_db import StrategyDB


def generate_report(db: StrategyDB, output_file: str = None):
    """Generate evolution report."""
    
    generations = db.get_all_generations()
    top_strategies = db.get_top_strategies(20)
    
    # Generate report content
    lines = []
    lines.append("=" * 80)
    lines.append("GAFreqTrade Evolution Report")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    
    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Generations: {len(generations)}")
    
    if generations:
        best_gen = max(generations, key=lambda x: x['best_fitness'])
        latest_gen = generations[-1]
        
        lines.append(f"Latest Generation: {latest_gen['generation']}")
        lines.append(f"Best Overall Fitness: {best_gen['best_fitness']:.4f} (Gen {best_gen['generation']})")
        lines.append(f"Latest Fitness: {latest_gen['best_fitness']:.4f}")
        lines.append(f"Best Profit: {best_gen['best_profit']:.2f}%")
        lines.append("")
    
    # Generation details
    lines.append("GENERATION HISTORY")
    lines.append("-" * 80)
    lines.append(f"{'Gen':>4} | {'Best Fitness':>12} | {'Avg Fitness':>12} | {'Best Profit':>12}")
    lines.append("-" * 80)
    
    for gen in generations:
        lines.append(f"{gen['generation']:4d} | "
                    f"{gen['best_fitness']:12.4f} | "
                    f"{gen['avg_fitness']:12.4f} | "
                    f"{gen['best_profit']:11.2f}%")
    
    lines.append("")
    
    # Top strategies
    lines.append("TOP 20 STRATEGIES")
    lines.append("-" * 80)
    
    for i, strategy in enumerate(top_strategies, 1):
        lines.append(f"\n{i}. {strategy['name']}")
        lines.append(f"   Generation: {strategy['generation']}")
        lines.append(f"   Fitness: {strategy['fitness']:.4f}")
        lines.append(f"   Profit: {strategy['profit']:.2f}%")
        
        indicators = strategy.get('indicators', [])
        if isinstance(indicators, list):
            lines.append(f"   Indicators: {', '.join(indicators)}")
        
        metrics = strategy.get('metrics', {})
        if metrics:
            lines.append(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            lines.append(f"   Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
            lines.append(f"   Win Rate: {metrics.get('win_rate', 0):.2f}%")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("End of Report")
    lines.append("=" * 80)
    
    report_text = "\n".join(lines)
    
    # Output
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text)
        print(f"Report saved to {output_path}")
    else:
        print(report_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='GAFreqTrade Report Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--db',
        type=str,
        default='storage/strategies.db',
        help='Path to database file (default: storage/strategies.db)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: print to console)'
    )
    
    args = parser.parse_args()
    
    # Check if database exists
    if not Path(args.db).exists():
        print(f"Error: Database not found at {args.db}")
        print("Run evolution first to create strategies.")
        return 1
    
    # Load database
    db = StrategyDB(args.db)
    
    # Generate report
    generate_report(db, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
