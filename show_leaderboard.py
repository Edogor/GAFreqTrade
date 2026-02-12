#!/usr/bin/env python3
"""
Show Leaderboard - Display top performing strategies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from pathlib import Path
from storage.strategy_db import StrategyDB
from storage.leaderboard import Leaderboard


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='GAFreqTrade Leaderboard - Display top strategies',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of top strategies to display (default: 10)'
    )
    
    parser.add_argument(
        '--db',
        type=str,
        default='storage/strategies.db',
        help='Path to database file (default: storage/strategies.db)'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='Export leaderboard to file'
    )
    
    parser.add_argument(
        '--save-hof',
        action='store_true',
        help='Save top strategies to Hall of Fame directory'
    )
    
    args = parser.parse_args()
    
    # Check if database exists
    if not Path(args.db).exists():
        print(f"Error: Database not found at {args.db}")
        print("Run evolution first to create strategies.")
        return 1
    
    # Load database
    db = StrategyDB(args.db)
    leaderboard = Leaderboard(db)
    
    # Display leaderboard
    leaderboard.display(args.top)
    
    # Export if requested
    if args.export:
        leaderboard.export_to_file(args.export)
    
    # Save to Hall of Fame if requested
    if args.save_hof:
        leaderboard.save_hall_of_fame_strategies(args.top)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
