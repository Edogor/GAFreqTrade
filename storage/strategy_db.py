"""
Strategy Database - SQLite storage for strategies and results.

This module provides database functionality for storing strategies,
their performance metrics, and tracking evolution history.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class StrategyDB:
    """Database manager for strategies and results."""
    
    def __init__(self, db_path: str = "storage/strategies.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Strategies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    generation INTEGER NOT NULL,
                    parent1 TEXT,
                    parent2 TEXT,
                    indicators TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    fitness REAL NOT NULL,
                    profit REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    win_rate REAL,
                    total_trades INTEGER,
                    avg_trade REAL,
                    metrics TEXT,
                    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_name) REFERENCES strategies(name)
                )
            """)
            
            # Generations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generations (
                    generation INTEGER PRIMARY KEY,
                    best_fitness REAL,
                    avg_fitness REAL,
                    best_profit REAL,
                    population_size INTEGER,
                    diversity REAL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def save_strategy(self, strategy: Dict[str, Any]) -> bool:
        """
        Save strategy to database.
        
        Args:
            strategy: Strategy dictionary with metadata
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO strategies 
                    (name, generation, parent1, parent2, indicators, parameters, code)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    strategy['name'],
                    strategy.get('generation', 0),
                    strategy.get('parent1'),
                    strategy.get('parent2'),
                    json.dumps(strategy.get('indicators', [])),
                    json.dumps(strategy.get('parameters', {})),
                    strategy.get('code', '')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving strategy: {e}")
            return False
    
    def save_result(self, strategy_name: str, generation: int, 
                   fitness: float, metrics: Dict[str, Any]) -> bool:
        """
        Save evaluation result.
        
        Args:
            strategy_name: Name of strategy
            generation: Generation number
            fitness: Fitness score
            metrics: Performance metrics dictionary
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO results 
                    (strategy_name, generation, fitness, profit, sharpe_ratio, 
                     max_drawdown, win_rate, total_trades, avg_trade, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    strategy_name,
                    generation,
                    fitness,
                    metrics.get('total_profit_pct'),  # Changed from 'profit'
                    metrics.get('sharpe_ratio'),
                    metrics.get('max_drawdown'),
                    metrics.get('win_rate'),
                    metrics.get('trades_count') or metrics.get('total_trades'),
                    metrics.get('avg_trade'),
                    json.dumps(metrics)
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving result: {e}")
            return False
    
    def save_generation(self, generation: int, stats: Dict[str, Any]) -> bool:
        """
        Save generation statistics.
        
        Args:
            generation: Generation number
            stats: Statistics dictionary
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO generations 
                    (generation, best_fitness, avg_fitness, best_profit, 
                     population_size, diversity)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    generation,
                    stats.get('best_fitness'),
                    stats.get('avg_fitness'),
                    stats.get('best_profit'),
                    stats.get('population_size'),
                    stats.get('diversity')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving generation: {e}")
            return False
    
    def get_top_strategies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N strategies by fitness.
        
        Args:
            limit: Number of strategies to return
            
        Returns:
            List of strategy dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Query results directly since strategies may not be fully populated
                cursor.execute("""
                    SELECT strategy_name, generation, fitness, profit, 
                           sharpe_ratio, max_drawdown, win_rate, total_trades, metrics
                    FROM results
                    ORDER BY fitness DESC
                    LIMIT ?
                """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    metrics = json.loads(row['metrics']) if row['metrics'] else {}
                    results.append({
                        'strategy_name': row['strategy_name'],
                        'generation': row['generation'],
                        'fitness': row['fitness'],
                        'profit': row['profit'],
                        'sharpe_ratio': row['sharpe_ratio'],
                        'max_drawdown': row['max_drawdown'],
                        'win_rate': row['win_rate'],
                        'total_trades': row['total_trades'],
                        'metrics': metrics
                    })
                
                return results
        except Exception as e:
            print(f"Error getting top strategies: {e}")
            return []
    
    def get_generation_stats(self, generation: int) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific generation.
        
        Args:
            generation: Generation number
            
        Returns:
            Statistics dictionary or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT best_fitness, avg_fitness, best_profit, 
                           population_size, diversity, completed_at
                    FROM generations
                    WHERE generation = ?
                """, (generation,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'best_fitness': row[0],
                        'avg_fitness': row[1],
                        'best_profit': row[2],
                        'population_size': row[3],
                        'diversity': row[4],
                        'completed_at': row[5]
                    }
                return None
        except Exception as e:
            print(f"Error getting generation stats: {e}")
            return None
    
    def get_all_generations(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all generations.
        
        Returns:
            List of generation statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT generation, best_fitness, avg_fitness, best_profit
                    FROM generations
                    ORDER BY generation
                """)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'generation': row[0],
                        'best_fitness': row[1],
                        'avg_fitness': row[2],
                        'best_profit': row[3]
                    })
                
                return results
        except Exception as e:
            print(f"Error getting all generations: {e}")
            return []
    
    def get_generations_stats(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive statistics for all generations.
        
        Returns:
            List of generation statistics with all fields
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT generation, best_fitness, avg_fitness, best_profit,
                           population_size, diversity, completed_at
                    FROM generations
                    ORDER BY generation
                """)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'generation': row['generation'],
                        'best_fitness': row['best_fitness'],
                        'avg_fitness': row['avg_fitness'],
                        'best_profit': row['best_profit'],
                        'population_size': row['population_size'],
                        'diversity': row['diversity'],
                        'completed_at': row['completed_at']
                    })
                
                return results
        except Exception as e:
            print(f"Error getting generations stats: {e}")
            return []
