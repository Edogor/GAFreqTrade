"""
Population Manager for GAFreqTrade

This module manages the population of trading strategies across generations.
"""

import os
import json
import pickle
import random
from typing import Dict, List, Optional
from datetime import datetime
import logging

try:
    from ga_core.strategy_generator import StrategyGenerator, generate_initial_population
    from ga_core.genetic_ops import GeneticOperations
except ImportError:
    from strategy_generator import StrategyGenerator, generate_initial_population
    from genetic_ops import GeneticOperations

try:
    from utils.logger import get_logger
    logger = get_logger()
except (ImportError, ModuleNotFoundError):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class Population:
    """
    Manages a population of trading strategies
    
    Tracks strategies, their fitness scores, and genealogy across generations.
    """
    
    def __init__(self, 
                 size: int = 100,
                 generation: int = 0,
                 output_dir: str = "strategies/generated"):
        """
        Initialize population
        
        Args:
            size: Population size
            generation: Current generation number
            output_dir: Directory for generated strategies
        """
        self.size = size
        self.generation = generation
        self.output_dir = output_dir
        
        self.strategies: List[Dict] = []
        self.fitness_scores: Dict[str, float] = {}
        self.genealogy: Dict[str, List[str]] = {}  # strategy_id -> [parent_ids]
        
        self.generator = StrategyGenerator(output_dir)
        self.genetic_ops = GeneticOperations()
    
    def initialize_random(self):
        """Create initial random population"""
        logger.info(f"Initializing random population of size {self.size}")
        
        self.strategies = generate_initial_population(
            population_size=self.size,
            output_dir=self.output_dir
        )
        
        # Initialize empty fitness scores
        for strategy in self.strategies:
            strategy_id = strategy['strategy_id']
            self.fitness_scores[strategy_id] = 0.0
            self.genealogy[strategy_id] = []  # No parents
        
        logger.info(f"Initialized {len(self.strategies)} random strategies")
    
    def add_strategy(self, strategy_metadata: Dict, fitness: float = 0.0, 
                    parents: Optional[List[str]] = None):
        """
        Add a strategy to the population
        
        Args:
            strategy_metadata: Strategy metadata
            fitness: Fitness score
            parents: List of parent strategy IDs
        """
        strategy_id = strategy_metadata['strategy_id']
        
        self.strategies.append(strategy_metadata)
        self.fitness_scores[strategy_id] = fitness
        self.genealogy[strategy_id] = parents if parents else []
    
    def update_fitness(self, strategy_id: str, fitness: float):
        """Update fitness score for a strategy"""
        self.fitness_scores[strategy_id] = fitness
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        """Get strategy by ID"""
        for strategy in self.strategies:
            if strategy['strategy_id'] == strategy_id:
                return strategy
        return None
    
    def get_top_n(self, n: int) -> List[Dict]:
        """
        Get top N strategies by fitness
        
        Args:
            n: Number of strategies to return
            
        Returns:
            List of top strategies
        """
        sorted_strategies = sorted(
            self.strategies,
            key=lambda s: self.fitness_scores.get(s['strategy_id'], 0.0),
            reverse=True
        )
        return sorted_strategies[:n]
    
    def get_statistics(self) -> Dict:
        """
        Get population statistics
        
        Returns:
            Dictionary with statistics
        """
        if not self.fitness_scores:
            return {
                'generation': self.generation,
                'size': len(self.strategies),
                'evaluated': 0
            }
        
        fitness_values = list(self.fitness_scores.values())
        
        return {
            'generation': self.generation,
            'size': len(self.strategies),
            'evaluated': len([f for f in fitness_values if f > 0]),
            'best_fitness': max(fitness_values) if fitness_values else 0.0,
            'avg_fitness': sum(fitness_values) / len(fitness_values) if fitness_values else 0.0,
            'worst_fitness': min(fitness_values) if fitness_values else 0.0,
        }
    
    def evolve_generation(self, 
                         elite_size: int = 10,
                         mutation_rate: float = 0.20,
                         crossover_rate: float = 0.70,
                         new_random_rate: float = 0.10,
                         tournament_size: int = 5) -> 'Population':
        """
        Create next generation through evolution
        
        Args:
            elite_size: Number of elite strategies to preserve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            new_random_rate: Rate of new random strategies
            tournament_size: Tournament size for selection
            
        Returns:
            New population
        """
        logger.info(f"Evolving generation {self.generation} -> {self.generation + 1}")
        
        new_population = Population(
            size=self.size,
            generation=self.generation + 1,
            output_dir=self.output_dir
        )
        
        # 1. Elitism - preserve best strategies
        elite = self.genetic_ops.elite_selection(
            self.strategies,
            self.fitness_scores,
            elite_size
        )
        
        for strategy in elite:
            new_strategy = strategy.copy()
            new_strategy['generation'] = self.generation + 1
            # Keep the same strategy_id for elite (or create a new one)
            new_population.add_strategy(
                new_strategy,
                fitness=self.fitness_scores[strategy['strategy_id']],
                parents=[strategy['strategy_id']]
            )
        
        logger.info(f"Preserved {len(elite)} elite strategies")
        
        # 2. Generate offspring
        num_offspring = self.size - elite_size
        num_new_random = int(num_offspring * new_random_rate)
        num_evolved = num_offspring - num_new_random
        
        offspring_count = 0
        
        # Create evolved offspring
        while offspring_count < num_evolved:
            # Selection
            parent1 = self.genetic_ops.tournament_selection(
                self.strategies,
                self.fitness_scores,
                tournament_size
            )
            parent2 = self.genetic_ops.tournament_selection(
                self.strategies,
                self.fitness_scores,
                tournament_size
            )
            
            # Crossover
            if random.random() < crossover_rate:
                child1_meta, child2_meta = self.genetic_ops.crossover(parent1, parent2)
            else:
                child1_meta = parent1.copy()
                child2_meta = parent2.copy()
            
            # Mutation
            if random.random() < mutation_rate:
                child1_meta = self.genetic_ops.mutate(child1_meta)
            if random.random() < mutation_rate:
                child2_meta = self.genetic_ops.mutate(child2_meta)
            
            # Generate actual strategy files for children
            for child_meta in [child1_meta, child2_meta]:
                if offspring_count >= num_evolved:
                    break
                
                # Generate new strategy based on metadata
                # This is simplified - in practice, you'd regenerate the strategy file
                new_strategy = self.generator.generate_random_strategy(
                    generation=self.generation + 1,
                    strategy_num=len(new_population.strategies) + 1
                )
                
                # Update with crossover/mutation results
                new_strategy['indicators'] = child_meta.get('indicators', new_strategy['indicators'])
                
                new_population.add_strategy(
                    new_strategy,
                    fitness=0.0,  # Will be evaluated
                    parents=[parent1['strategy_id'], parent2['strategy_id']]
                )
                
                offspring_count += 1
        
        logger.info(f"Created {offspring_count} evolved offspring")
        
        # 3. Add new random strategies (for diversity)
        for i in range(num_new_random):
            new_strategy = self.generator.generate_random_strategy(
                generation=self.generation + 1,
                strategy_num=len(new_population.strategies) + 1
            )
            new_population.add_strategy(
                new_strategy,
                fitness=0.0,
                parents=[]  # No parents
            )
        
        logger.info(f"Added {num_new_random} new random strategies")
        logger.info(f"New population size: {len(new_population.strategies)}")
        
        return new_population
    
    def save_checkpoint(self, checkpoint_dir: str = "checkpoints"):
        """
        Save population checkpoint
        
        Args:
            checkpoint_dir: Directory to save checkpoint
        """
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_file = os.path.join(
            checkpoint_dir,
            f"population_gen_{self.generation:04d}.pkl"
        )
        
        checkpoint_data = {
            'generation': self.generation,
            'size': self.size,
            'strategies': self.strategies,
            'fitness_scores': self.fitness_scores,
            'genealogy': self.genealogy,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        # Also save as JSON for human readability
        json_file = checkpoint_file.replace('.pkl', '.json')
        with open(json_file, 'w') as f:
            json.dump({
                'generation': self.generation,
                'size': self.size,
                'statistics': self.get_statistics(),
                'top_10': [
                    {
                        'strategy_id': s['strategy_id'],
                        'fitness': self.fitness_scores.get(s['strategy_id'], 0.0),
                        'indicators': s.get('indicators', []),
                        'parents': self.genealogy.get(s['strategy_id'], [])
                    }
                    for s in self.get_top_n(10)
                ],
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info(f"Saved checkpoint to {checkpoint_file}")
    
    @classmethod
    def load_checkpoint(cls, checkpoint_file: str, output_dir: str = "strategies/generated") -> 'Population':
        """
        Load population from checkpoint
        
        Args:
            checkpoint_file: Path to checkpoint file
            output_dir: Directory for generated strategies
            
        Returns:
            Loaded population
        """
        logger.info(f"Loading checkpoint from {checkpoint_file}")
        
        with open(checkpoint_file, 'rb') as f:
            checkpoint_data = pickle.load(f)
        
        population = cls(
            size=checkpoint_data['size'],
            generation=checkpoint_data['generation'],
            output_dir=output_dir
        )
        
        population.strategies = checkpoint_data['strategies']
        population.fitness_scores = checkpoint_data['fitness_scores']
        population.genealogy = checkpoint_data['genealogy']
        
        logger.info(f"Loaded population: generation {population.generation}, "
                   f"size {len(population.strategies)}")
        
        return population


if __name__ == "__main__":
    import random
    
    # Test population manager
    print("Testing Population Manager...")
    
    # Create initial population
    pop = Population(size=10, generation=0)
    pop.initialize_random()
    
    print(f"\nInitial population:")
    print(f"  Size: {len(pop.strategies)}")
    print(f"  Generation: {pop.generation}")
    
    # Assign random fitness scores
    print("\nAssigning random fitness scores...")
    for strategy in pop.strategies:
        fitness = random.uniform(0.3, 0.9)
        pop.update_fitness(strategy['strategy_id'], fitness)
    
    stats = pop.get_statistics()
    print(f"\nPopulation statistics:")
    print(f"  Best fitness: {stats['best_fitness']:.4f}")
    print(f"  Avg fitness: {stats['avg_fitness']:.4f}")
    print(f"  Worst fitness: {stats['worst_fitness']:.4f}")
    
    # Get top strategies
    top_3 = pop.get_top_n(3)
    print(f"\nTop 3 strategies:")
    for i, strategy in enumerate(top_3, 1):
        fitness = pop.fitness_scores[strategy['strategy_id']]
        print(f"  {i}. {strategy['strategy_id']}: {fitness:.4f}")
    
    # Save checkpoint
    print("\nSaving checkpoint...")
    pop.save_checkpoint()
    
    # Evolve to next generation
    print("\nEvolving to next generation...")
    next_pop = pop.evolve_generation(
        elite_size=2,
        mutation_rate=0.3,
        crossover_rate=0.7,
        new_random_rate=0.1,
        tournament_size=3
    )
    
    print(f"\nNew population:")
    print(f"  Size: {len(next_pop.strategies)}")
    print(f"  Generation: {next_pop.generation}")
    
    print("\n✓ Population manager tests passed!")
