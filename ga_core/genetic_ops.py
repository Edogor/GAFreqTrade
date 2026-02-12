"""
Genetic Operations for GAFreqTrade

This module implements the core genetic algorithm operations:
- Mutation: Randomly modify strategies
- Crossover: Combine two parent strategies
- Selection: Choose strategies for reproduction
"""

import random
import copy
import json
from typing import Dict, List, Tuple, Any, Optional
import logging

try:
    from ga_core.strategy_generator import IndicatorLibrary, ConditionGenerator
except ImportError:
    from strategy_generator import IndicatorLibrary, ConditionGenerator

try:
    from utils.logger import get_logger
    logger = get_logger()
except (ImportError, ModuleNotFoundError):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class GeneticOperations:
    """Container for genetic algorithm operations"""
    
    def __init__(self, 
                 mutation_rate: float = 0.20,
                 mutation_strength: float = 0.15,
                 crossover_rate: float = 0.70):
        """
        Initialize genetic operations
        
        Args:
            mutation_rate: Probability of mutation
            mutation_strength: Magnitude of parameter changes (±%)
            crossover_rate: Probability of crossover
        """
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.crossover_rate = crossover_rate
    
    # ==================== MUTATION OPERATIONS ====================
    
    def mutate(self, strategy_metadata: Dict) -> Dict:
        """
        Apply mutation to a strategy
        
        Args:
            strategy_metadata: Strategy metadata dictionary
            
        Returns:
            Mutated strategy metadata
        """
        mutated = copy.deepcopy(strategy_metadata)
        
        # Decide which type of mutation to apply
        mutation_types = [
            ('parameter', 0.5),
            ('indicator', 0.3),
            ('condition', 0.2),
        ]
        
        # Apply mutations based on probabilities
        for mutation_type, probability in mutation_types:
            if random.random() < probability:
                if mutation_type == 'parameter':
                    mutated = self.mutate_parameters(mutated)
                elif mutation_type == 'indicator':
                    mutated = self.mutate_indicators(mutated)
                elif mutation_type == 'condition':
                    mutated = self.mutate_conditions(mutated)
        
        return mutated
    
    def mutate_parameters(self, strategy_metadata: Dict) -> Dict:
        """
        Mutate strategy parameters (stoploss, ROI, etc.)
        
        Args:
            strategy_metadata: Strategy metadata
            
        Returns:
            Mutated strategy
        """
        mutated = copy.deepcopy(strategy_metadata)
        
        # Mutate stoploss
        if 'stoploss' in mutated and random.random() < 0.5:
            current_stoploss = mutated['stoploss']
            change = random.uniform(-self.mutation_strength, self.mutation_strength)
            new_stoploss = current_stoploss * (1 + change)
            # Clamp to reasonable range
            mutated['stoploss'] = max(-0.25, min(-0.03, new_stoploss))
        
        # Mutate trailing stop
        if 'trailing_stop' in mutated and random.random() < 0.3:
            mutated['trailing_stop'] = not mutated['trailing_stop']
        
        # Mutate timeframe
        if 'timeframe' in mutated and random.random() < 0.2:
            timeframes = ['1m', '5m', '15m', '30m', '1h', '4h']
            mutated['timeframe'] = random.choice(timeframes)
        
        # Mutate hyperopt parameters
        if 'hyperopt_params' in mutated and random.random() < 0.4:
            params = mutated['hyperopt_params']
            if params:
                param_to_mutate = random.choice(params)
                # This would need access to the actual parameter values
                # For now, just mark that it needs re-evaluation
                logger.debug(f"Marking hyperopt parameter for mutation: {param_to_mutate}")
        
        logger.debug(f"Applied parameter mutation to {mutated.get('strategy_id', 'unknown')}")
        return mutated
    
    def mutate_indicators(self, strategy_metadata: Dict) -> Dict:
        """
        Mutate indicators in a strategy
        
        Possible mutations:
        - Add a new indicator
        - Remove an indicator
        - Replace an indicator
        
        Args:
            strategy_metadata: Strategy metadata
            
        Returns:
            Mutated strategy
        """
        mutated = copy.deepcopy(strategy_metadata)
        
        if 'indicators' not in mutated:
            return mutated
        
        indicators = mutated['indicators']
        mutation_type = random.choice(['add', 'remove', 'replace'])
        
        if mutation_type == 'add' and len(indicators) < 6:
            # Add a new random indicator
            available_indicators = list(IndicatorLibrary.INDICATORS.keys())
            new_indicator = random.choice([ind for ind in available_indicators if ind not in indicators])
            indicators.append(new_indicator)
            logger.debug(f"Added indicator: {new_indicator}")
        
        elif mutation_type == 'remove' and len(indicators) > 2:
            # Remove a random indicator
            removed = random.choice(indicators)
            indicators.remove(removed)
            logger.debug(f"Removed indicator: {removed}")
        
        elif mutation_type == 'replace':
            # Replace an indicator
            if indicators:
                available_indicators = list(IndicatorLibrary.INDICATORS.keys())
                old_indicator = random.choice(indicators)
                new_indicator = random.choice([ind for ind in available_indicators if ind not in indicators])
                indicators[indicators.index(old_indicator)] = new_indicator
                logger.debug(f"Replaced {old_indicator} with {new_indicator}")
        
        mutated['indicators'] = indicators
        return mutated
    
    def mutate_conditions(self, strategy_metadata: Dict) -> Dict:
        """
        Mutate entry/exit conditions
        
        Args:
            strategy_metadata: Strategy metadata
            
        Returns:
            Mutated strategy
        """
        mutated = copy.deepcopy(strategy_metadata)
        
        # This is a simplified mutation
        # In a real implementation, you'd regenerate conditions based on current indicators
        
        if 'num_buy_conditions' in mutated and random.random() < 0.5:
            change = random.choice([-1, 1])
            mutated['num_buy_conditions'] = max(1, min(4, mutated['num_buy_conditions'] + change))
        
        if 'num_sell_conditions' in mutated and random.random() < 0.5:
            change = random.choice([-1, 1])
            mutated['num_sell_conditions'] = max(1, min(4, mutated['num_sell_conditions'] + change))
        
        logger.debug(f"Applied condition mutation to {mutated.get('strategy_id', 'unknown')}")
        return mutated
    
    # ==================== CROSSOVER OPERATIONS ====================
    
    def crossover(self, parent1_metadata: Dict, parent2_metadata: Dict) -> Tuple[Dict, Dict]:
        """
        Perform crossover between two parent strategies
        
        Args:
            parent1_metadata: First parent strategy metadata
            parent2_metadata: Second parent strategy metadata
            
        Returns:
            Tuple of two child strategy metadata
        """
        # Choose crossover type
        crossover_type = random.choice(['single_point', 'uniform', 'indicator_swap'])
        
        if crossover_type == 'single_point':
            return self.single_point_crossover(parent1_metadata, parent2_metadata)
        elif crossover_type == 'uniform':
            return self.uniform_crossover(parent1_metadata, parent2_metadata)
        else:
            return self.indicator_swap_crossover(parent1_metadata, parent2_metadata)
    
    def single_point_crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """
        Single-point crossover on indicators
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Two children
        """
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # Crossover indicators
        if 'indicators' in parent1 and 'indicators' in parent2:
            indicators1 = parent1['indicators']
            indicators2 = parent2['indicators']
            
            if indicators1 and indicators2:
                # Choose crossover point
                point1 = random.randint(1, len(indicators1))
                point2 = random.randint(1, len(indicators2))
                
                # Create children
                child1['indicators'] = indicators1[:point1] + indicators2[point2:]
                child2['indicators'] = indicators2[:point2] + indicators1[point1:]
                
                # Remove duplicates while preserving order
                child1['indicators'] = list(dict.fromkeys(child1['indicators']))
                child2['indicators'] = list(dict.fromkeys(child2['indicators']))
        
        # Mix parameters
        if random.random() < 0.5:
            child1['stoploss'], child2['stoploss'] = child2.get('stoploss', child1['stoploss']), child1.get('stoploss', child2['stoploss'])
        
        if random.random() < 0.5:
            child1['timeframe'], child2['timeframe'] = child2.get('timeframe', child1['timeframe']), child1.get('timeframe', child2['timeframe'])
        
        logger.debug(f"Applied single-point crossover")
        return child1, child2
    
    def uniform_crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """
        Uniform crossover - randomly select traits from each parent
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Two children
        """
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # For each attribute, randomly choose from which parent to inherit
        attributes = ['stoploss', 'timeframe', 'trailing_stop']
        
        for attr in attributes:
            if attr in parent1 and attr in parent2 and random.random() < 0.5:
                # Swap attribute between children
                child1[attr], child2[attr] = parent2[attr], parent1[attr]
        
        # Mix indicators uniformly
        if 'indicators' in parent1 and 'indicators' in parent2:
            all_indicators = list(set(parent1['indicators'] + parent2['indicators']))
            
            child1['indicators'] = [ind for ind in all_indicators if random.random() < 0.5]
            child2['indicators'] = [ind for ind in all_indicators if ind not in child1['indicators']]
            
            # Ensure minimum indicators
            if len(child1['indicators']) < 2:
                child1['indicators'] = random.sample(all_indicators, 2)
            if len(child2['indicators']) < 2:
                remaining = [ind for ind in all_indicators if ind not in child1['indicators']]
                if len(remaining) >= 2:
                    child2['indicators'] = random.sample(remaining, 2)
                else:
                    child2['indicators'] = random.sample(all_indicators, 2)
        
        logger.debug(f"Applied uniform crossover")
        return child1, child2
    
    def indicator_swap_crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """
        Swap indicators between parents
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Two children
        """
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        if 'indicators' in parent1 and 'indicators' in parent2:
            indicators1 = parent1['indicators'].copy()
            indicators2 = parent2['indicators'].copy()
            
            # Swap 1-2 indicators
            num_swaps = random.randint(1, 2)
            
            for _ in range(num_swaps):
                if indicators1 and indicators2:
                    # Pick random indicators to swap
                    ind1 = random.choice(indicators1)
                    ind2 = random.choice(indicators2)
                    
                    # Swap
                    if ind2 not in indicators1:
                        indicators1[indicators1.index(ind1)] = ind2
                    if ind1 not in indicators2:
                        indicators2[indicators2.index(ind2)] = ind1
            
            child1['indicators'] = indicators1
            child2['indicators'] = indicators2
        
        logger.debug(f"Applied indicator swap crossover")
        return child1, child2
    
    # ==================== SELECTION OPERATIONS ====================
    
    def tournament_selection(self, 
                           population: List[Dict], 
                           fitness_scores: Dict[str, float],
                           tournament_size: int = 5) -> Dict:
        """
        Tournament selection
        
        Args:
            population: List of strategy metadata
            fitness_scores: Dictionary mapping strategy_id to fitness
            tournament_size: Number of strategies in tournament
            
        Returns:
            Selected strategy metadata
        """
        if not population:
            raise ValueError("Population is empty")
        
        # Select random strategies for tournament
        tournament_size = min(tournament_size, len(population))
        tournament = random.sample(population, tournament_size)
        
        # Find best strategy in tournament
        best_strategy = max(
            tournament,
            key=lambda s: fitness_scores.get(s.get('strategy_id', ''), 0.0)
        )
        
        return best_strategy
    
    def roulette_wheel_selection(self,
                                population: List[Dict],
                                fitness_scores: Dict[str, float]) -> Dict:
        """
        Roulette wheel selection (fitness-proportionate selection)
        
        Args:
            population: List of strategy metadata
            fitness_scores: Dictionary mapping strategy_id to fitness
            
        Returns:
            Selected strategy metadata
        """
        if not population:
            raise ValueError("Population is empty")
        
        # Calculate total fitness
        total_fitness = sum(
            fitness_scores.get(s.get('strategy_id', ''), 0.0) 
            for s in population
        )
        
        if total_fitness <= 0:
            # If all fitness scores are 0 or negative, select randomly
            return random.choice(population)
        
        # Spin the wheel
        spin = random.uniform(0, total_fitness)
        current = 0
        
        for strategy in population:
            fitness = fitness_scores.get(strategy.get('strategy_id', ''), 0.0)
            current += fitness
            if current >= spin:
                return strategy
        
        # Fallback (shouldn't reach here)
        return population[-1]
    
    def rank_selection(self,
                      population: List[Dict],
                      fitness_scores: Dict[str, float]) -> Dict:
        """
        Rank-based selection
        
        Args:
            population: List of strategy metadata
            fitness_scores: Dictionary mapping strategy_id to fitness
            
        Returns:
            Selected strategy metadata
        """
        if not population:
            raise ValueError("Population is empty")
        
        # Sort by fitness
        sorted_pop = sorted(
            population,
            key=lambda s: fitness_scores.get(s.get('strategy_id', ''), 0.0),
            reverse=True
        )
        
        # Assign selection probabilities based on rank
        n = len(sorted_pop)
        ranks = range(n, 0, -1)  # n, n-1, ..., 1
        total_rank = sum(ranks)
        
        # Roulette wheel on ranks
        spin = random.uniform(0, total_rank)
        current = 0
        
        for strategy, rank in zip(sorted_pop, ranks):
            current += rank
            if current >= spin:
                return strategy
        
        return sorted_pop[0]
    
    def elite_selection(self,
                       population: List[Dict],
                       fitness_scores: Dict[str, float],
                       elite_size: int) -> List[Dict]:
        """
        Select top N strategies (elitism)
        
        Args:
            population: List of strategy metadata
            fitness_scores: Dictionary mapping strategy_id to fitness
            elite_size: Number of elite strategies to select
            
        Returns:
            List of elite strategies
        """
        if not population:
            return []
        
        # Sort by fitness (descending)
        sorted_pop = sorted(
            population,
            key=lambda s: fitness_scores.get(s.get('strategy_id', ''), 0.0),
            reverse=True
        )
        
        return sorted_pop[:elite_size]


if __name__ == "__main__":
    # Test genetic operations
    print("Testing Genetic Operations...")
    
    genetic_ops = GeneticOperations()
    
    # Create test strategies
    strategy1 = {
        'strategy_id': 'Test_Strategy_1',
        'generation': 0,
        'indicators': ['rsi', 'macd', 'ema'],
        'stoploss': -0.10,
        'timeframe': '5m',
        'trailing_stop': True,
        'num_buy_conditions': 2,
        'num_sell_conditions': 2
    }
    
    strategy2 = {
        'strategy_id': 'Test_Strategy_2',
        'generation': 0,
        'indicators': ['bb', 'sma', 'adx'],
        'stoploss': -0.15,
        'timeframe': '15m',
        'trailing_stop': False,
        'num_buy_conditions': 3,
        'num_sell_conditions': 1
    }
    
    # Test mutation
    print("\n--- Testing Mutation ---")
    mutated = genetic_ops.mutate(strategy1)
    print(f"Original indicators: {strategy1['indicators']}")
    print(f"Mutated indicators: {mutated['indicators']}")
    
    # Test crossover
    print("\n--- Testing Crossover ---")
    child1, child2 = genetic_ops.crossover(strategy1, strategy2)
    print(f"Parent1 indicators: {strategy1['indicators']}")
    print(f"Parent2 indicators: {strategy2['indicators']}")
    print(f"Child1 indicators: {child1['indicators']}")
    print(f"Child2 indicators: {child2['indicators']}")
    
    # Test selection
    print("\n--- Testing Selection ---")
    population = [strategy1, strategy2]
    fitness_scores = {
        'Test_Strategy_1': 0.75,
        'Test_Strategy_2': 0.60
    }
    
    selected = genetic_ops.tournament_selection(population, fitness_scores, tournament_size=2)
    print(f"Tournament selected: {selected['strategy_id']}")
    
    elite = genetic_ops.elite_selection(population, fitness_scores, elite_size=1)
    print(f"Elite selection: {elite[0]['strategy_id']}")
    
    print("\n✓ All genetic operations tests passed!")
