"""
Visualization Module for GAFreqTrade

This module provides visualization tools for monitoring and analyzing
the genetic algorithm evolution process, including:
- Fitness progression over generations
- Performance metric comparisons
- Population diversity tracking
- Top strategies dashboard
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import logging

try:
    from storage.strategy_db import StrategyDB
    from storage.leaderboard import Leaderboard
except ImportError:
    StrategyDB = None
    Leaderboard = None

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

logger = logging.getLogger(__name__)


class EvolutionVisualizer:
    """Main visualization class for evolution tracking and analysis."""
    
    def __init__(self, db: Optional['StrategyDB'] = None, output_dir: str = "plots"):
        """
        Initialize visualizer.
        
        Args:
            db: StrategyDB instance for data access
            output_dir: Directory to save plots
        """
        self.db = db
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_fitness_over_generations(
        self,
        save_path: Optional[str] = None,
        show_best: bool = True,
        show_avg: bool = True,
        show_diversity: bool = False
    ) -> str:
        """
        Plot fitness evolution over generations.
        
        Args:
            save_path: Custom path to save plot, defaults to output_dir
            show_best: Show best fitness line
            show_avg: Show average fitness line
            show_diversity: Show population diversity on secondary axis
            
        Returns:
            Path to saved plot
        """
        if self.db is None:
            logger.warning("No database connection, cannot plot fitness")
            return None
        
        # Query generation statistics
        generations_data = self.db.get_generations_stats()
        
        if not generations_data:
            logger.warning("No generation data available")
            return None
        
        df = pd.DataFrame(generations_data)
        
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Plot fitness metrics
        if show_best and 'best_fitness' in df.columns:
            ax1.plot(df['generation'], df['best_fitness'], 
                    'g-', linewidth=2, label='Best Fitness', marker='o')
        
        if show_avg and 'avg_fitness' in df.columns:
            ax1.plot(df['generation'], df['avg_fitness'], 
                    'b--', linewidth=2, label='Average Fitness', marker='s')
        
        ax1.set_xlabel('Generation', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Fitness Score', fontsize=12, fontweight='bold')
        ax1.set_title('Fitness Evolution Over Generations', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Plot diversity on secondary axis if requested
        if show_diversity and 'diversity' in df.columns:
            ax2 = ax1.twinx()
            ax2.plot(df['generation'], df['diversity'], 
                    'r-.', linewidth=2, label='Population Diversity', marker='^', alpha=0.7)
            ax2.set_ylabel('Diversity Score', fontsize=12, fontweight='bold', color='r')
            ax2.tick_params(axis='y', labelcolor='r')
            ax2.legend(loc='upper right')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / f"fitness_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Fitness evolution plot saved to {save_path}")
        return str(save_path)
    
    def plot_performance_comparison(
        self,
        metrics: List[str] = None,
        top_n: int = 10,
        save_path: Optional[str] = None
    ) -> str:
        """
        Compare performance metrics across top strategies.
        
        Args:
            metrics: List of metrics to compare (profit, sharpe_ratio, max_drawdown, win_rate)
            top_n: Number of top strategies to include
            save_path: Custom path to save plot
            
        Returns:
            Path to saved plot
        """
        if self.db is None:
            logger.warning("No database connection, cannot plot performance comparison")
            return None
        
        if metrics is None:
            metrics = ['profit', 'sharpe_ratio', 'max_drawdown', 'win_rate']
        
        # Get top strategies
        top_strategies = self.db.get_top_strategies(limit=top_n)
        
        if not top_strategies:
            logger.warning("No strategy data available")
            return None
        
        # Prepare data
        df = pd.DataFrame(top_strategies)
        df['strategy_name'] = df['strategy_name'].str[:20]  # Truncate names
        
        # Create subplots
        n_metrics = len(metrics)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for idx, metric in enumerate(metrics[:4]):  # Max 4 metrics
            if metric in df.columns:
                ax = axes[idx]
                
                # Sort by metric
                df_sorted = df.sort_values(by=metric, ascending=(metric != 'max_drawdown'))
                
                # Create bar plot
                bars = ax.barh(df_sorted['strategy_name'], df_sorted[metric])
                
                # Color bars based on value
                colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(bars)))
                if metric == 'max_drawdown':
                    colors = colors[::-1]  # Reverse for drawdown (lower is better)
                
                for bar, color in zip(bars, colors):
                    bar.set_color(color)
                
                ax.set_xlabel(metric.replace('_', ' ').title(), fontsize=11, fontweight='bold')
                ax.set_ylabel('Strategy', fontsize=11, fontweight='bold')
                ax.set_title(f'Top {top_n} Strategies by {metric.replace("_", " ").title()}', 
                           fontsize=12, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)
        
        plt.suptitle('Performance Metrics Comparison', fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / f"performance_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Performance comparison plot saved to {save_path}")
        return str(save_path)
    
    def plot_population_diversity(
        self,
        window_size: int = 10,
        save_path: Optional[str] = None
    ) -> str:
        """
        Plot population diversity metrics over time.
        
        Args:
            window_size: Rolling window for smoothing
            save_path: Custom path to save plot
            
        Returns:
            Path to saved plot
        """
        if self.db is None:
            logger.warning("No database connection, cannot plot diversity")
            return None
        
        generations_data = self.db.get_generations_stats()
        
        if not generations_data:
            logger.warning("No generation data available")
            return None
        
        df = pd.DataFrame(generations_data)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Diversity over generations
        if 'diversity' in df.columns:
            ax1.plot(df['generation'], df['diversity'], 'b-', linewidth=2, label='Diversity', alpha=0.6)
            
            # Add rolling average
            if len(df) >= window_size:
                rolling_avg = df['diversity'].rolling(window=window_size).mean()
                ax1.plot(df['generation'], rolling_avg, 'r-', linewidth=2.5, 
                        label=f'{window_size}-Gen Moving Avg')
            
            ax1.set_xlabel('Generation', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Diversity Score', fontsize=12, fontweight='bold')
            ax1.set_title('Population Diversity Over Time', fontsize=14, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Plot 2: Population size and best fitness correlation
        if 'population_size' in df.columns and 'best_fitness' in df.columns:
            ax2_twin = ax2.twinx()
            
            ax2.bar(df['generation'], df['population_size'], alpha=0.3, label='Population Size', color='lightblue')
            ax2_twin.plot(df['generation'], df['best_fitness'], 'g-', linewidth=2, 
                         marker='o', label='Best Fitness', markersize=4)
            
            ax2.set_xlabel('Generation', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Population Size', fontsize=12, fontweight='bold')
            ax2_twin.set_ylabel('Best Fitness', fontsize=12, fontweight='bold', color='g')
            ax2.set_title('Population Size vs Best Fitness', fontsize=14, fontweight='bold')
            ax2.legend(loc='upper left')
            ax2_twin.legend(loc='upper right')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / f"population_diversity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Population diversity plot saved to {save_path}")
        return str(save_path)
    
    def create_top_strategies_dashboard(
        self,
        top_n: int = 10,
        save_path: Optional[str] = None
    ) -> str:
        """
        Create comprehensive dashboard for top strategies.
        
        Args:
            top_n: Number of top strategies to display
            save_path: Custom path to save plot
            
        Returns:
            Path to saved plot
        """
        if self.db is None:
            logger.warning("No database connection, cannot create dashboard")
            return None
        
        top_strategies = self.db.get_top_strategies(limit=top_n)
        
        if not top_strategies:
            logger.warning("No strategy data available")
            return None
        
        df = pd.DataFrame(top_strategies)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Fitness Scores
        ax1 = fig.add_subplot(gs[0, :2])
        df_sorted = df.sort_values('fitness', ascending=True)
        bars = ax1.barh(range(len(df_sorted)), df_sorted['fitness'])
        colors = plt.cm.viridis(np.linspace(0, 1, len(bars)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        ax1.set_yticks(range(len(df_sorted)))
        ax1.set_yticklabels([f"Gen{g}" for g in df_sorted['generation']])
        ax1.set_xlabel('Fitness Score', fontweight='bold')
        ax1.set_title(f'Top {top_n} Strategies - Fitness Scores', fontweight='bold', fontsize=12)
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. Profit Distribution
        ax2 = fig.add_subplot(gs[0, 2])
        if 'profit' in df.columns:
            ax2.hist(df['profit'], bins=15, color='green', alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Profit (%)', fontweight='bold')
            ax2.set_ylabel('Count', fontweight='bold')
            ax2.set_title('Profit Distribution', fontweight='bold', fontsize=11)
            ax2.grid(axis='y', alpha=0.3)
        
        # 3. Sharpe Ratio vs Max Drawdown
        ax3 = fig.add_subplot(gs[1, 0])
        if 'sharpe_ratio' in df.columns and 'max_drawdown' in df.columns:
            scatter = ax3.scatter(df['max_drawdown'], df['sharpe_ratio'], 
                                 c=df['fitness'], cmap='RdYlGn', s=100, alpha=0.7, edgecolors='black')
            ax3.set_xlabel('Max Drawdown (%)', fontweight='bold')
            ax3.set_ylabel('Sharpe Ratio', fontweight='bold')
            ax3.set_title('Risk-Return Profile', fontweight='bold', fontsize=11)
            ax3.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax3, label='Fitness')
        
        # 4. Win Rate Distribution
        ax4 = fig.add_subplot(gs[1, 1])
        if 'win_rate' in df.columns:
            ax4.hist(df['win_rate'], bins=15, color='blue', alpha=0.7, edgecolor='black')
            ax4.set_xlabel('Win Rate (%)', fontweight='bold')
            ax4.set_ylabel('Count', fontweight='bold')
            ax4.set_title('Win Rate Distribution', fontweight='bold', fontsize=11)
            ax4.axvline(df['win_rate'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
            ax4.legend()
            ax4.grid(axis='y', alpha=0.3)
        
        # 5. Trade Count
        ax5 = fig.add_subplot(gs[1, 2])
        if 'total_trades' in df.columns:
            ax5.hist(df['total_trades'], bins=15, color='orange', alpha=0.7, edgecolor='black')
            ax5.set_xlabel('Total Trades', fontweight='bold')
            ax5.set_ylabel('Count', fontweight='bold')
            ax5.set_title('Trading Activity', fontweight='bold', fontsize=11)
            ax5.grid(axis='y', alpha=0.3)
        
        # 6. Generation Distribution
        ax6 = fig.add_subplot(gs[2, 0])
        generation_counts = df['generation'].value_counts().sort_index()
        ax6.bar(generation_counts.index, generation_counts.values, color='purple', alpha=0.7)
        ax6.set_xlabel('Generation', fontweight='bold')
        ax6.set_ylabel('Count', fontweight='bold')
        ax6.set_title('Strategies by Generation', fontweight='bold', fontsize=11)
        ax6.grid(axis='y', alpha=0.3)
        
        # 7. Performance Metrics Table
        ax7 = fig.add_subplot(gs[2, 1:])
        ax7.axis('tight')
        ax7.axis('off')
        
        # Create summary statistics table
        summary_data = {
            'Metric': ['Avg Fitness', 'Avg Profit', 'Avg Sharpe', 'Avg Drawdown', 'Avg Win Rate'],
            'Value': [
                f"{df['fitness'].mean():.4f}",
                f"{df['profit'].mean():.2f}%" if 'profit' in df.columns else 'N/A',
                f"{df['sharpe_ratio'].mean():.3f}" if 'sharpe_ratio' in df.columns else 'N/A',
                f"{df['max_drawdown'].mean():.2f}%" if 'max_drawdown' in df.columns else 'N/A',
                f"{df['win_rate'].mean():.2f}%" if 'win_rate' in df.columns else 'N/A'
            ]
        }
        table = ax7.table(cellText=list(zip(summary_data['Metric'], summary_data['Value'])),
                         colLabels=['Metric', 'Value'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        
        plt.suptitle(f'Top {top_n} Strategies - Comprehensive Dashboard', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save_path is None:
            save_path = self.output_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Dashboard saved to {save_path}")
        return str(save_path)
    
    def plot_metric_evolution(
        self,
        metric: str = 'profit',
        top_n: int = 5,
        save_path: Optional[str] = None
    ) -> str:
        """
        Plot how a specific metric evolves for top strategies over generations.
        
        Args:
            metric: Metric to track (profit, sharpe_ratio, etc.)
            top_n: Number of top strategies to track
            save_path: Custom path to save plot
            
        Returns:
            Path to saved plot
        """
        if self.db is None:
            logger.warning("No database connection, cannot plot metric evolution")
            return None
        
        # This would require historical tracking of specific strategies across generations
        # For now, we'll plot the best metric per generation
        generations_data = self.db.get_generations_stats()
        
        if not generations_data:
            logger.warning("No generation data available")
            return None
        
        df = pd.DataFrame(generations_data)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        metric_col = f'best_{metric}'
        if metric_col in df.columns:
            ax.plot(df['generation'], df[metric_col], 'b-', linewidth=2, marker='o', label=f'Best {metric}')
            ax.fill_between(df['generation'], df[metric_col], alpha=0.3)
        
        ax.set_xlabel('Generation', fontsize=12, fontweight='bold')
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_title(f'{metric.replace("_", " ").title()} Evolution Over Generations', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = self.output_dir / f"{metric}_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Metric evolution plot saved to {save_path}")
        return str(save_path)
    
    def generate_all_plots(self, output_subdir: Optional[str] = None) -> Dict[str, str]:
        """
        Generate all available plots at once.
        
        Args:
            output_subdir: Optional subdirectory name within output_dir
            
        Returns:
            Dictionary mapping plot type to file path
        """
        if output_subdir:
            original_output_dir = self.output_dir
            self.output_dir = self.output_dir / output_subdir
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        plots = {}
        
        try:
            # Generate all plots
            logger.info("Generating fitness evolution plot...")
            plots['fitness_evolution'] = self.plot_fitness_over_generations(show_diversity=True)
            
            logger.info("Generating performance comparison...")
            plots['performance_comparison'] = self.plot_performance_comparison()
            
            logger.info("Generating population diversity plot...")
            plots['population_diversity'] = self.plot_population_diversity()
            
            logger.info("Generating top strategies dashboard...")
            plots['dashboard'] = self.create_top_strategies_dashboard()
            
            logger.info(f"All plots generated successfully in {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Error generating plots: {e}")
        
        finally:
            if output_subdir:
                self.output_dir = original_output_dir
        
        return plots


def create_quick_report(db_path: str = "storage/strategies.db", output_dir: str = "plots") -> Dict[str, str]:
    """
    Quick function to generate all visualization reports.
    
    Args:
        db_path: Path to strategy database
        output_dir: Directory to save plots
        
    Returns:
        Dictionary of generated plot paths
    """
    if StrategyDB is None:
        logger.error("StrategyDB not available, cannot create report")
        return {}
    
    db = StrategyDB(db_path)
    visualizer = EvolutionVisualizer(db, output_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plots = visualizer.generate_all_plots(output_subdir=f"report_{timestamp}")
    
    return plots


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    print("GAFreqTrade Visualization Module")
    print("=" * 50)
    
    # Create sample plots
    try:
        plots = create_quick_report()
        print("\nGenerated plots:")
        for plot_type, path in plots.items():
            if path:
                print(f"  - {plot_type}: {path}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This example requires a populated database to work.")
