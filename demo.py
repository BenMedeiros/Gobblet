"""
Demo script to showcase the Gobblet simulator capabilities.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gobblet.simulator import GameSimulator
from gobblet.moves import GameDataManager
from gobblet.game import GobbletGame
from gobblet.player import RandomPlayer, GreedyPlayer, DefensivePlayer, PieceColor


def demo_single_game():
    """Demonstrate a single game with detailed output."""
    print("=" * 60)
    print("DEMO: Single Game Simulation")
    print("=" * 60)
    
    # Create players
    light_player = GreedyPlayer(PieceColor.LIGHT)
    dark_player = DefensivePlayer(PieceColor.DARK)
    
    # Create and play game
    game = GobbletGame(light_player, dark_player)
    
    print(f"Starting game: {light_player} vs {dark_player}")
    print()
    
    # Play a few turns manually to show the board state
    for turn in range(5):
        if game.game_over:
            break
            
        print(f"Turn {turn + 1}: {game.current_player}'s move")
        game.play_turn()
        print(game.board)
        print()
    
    # Finish the game
    winner = game.play_game()
    
    print("Final game state:")
    print(game.board)
    print()
    
    if winner:
        print(f"Winner: {winner.value.capitalize()}")
    else:
        print("Game ended in a draw")
    
    print(f"Total turns: {game.turn_count}")
    print(f"Total moves: {len(game.move_tracker.moves)}")
    
    return game


def demo_batch_simulation():
    """Demonstrate batch simulation."""
    print("\n" + "=" * 60)
    print("DEMO: Batch Simulation")
    print("=" * 60)
    
    data_manager = GameDataManager("demo_data.json")
    simulator = GameSimulator(data_manager)
    
    # Run a small batch simulation
    results = simulator.run_batch_simulation(
        num_games=10,
        light_strategy="greedy",
        dark_strategy="defensive",
        verbose=False
    )
    
    print(f"\nSimulated {results['total_games']} games")
    print(f"Greedy (Light) wins: {results['light_wins']} ({results['light_win_rate']:.1%})")
    print(f"Defensive (Dark) wins: {results['dark_wins']} ({results['dark_win_rate']:.1%})")
    print(f"Draws: {results['draws']} ({results['draw_rate']:.1%})")
    print(f"Average game duration: {results['average_game_duration']:.3f}s")
    print(f"Average moves per game: {results['average_moves']:.1f}")


def demo_tournament():
    """Demonstrate tournament functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Tournament")
    print("=" * 60)
    
    data_manager = GameDataManager("tournament_demo_data.json")
    simulator = GameSimulator(data_manager)
    
    # Run a small tournament
    tournament_results = simulator.run_tournament(
        strategies=["random", "greedy", "defensive"],
        games_per_matchup=5,
        verbose=False
    )
    
    print("\nTournament Results:")
    overall_stats = tournament_results["overall_stats"]
    
    for i, strategy in enumerate(overall_stats["ranking"], 1):
        stats = overall_stats["strategy_stats"][strategy]
        print(f"{i}. {strategy.capitalize()}: {stats['win_rate']:.1%} win rate "
              f"({stats['total_wins']}/{stats['games_played']} games)")
    
    print(f"\nTotal games played: {tournament_results['total_games']}")
    print(f"Tournament duration: {tournament_results['total_time']:.2f}s")


def demo_data_analysis():
    """Demonstrate basic data analysis."""
    print("\n" + "=" * 60)
    print("DEMO: Data Analysis")
    print("=" * 60)
    
    # Load data from previous demos
    data_manager = GameDataManager("demo_data.json")
    games = data_manager.load_games()
    
    if not games:
        print("No game data available for analysis.")
        return
    
    print(f"Loaded {len(games)} games for analysis")
    
    # Basic statistics
    stats = data_manager.get_statistics()
    print("\nBasic Statistics:")
    print(f"- Total games: {stats['total_games']}")
    print(f"- Light win rate: {stats['light_win_rate']:.1%}")
    print(f"- Dark win rate: {stats['dark_win_rate']:.1%}")
    print(f"- Draw rate: {(stats['total_games'] - stats['light_wins'] - stats['dark_wins']) / stats['total_games']:.1%}")
    print(f"- Average moves per game: {stats['average_moves_per_game']:.1f}")
    print(f"- Average game duration: {stats['average_game_duration']:.2f}s")
    
    # Strategy analysis
    strategy_wins = {}
    strategy_games = {}
    
    for game in games:
        for color, strategy in game.player_strategies.items():
            if strategy not in strategy_wins:
                strategy_wins[strategy] = 0
                strategy_games[strategy] = 0
            
            strategy_games[strategy] += 1
            if game.winner == color:
                strategy_wins[strategy] += 1
    
    print("\nStrategy Performance:")
    for strategy in sorted(strategy_games.keys()):
        win_rate = strategy_wins[strategy] / strategy_games[strategy] if strategy_games[strategy] > 0 else 0
        print(f"- {strategy.capitalize()}: {win_rate:.1%} ({strategy_wins[strategy]}/{strategy_games[strategy]})")


def main():
    """Run all demos."""
    print("Gobblet Game Simulator - Demo")
    print("=" * 40)
    print("This demo showcases the key features of the Gobblet simulator:")
    print("1. Single game simulation with detailed output")
    print("2. Batch simulation for statistical analysis") 
    print("3. Tournament between different strategies")
    print("4. Basic data analysis")
    print()
    input("Press Enter to start the demo...")
    
    try:
        # Demo 1: Single game
        demo_single_game()
        input("\nPress Enter to continue to batch simulation demo...")
        
        # Demo 2: Batch simulation
        demo_batch_simulation()
        input("\nPress Enter to continue to tournament demo...")
        
        # Demo 3: Tournament
        demo_tournament()
        input("\nPress Enter to continue to data analysis demo...")
        
        # Demo 4: Data analysis
        demo_data_analysis()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("All core features demonstrated successfully!")
        print("You can now run simulations using: python main.py --help")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")


if __name__ == "__main__":
    main()
