"""
Main entry point for the Gobblet game simulator.
"""

import argparse
import sys
import os
from typing import List

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gobblet.simulator import GameSimulator
from gobblet.moves import GameDataManager

# Optional imports for analysis (require additional dependencies)
try:
    from analysis.move_analyzer import MoveAnalyzer
    from analysis.strategy_analyzer import StrategyAnalyzer
    ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Analysis modules not available ({e})")
    print("Install additional dependencies: pip install pandas matplotlib seaborn")
    MoveAnalyzer = None
    StrategyAnalyzer = None
    ANALYSIS_AVAILABLE = False


def main():
    """Main function to run the Gobblet simulator."""
    parser = argparse.ArgumentParser(description='Gobblet Game Simulator')
    
    # Simulation arguments
    parser.add_argument('--games', type=int, default=10,
                       help='Number of games to simulate (default: 10)')
    parser.add_argument('--light-strategy', type=str, default='random',
                       choices=['random', 'greedy', 'defensive'],
                       help='Strategy for light player (default: random)')
    parser.add_argument('--dark-strategy', type=str, default='random',
                       choices=['random', 'greedy', 'defensive'],
                       help='Strategy for dark player (default: random)')
    parser.add_argument('--board-size', type=int, default=4,
                       help='Size of the game board (default: 4)')
    parser.add_argument('--parallel', action='store_true',
                       help='Run games in parallel (faster)')
    parser.add_argument('--verbose', action='store_true',
                       help='Print detailed output')
    
    # Tournament arguments
    parser.add_argument('--tournament', action='store_true',
                       help='Run a tournament with all strategies')
    parser.add_argument('--tournament-games', type=int, default=10,
                       help='Games per matchup in tournament (default: 10)')
    
    # Analysis arguments
    parser.add_argument('--analyze', action='store_true',
                       help='Run analysis on existing game data')
    parser.add_argument('--data-file', type=str, default='data/games.json',
                       help='Path to game data file (default: data/games.json)')
    
    # Output arguments
    parser.add_argument('--save-plots', type=str,
                       help='Directory to save analysis plots')
    
    args = parser.parse_args()
    
    # Create data manager
    data_manager = GameDataManager(args.data_file)
    
    if args.analyze:
        run_analysis(data_manager, args)
    elif args.tournament:
        run_tournament(data_manager, args)
    else:
        run_simulation(data_manager, args)


def run_simulation(data_manager: GameDataManager, args):
    """Run a batch simulation."""
    print("Starting Gobblet Game Simulation")
    print("=" * 40)
    print(f"Games to simulate: {args.games}")
    print(f"Light strategy: {args.light_strategy}")
    print(f"Dark strategy: {args.dark_strategy}")
    print(f"Board size: {args.board_size}x{args.board_size}")
    print(f"Parallel execution: {args.parallel}")
    print()
    
    simulator = GameSimulator(data_manager)
    
    try:
        results = simulator.run_batch_simulation(
            num_games=args.games,
            light_strategy=args.light_strategy,
            dark_strategy=args.dark_strategy,
            board_size=args.board_size,
            verbose=args.verbose,
            parallel=args.parallel
        )
        
        print("\nSimulation completed successfully!")
        print(f"Data saved to: {args.data_file}")
        
        if args.analyze:
            print("\nRunning quick analysis...")
            run_quick_analysis(data_manager)
            
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError during simulation: {e}")
        sys.exit(1)


def run_tournament(data_manager: GameDataManager, args):
    """Run a tournament with all strategies."""
    print("Starting Gobblet Tournament")
    print("=" * 30)
    
    strategies = ['random', 'greedy', 'defensive']
    print(f"Strategies: {strategies}")
    print(f"Games per matchup: {args.tournament_games}")
    print(f"Board size: {args.board_size}x{args.board_size}")
    print()
    
    simulator = GameSimulator(data_manager)
    
    try:
        tournament_results = simulator.run_tournament(
            strategies=strategies,
            games_per_matchup=args.tournament_games,
            board_size=args.board_size,
            verbose=args.verbose
        )
        
        print("\nTournament completed successfully!")
        print(f"Data saved to: {args.data_file}")
        
        if args.analyze:
            print("\nRunning tournament analysis...")
            run_tournament_analysis(data_manager, tournament_results)
            
    except KeyboardInterrupt:
        print("\nTournament interrupted by user.")
    except Exception as e:
        print(f"\nError during tournament: {e}")
        sys.exit(1)


def run_analysis(data_manager: GameDataManager, args):
    """Run comprehensive analysis on existing game data."""
    if not ANALYSIS_AVAILABLE:
        print("Analysis not available. Install dependencies: pip install pandas matplotlib seaborn")
        return
        
    print("Starting Gobblet Game Analysis")
    print("=" * 35)
    
    # Load existing games
    games = data_manager.load_games()
    if not games:
        print(f"No game data found in {args.data_file}")
        print("Run some simulations first to generate data for analysis.")
        return
    
    print(f"Loaded {len(games)} games from {args.data_file}")
    print()
    
    # Move analysis
    print("Running move pattern analysis...")
    move_analyzer = MoveAnalyzer(data_manager)
    move_report = move_analyzer.generate_comprehensive_report()
    print(move_report)
    
    # Strategy analysis
    print("\nRunning strategy analysis...")
    strategy_analyzer = StrategyAnalyzer(data_manager)
    strategy_report = strategy_analyzer.generate_comprehensive_strategy_report()
    print(strategy_report)
    
    # Generate plots if requested
    if args.save_plots:
        print(f"\nGenerating plots in {args.save_plots}...")
        try:
            os.makedirs(args.save_plots, exist_ok=True)
            
            # Only try to create plots if matplotlib is available
            try:
                heatmap_path = os.path.join(args.save_plots, "move_frequency_heatmap.png")
                move_analyzer.create_move_frequency_heatmap(heatmap_path)
                print(f"Saved move frequency heatmap to {heatmap_path}")
                
                strategy_plot_path = os.path.join(args.save_plots, "strategy_comparison.png")
                move_analyzer.create_strategy_comparison_plot(strategy_plot_path)
                print(f"Saved strategy comparison plot to {strategy_plot_path}")
                
            except ImportError:
                print("Matplotlib not available - skipping plot generation.")
                print("Install matplotlib with: pip install matplotlib")
            
        except Exception as e:
            print(f"Error generating plots: {e}")


def run_quick_analysis(data_manager: GameDataManager):
    """Run a quick analysis after simulation."""
    games = data_manager.load_games()
    if not games:
        return
    
    # Basic statistics
    stats = data_manager.get_statistics()
    print("Quick Analysis Results:")
    print("-" * 25)
    print(f"Total games: {stats['total_games']}")
    print(f"Light wins: {stats['light_wins']} ({stats['light_win_rate']:.1%})")
    print(f"Dark wins: {stats['dark_wins']} ({stats['dark_win_rate']:.1%})")
    print(f"Draws: {stats['draws']}")
    print(f"Average moves per game: {stats['average_moves_per_game']:.1f}")
    
    if stats['average_game_duration'] > 0:
        print(f"Average game duration: {stats['average_game_duration']:.2f}s")


def run_tournament_analysis(data_manager: GameDataManager, tournament_results):
    """Run analysis specific to tournament results."""
    if not ANALYSIS_AVAILABLE:
        print("Detailed analysis not available. Install dependencies: pip install pandas matplotlib seaborn")
        return
        
    strategy_analyzer = StrategyAnalyzer(data_manager)
    
    # Get strategy recommendations
    recommendations = strategy_analyzer.generate_strategy_recommendations()
    
    print("\nTournament Analysis:")
    print("-" * 20)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")


def create_sample_config():
    """Create a sample configuration file."""
    config = """# Gobblet Simulator Configuration
# Run with: python main.py @config.txt

--games
50
--light-strategy
greedy
--dark-strategy
defensive
--board-size
4
--parallel
--verbose
--analyze
"""
    
    with open("config.txt", "w") as f:
        f.write(config)
    
    print("Created sample configuration file: config.txt")
    print("Use with: python main.py @config.txt")


if __name__ == "__main__":
    # Check if user wants to create sample config
    if len(sys.argv) == 2 and sys.argv[1] == "--create-config":
        create_sample_config()
        sys.exit(0)
    
    # Show help for common usage
    if len(sys.argv) == 1:
        print("Gobblet Game Simulator")
        print("=" * 25)
        print()
        print("Quick start examples:")
        print("  python main.py --games 20 --verbose")
        print("  python main.py --tournament --tournament-games 15")
        print("  python main.py --analyze --data-file data/games.json")
        print("  python main.py --light-strategy greedy --dark-strategy defensive")
        print()
        print("For full help: python main.py --help")
        print("To create config file: python main.py --create-config")
        print()
    
    main()
