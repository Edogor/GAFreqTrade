#!/usr/bin/env python3
"""
GAFreqTrade - Main Entry Point

Run genetic algorithm evolution to optimize trading strategies for Freqtrade.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from pathlib import Path

from orchestration.evolution_loop import run_evolution
from utils.logger import get_logger

logger = get_logger()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='GAFreqTrade - Genetic Algorithm for Freqtrade Strategy Optimization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run evolution with default settings (mock mode)
  python run_evolution.py
  
  # Run with custom config
  python run_evolution.py --config config/ga_config.yaml
  
  # Run with real backtesting
  python run_evolution.py --no-mock --generations 50
  
  # Resume from checkpoint
  python run_evolution.py --resume checkpoints/population_gen_0010.pkl
  
  # Quick test run
  python run_evolution.py --generations 3 --population 10
        '''
    )
    
    # Configuration
    parser.add_argument(
        '--config',
        type=str,
        default='config/ga_config.yaml',
        help='Path to configuration file (default: config/ga_config.yaml)'
    )
    
    # Population parameters
    parser.add_argument(
        '--population',
        type=int,
        help='Population size (overrides config)'
    )
    
    parser.add_argument(
        '--generations',
        type=int,
        help='Number of generations to run (overrides config)'
    )
    
    parser.add_argument(
        '--elite',
        type=int,
        help='Elite size - number of best strategies to preserve (overrides config)'
    )
    
    # Execution modes
    parser.add_argument(
        '--resume',
        type=str,
        metavar='CHECKPOINT',
        help='Resume from checkpoint file'
    )
    
    parser.add_argument(
        '--no-mock',
        action='store_true',
        help='Use real Freqtrade backtesting (default: mock mode for testing)'
    )
    
    # Output
    parser.add_argument(
        '--checkpoint-interval',
        type=int,
        default=10,
        help='Save checkpoint every N generations (default: 10)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='strategies/generated',
        help='Output directory for generated strategies (default: strategies/generated)'
    )
    
    # Logging
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output (only errors)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        logger.setLevel('ERROR')
    else:
        logger.setLevel(args.log_level)
    
    # Display banner
    if not args.quiet:
        print_banner()
    
    # Load configuration
    config = None
    if args.config and Path(args.config).exists():
        try:
            from utils.config_loader import load_config
            config = load_config(args.config)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            config = {}
    else:
        logger.info("Using default configuration")
        config = {}
    
    # Override config with CLI arguments
    if args.population:
        config['population_size'] = args.population
    if args.generations:
        config['generations'] = args.generations
    if args.elite:
        config['elite_size'] = args.elite
    if args.checkpoint_interval:
        config['checkpoint_interval'] = args.checkpoint_interval
    
    # Validate
    if not config.get('population_size'):
        config['population_size'] = 20
    if not config.get('generations'):
        config['generations'] = 10
    
    # Display configuration
    if not args.quiet:
        logger.info("=" * 60)
        logger.info("GAFreqTrade Configuration:")
        logger.info(f"  Population Size: {config.get('population_size')}")
        logger.info(f"  Generations: {config.get('generations')}")
        logger.info(f"  Elite Size: {config.get('elite_size', 4)}")
        logger.info(f"  Mutation Rate: {config.get('mutation_rate', 0.20)}")
        logger.info(f"  Crossover Rate: {config.get('crossover_rate', 0.70)}")
        logger.info(f"  Evaluation Mode: {'Real Backtesting' if args.no_mock else 'Mock (Testing)'}")
        if args.resume:
            logger.info(f"  Resume from: {args.resume}")
        logger.info("=" * 60)
    
    # Confirm if using real backtesting
    if args.no_mock and not args.quiet:
        logger.warning("=" * 60)
        logger.warning("REAL BACKTESTING MODE ENABLED")
        logger.warning("This will use actual Freqtrade backtesting.")
        logger.warning("Make sure Freqtrade is properly configured.")
        logger.warning("=" * 60)
        input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Run evolution
    try:
        logger.info("Starting evolution...")
        
        final_population = run_evolution(
            config_path=args.config if config else None,
            resume_checkpoint=args.resume,
            max_generations=config.get('generations', 10),
            use_mock=not args.no_mock
        )
        
        logger.info("=" * 60)
        logger.info("EVOLUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Final population size: {len(final_population.strategies)}")
        logger.info(f"Best strategies saved in: {args.output_dir}/")
        logger.info(f"Checkpoints saved in: checkpoints/")
        logger.info("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n\nEvolution interrupted by user")
        logger.info("Progress has been saved in checkpoints/")
        return 1
        
    except Exception as e:
        logger.error(f"Error during evolution: {e}", exc_info=True)
        return 1


def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║                    GAFreqTrade v1.0                      ║
    ║                                                          ║
    ║        Genetic Algorithm Strategy Optimization           ║
    ║                  for Freqtrade                          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    sys.exit(main())
