"""
Leaderboard - Track and display top performing strategies.
"""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime


class Leaderboard:
    """Manages top performing strategies."""
    
    def __init__(self, db=None):
        """
        Initialize leaderboard.
        
        Args:
            db: Optional StrategyDB instance
        """
        self.db = db
        self.hall_of_fame: List[Dict[str, Any]] = []
    
    def update(self, strategies: List[Dict[str, Any]]):
        """
        Update leaderboard with new strategies.
        
        Args:
            strategies: List of strategy dictionaries with fitness scores
        """
        # Add new strategies
        for strategy in strategies:
            if strategy not in self.hall_of_fame:
                self.hall_of_fame.append(strategy)
        
        # Sort by fitness
        self.hall_of_fame.sort(key=lambda x: x.get('fitness', 0), reverse=True)
        
        # Keep only top 100
        self.hall_of_fame = self.hall_of_fame[:100]
    
    def get_top(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N strategies.
        
        Args:
            n: Number of strategies to return
            
        Returns:
            List of top strategies
        """
        if self.db:
            return self.db.get_top_strategies(n)
        return self.hall_of_fame[:n]
    
    def display(self, n: int = 10):
        """
        Display top N strategies.
        
        Args:
            n: Number of strategies to display
        """
        top = self.get_top(n)
        
        print("\n" + "=" * 80)
        print(f"TOP {n} STRATEGIES - LEADERBOARD")
        print("=" * 80)
        
        for i, strategy in enumerate(top, 1):
            print(f"\n{i}. {strategy.get('name', 'Unknown')}")
            print(f"   Fitness: {strategy.get('fitness', 0):.4f}")
            profit = strategy.get('profit') or 0
            print(f"   Profit: {profit:.2f}%")
            print(f"   Generation: {strategy.get('generation', 0)}")
            indicators = strategy.get('indicators', [])
            if isinstance(indicators, list) and indicators:
                print(f"   Indicators: {', '.join(indicators)}")
            
        print("\n" + "=" * 80)
    
    def export_to_file(self, filename: str = "leaderboard.txt"):
        """
        Export leaderboard to file.
        
        Args:
            filename: Output filename
        """
        output_path = Path(filename)
        
        with open(output_path, 'w') as f:
            f.write(f"GAFreqTrade Leaderboard\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            top = self.get_top(50)  # Export top 50
            
            for i, strategy in enumerate(top, 1):
                f.write(f"{i}. {strategy.get('name', 'Unknown')}\n")
                f.write(f"   Fitness: {strategy.get('fitness', 0):.4f}\n")
                f.write(f"   Profit: {strategy.get('profit', 0):.2f}%\n")
                f.write(f"   Generation: {strategy.get('generation', 0)}\n")
                
                indicators = strategy.get('indicators', [])
                if isinstance(indicators, list):
                    f.write(f"   Indicators: {', '.join(indicators)}\n")
                f.write("\n")
        
        print(f"Leaderboard exported to {output_path}")
    
    def get_hall_of_fame_dir(self) -> Path:
        """Get hall of fame directory path."""
        return Path("strategies/hall_of_fame")
    
    def save_hall_of_fame_strategies(self, n: int = 10):
        """
        Copy top strategies to hall of fame directory.
        
        Args:
            n: Number of strategies to save
        """
        hof_dir = self.get_hall_of_fame_dir()
        hof_dir.mkdir(parents=True, exist_ok=True)
        
        top = self.get_top(n)
        
        print(f"\nSaving top {n} strategies to Hall of Fame...")
        
        for strategy in top:
            name = strategy.get('name', 'Unknown')
            # Copy strategy file if it exists
            strategy_file = Path(f"strategies/generated/Strategy_{name}.py")
            if strategy_file.exists():
                dest_file = hof_dir / strategy_file.name
                dest_file.write_text(strategy_file.read_text())
                print(f"  Saved {name} (Fitness: {strategy.get('fitness', 0):.4f})")
        
        print(f"Hall of Fame updated in {hof_dir}/")
