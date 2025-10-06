"""
Game simulation engine for running multiple Gobblet games.
"""

import random
from typing import List, Dict, Any, Type, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from .game import GobbletGame
from .player import Player, RandomPlayer, GreedyPlayer, DefensivePlayer, PieceColor
from .moves import GameDataManager
from .piece import PieceColor


class GameSimulator:
    """Runs simulations of Gobblet games."""
    
    def __init__(self, data_manager: Optional[GameDataManager] = None):
        """
        Initialize the simulator.
        
        Args:
            data_manager: Optional data manager for storing results
        """
        self.data_manager = data_manager or GameDataManager()
        self.player_types = {
            "random": RandomPlayer,
            "greedy": GreedyPlayer,
            "defensive": DefensivePlayer
        }
    
    def run_single_simulation(self, 
                            light_strategy: str = "random",
                            dark_strategy: str = "random",
                            board_size: int = 4,
                            verbose: bool = False) -> Dict[str, Any]:
        """
        Run a single game simulation.
        
        Args:
            light_strategy: Strategy for light player
            dark_strategy: Strategy for dark player
            board_size: Size of the game board
            verbose: Whether to print game progress
            
        Returns:
            Dictionary containing game results
        """
        # Create players
        light_player = self._create_player(light_strategy, PieceColor.LIGHT)
        dark_player = self._create_player(dark_strategy, PieceColor.DARK)
        
        # Create and play game
        game = GobbletGame(light_player, dark_player, board_size)
        
        if verbose:
            print(f"Starting game: {light_player} vs {dark_player}")
        
        start_time = time.time()
        winner = game.play_game()
        end_time = time.time()
        
        # Get game record and save it
        game_record = game.get_game_record()
        self.data_manager.save_game(game_record)
        
        result = {
            "game_id": game.game_id,
            "winner": winner.value if winner else "draw",
            "light_strategy": light_strategy,
            "dark_strategy": dark_strategy,
            "turn_count": game.turn_count,
            "duration_seconds": end_time - start_time,
            "move_count": len(game.move_tracker.moves),
            "game_record": game_record
        }
        
        if verbose:
            self._print_game_result(result)
        
        return result
    
    def run_batch_simulation(self,
                           num_games: int,
                           light_strategy: str = "random",
                           dark_strategy: str = "random",
                           board_size: int = 4,
                           verbose: bool = True,
                           parallel: bool = True) -> Dict[str, Any]:
        """
        Run multiple game simulations.
        
        Args:
            num_games: Number of games to simulate
            light_strategy: Strategy for light player
            dark_strategy: Strategy for dark player
            board_size: Size of the game board
            verbose: Whether to print progress
            parallel: Whether to run games in parallel
            
        Returns:
            Dictionary containing batch simulation results
        """
        if verbose:
            print(f"Running {num_games} games: {light_strategy} vs {dark_strategy}")
        
        start_time = time.time()
        results = []
        
        if parallel and num_games > 1:
            results = self._run_parallel_games(
                num_games, light_strategy, dark_strategy, board_size, verbose
            )
        else:
            results = self._run_sequential_games(
                num_games, light_strategy, dark_strategy, board_size, verbose
            )
        
        end_time = time.time()
        
        # Analyze results
        analysis = self._analyze_batch_results(results)
        analysis.update({
            "total_simulation_time": end_time - start_time,
            "games_per_second": num_games / (end_time - start_time),
            "light_strategy": light_strategy,
            "dark_strategy": dark_strategy,
            "board_size": board_size
        })
        
        if verbose:
            self._print_batch_analysis(analysis)
        
        return analysis
    
    def run_tournament(self,
                      strategies: List[str],
                      games_per_matchup: int = 10,
                      board_size: int = 4,
                      verbose: bool = True) -> Dict[str, Any]:
        """
        Run a tournament with multiple strategies.
        
        Args:
            strategies: List of strategy names
            games_per_matchup: Number of games per strategy matchup
            board_size: Size of the game board
            verbose: Whether to print progress
            
        Returns:
            Dictionary containing tournament results
        """
        if verbose:
            print(f"Running tournament with strategies: {strategies}")
            print(f"Games per matchup: {games_per_matchup}")
        
        tournament_results = {
            "strategies": strategies,
            "games_per_matchup": games_per_matchup,
            "matchups": {},
            "overall_stats": {}
        }
        
        total_games = len(strategies) * len(strategies) * games_per_matchup
        games_completed = 0
        
        start_time = time.time()
        
        # Run all matchups
        for light_strategy in strategies:
            for dark_strategy in strategies:
                matchup_key = f"{light_strategy}_vs_{dark_strategy}"
                
                if verbose:
                    print(f"Running matchup: {matchup_key}")
                
                matchup_results = self.run_batch_simulation(
                    num_games=games_per_matchup,
                    light_strategy=light_strategy,
                    dark_strategy=dark_strategy,
                    board_size=board_size,
                    verbose=False,
                    parallel=True
                )
                
                tournament_results["matchups"][matchup_key] = matchup_results
                games_completed += games_per_matchup
                
                if verbose:
                    progress = (games_completed / total_games) * 100
                    print(f"Tournament progress: {progress:.1f}% ({games_completed}/{total_games})")
        
        end_time = time.time()
        
        # Calculate overall statistics
        tournament_results["overall_stats"] = self._analyze_tournament_results(
            tournament_results["matchups"], strategies
        )
        tournament_results["total_time"] = end_time - start_time
        tournament_results["total_games"] = total_games
        
        if verbose:
            self._print_tournament_results(tournament_results)
        
        return tournament_results
    
    def _create_player(self, strategy: str, color: PieceColor) -> Player:
        """Create a player with the specified strategy."""
        if strategy not in self.player_types:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.player_types.keys())}")
        
        player_class = self.player_types[strategy]
        return player_class(color)
    
    def _run_parallel_games(self, num_games: int, light_strategy: str, 
                          dark_strategy: str, board_size: int, verbose: bool) -> List[Dict[str, Any]]:
        """Run games in parallel using ThreadPoolExecutor."""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(num_games, 8)) as executor:
            # Submit all games
            futures = [
                executor.submit(
                    self.run_single_simulation,
                    light_strategy, dark_strategy, board_size, False
                )
                for _ in range(num_games)
            ]
            
            # Collect results as they complete
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)
                
                if verbose and (i + 1) % max(1, num_games // 10) == 0:
                    print(f"Completed {i + 1}/{num_games} games")
        
        return results
    
    def _run_sequential_games(self, num_games: int, light_strategy: str,
                            dark_strategy: str, board_size: int, verbose: bool) -> List[Dict[str, Any]]:
        """Run games sequentially."""
        results = []
        
        for i in range(num_games):
            result = self.run_single_simulation(
                light_strategy, dark_strategy, board_size, False
            )
            results.append(result)
            
            if verbose and (i + 1) % max(1, num_games // 10) == 0:
                print(f"Completed {i + 1}/{num_games} games")
        
        return results
    
    def _analyze_batch_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze results from a batch of games."""
        if not results:
            return {"error": "No results to analyze"}
        
        total_games = len(results)
        light_wins = sum(1 for r in results if r["winner"] == "light")
        dark_wins = sum(1 for r in results if r["winner"] == "dark")
        draws = sum(1 for r in results if r["winner"] == "draw")
        
        total_turns = sum(r["turn_count"] for r in results)
        total_moves = sum(r["move_count"] for r in results)
        total_duration = sum(r["duration_seconds"] for r in results)
        
        return {
            "total_games": total_games,
            "light_wins": light_wins,
            "dark_wins": dark_wins,
            "draws": draws,
            "light_win_rate": light_wins / total_games,
            "dark_win_rate": dark_wins / total_games,
            "draw_rate": draws / total_games,
            "average_turns": total_turns / total_games,
            "average_moves": total_moves / total_games,
            "average_game_duration": total_duration / total_games,
            "total_duration": total_duration
        }
    
    def _analyze_tournament_results(self, matchups: Dict[str, Any], 
                                  strategies: List[str]) -> Dict[str, Any]:
        """Analyze tournament results across all matchups."""
        strategy_stats = {strategy: {
            "games_played": 0,
            "wins_as_light": 0,
            "wins_as_dark": 0,
            "total_wins": 0,
            "draws": 0,
            "win_rate": 0.0
        } for strategy in strategies}
        
        # Aggregate stats for each strategy
        for matchup_key, matchup_data in matchups.items():
            light_strategy, dark_strategy = matchup_key.split("_vs_")
            
            # Update light player stats
            strategy_stats[light_strategy]["games_played"] += matchup_data["total_games"]
            strategy_stats[light_strategy]["wins_as_light"] += matchup_data["light_wins"]
            strategy_stats[light_strategy]["total_wins"] += matchup_data["light_wins"]
            strategy_stats[light_strategy]["draws"] += matchup_data["draws"]
            
            # Update dark player stats
            strategy_stats[dark_strategy]["games_played"] += matchup_data["total_games"]
            strategy_stats[dark_strategy]["wins_as_dark"] += matchup_data["dark_wins"]
            strategy_stats[dark_strategy]["total_wins"] += matchup_data["dark_wins"]
            strategy_stats[dark_strategy]["draws"] += matchup_data["draws"]
        
        # Calculate win rates
        for strategy, stats in strategy_stats.items():
            if stats["games_played"] > 0:
                stats["win_rate"] = stats["total_wins"] / stats["games_played"]
        
        # Sort by win rate
        ranked_strategies = sorted(
            strategy_stats.items(),
            key=lambda x: x[1]["win_rate"],
            reverse=True
        )
        
        return {
            "strategy_stats": strategy_stats,
            "ranking": [strategy for strategy, _ in ranked_strategies]
        }
    
    def _print_game_result(self, result: Dict[str, Any]) -> None:
        """Print the result of a single game."""
        winner_str = result["winner"].capitalize() if result["winner"] != "draw" else "Draw"
        print(f"Game {result['game_id'][:8]}: {winner_str} "
              f"({result['turn_count']} turns, {result['move_count']} moves, "
              f"{result['duration_seconds']:.2f}s)")
    
    def _print_batch_analysis(self, analysis: Dict[str, Any]) -> None:
        """Print analysis of batch simulation results."""
        print("\n" + "="*50)
        print("BATCH SIMULATION RESULTS")
        print("="*50)
        print(f"Total games: {analysis['total_games']}")
        print(f"Light wins: {analysis['light_wins']} ({analysis['light_win_rate']:.1%})")
        print(f"Dark wins: {analysis['dark_wins']} ({analysis['dark_win_rate']:.1%})")
        print(f"Draws: {analysis['draws']} ({analysis['draw_rate']:.1%})")
        print(f"Average turns per game: {analysis['average_turns']:.1f}")
        print(f"Average moves per game: {analysis['average_moves']:.1f}")
        print(f"Total simulation time: {analysis['total_simulation_time']:.2f}s")
        print(f"Games per second: {analysis['games_per_second']:.2f}")
        print("="*50)
    
    def _print_tournament_results(self, tournament_results: Dict[str, Any]) -> None:
        """Print tournament results."""
        print("\n" + "="*60)
        print("TOURNAMENT RESULTS")
        print("="*60)
        
        overall_stats = tournament_results["overall_stats"]
        
        print("Strategy Rankings:")
        for i, strategy in enumerate(overall_stats["ranking"], 1):
            stats = overall_stats["strategy_stats"][strategy]
            print(f"{i}. {strategy}: {stats['win_rate']:.1%} win rate "
                  f"({stats['total_wins']}/{stats['games_played']} games)")
        
        print(f"\nTotal games played: {tournament_results['total_games']}")
        print(f"Total tournament time: {tournament_results['total_time']:.2f}s")
        print("="*60)
