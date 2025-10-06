"""
Strategy analysis for Gobblet games.
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics

from src.gobblet.moves import GameRecord, GameDataManager
from src.gobblet.piece import PieceColor


class StrategyAnalyzer:
    """Analyzes strategy effectiveness in Gobblet games."""
    
    def __init__(self, data_manager: GameDataManager):
        """
        Initialize the strategy analyzer.
        
        Args:
            data_manager: The game data manager
        """
        self.data_manager = data_manager
        self.games = data_manager.load_games()
    
    def analyze_strategy_effectiveness(self) -> Dict[str, Any]:
        """
        Analyze the overall effectiveness of different strategies.
        
        Returns:
            Dictionary containing strategy effectiveness metrics
        """
        strategy_stats = defaultdict(lambda: {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "win_rate": 0.0,
            "average_game_length": 0.0,
            "total_moves_made": 0,
            "average_moves_per_game": 0.0,
            "games_as_light": 0,
            "games_as_dark": 0,
            "wins_as_light": 0,
            "wins_as_dark": 0
        })
        
        for game in self.games:
            for color, strategy in game.player_strategies.items():
                stats = strategy_stats[strategy]
                stats["games_played"] += 1
                
                # Track color statistics
                if color == PieceColor.LIGHT:
                    stats["games_as_light"] += 1
                    if game.winner == PieceColor.LIGHT:
                        stats["wins_as_light"] += 1
                else:
                    stats["games_as_dark"] += 1
                    if game.winner == PieceColor.DARK:
                        stats["wins_as_dark"] += 1
                
                # Track wins/losses/draws
                if game.winner == color:
                    stats["wins"] += 1
                elif game.winner is None:
                    stats["draws"] += 1
                else:
                    stats["losses"] += 1
                
                # Track game length and moves
                if game.game_duration_seconds:
                    stats["average_game_length"] += game.game_duration_seconds
                
                player_moves = [m for m in game.moves if m.player_color == color]
                stats["total_moves_made"] += len(player_moves)
        
        # Calculate averages and rates
        for strategy, stats in strategy_stats.items():
            if stats["games_played"] > 0:
                stats["win_rate"] = stats["wins"] / stats["games_played"]
                stats["average_moves_per_game"] = stats["total_moves_made"] / stats["games_played"]
                stats["average_game_length"] /= stats["games_played"]
        
        return dict(strategy_stats)
    
    def analyze_head_to_head_matchups(self) -> Dict[str, Any]:
        """
        Analyze head-to-head performance between strategies.
        
        Returns:
            Dictionary containing matchup analysis
        """
        matchup_stats = defaultdict(lambda: {
            "games_played": 0,
            "light_wins": 0,
            "dark_wins": 0,
            "draws": 0,
            "light_strategy": "",
            "dark_strategy": "",
            "average_game_length": 0.0,
            "average_total_moves": 0.0
        })
        
        for game in self.games:
            if len(game.player_strategies) != 2:
                continue  # Skip if not exactly 2 players
            
            light_strategy = game.player_strategies.get(PieceColor.LIGHT, "unknown")
            dark_strategy = game.player_strategies.get(PieceColor.DARK, "unknown")
            
            matchup_key = f"{light_strategy}_vs_{dark_strategy}"
            stats = matchup_stats[matchup_key]
            
            stats["games_played"] += 1
            stats["light_strategy"] = light_strategy
            stats["dark_strategy"] = dark_strategy
            
            if game.winner == PieceColor.LIGHT:
                stats["light_wins"] += 1
            elif game.winner == PieceColor.DARK:
                stats["dark_wins"] += 1
            else:
                stats["draws"] += 1
            
            if game.game_duration_seconds:
                stats["average_game_length"] += game.game_duration_seconds
            
            stats["average_total_moves"] += game.total_moves
        
        # Calculate averages
        for matchup, stats in matchup_stats.items():
            if stats["games_played"] > 0:
                stats["average_game_length"] /= stats["games_played"]
                stats["average_total_moves"] /= stats["games_played"]
                
                # Add win rates
                stats["light_win_rate"] = stats["light_wins"] / stats["games_played"]
                stats["dark_win_rate"] = stats["dark_wins"] / stats["games_played"]
                stats["draw_rate"] = stats["draws"] / stats["games_played"]
        
        return dict(matchup_stats)
    
    def analyze_strategy_characteristics(self) -> Dict[str, Any]:
        """
        Analyze the characteristics of different strategies.
        
        Returns:
            Dictionary containing strategy characteristics
        """
        strategy_characteristics = defaultdict(lambda: {
            "aggressive_score": 0.0,  # Based on capture frequency
            "defensive_score": 0.0,   # Based on blocking patterns
            "positional_score": 0.0, # Based on position preferences
            "piece_size_preferences": defaultdict(int),
            "move_type_preferences": defaultdict(int),
            "average_captures_per_game": 0.0,
            "preferred_positions": [],
            "games_analyzed": 0
        })
        
        for game in self.games:
            for color, strategy in game.player_strategies.items():
                chars = strategy_characteristics[strategy]
                chars["games_analyzed"] += 1
                
                player_moves = [m for m in game.moves if m.player_color == color]
                captures = sum(1 for m in player_moves if m.captured_piece_id is not None)
                
                chars["average_captures_per_game"] += captures
                
                for move in player_moves:
                    chars["piece_size_preferences"][move.piece_size] += 1
                    chars["move_type_preferences"][move.move_type] += 1
        
        # Calculate final scores and averages
        for strategy, chars in strategy_characteristics.items():
            if chars["games_analyzed"] > 0:
                chars["average_captures_per_game"] /= chars["games_analyzed"]
                
                # Calculate aggressive score (higher capture rate = more aggressive)
                chars["aggressive_score"] = min(1.0, chars["average_captures_per_game"] / 2.0)
                
                # Calculate preferred positions
                position_counts = defaultdict(int)
                for game in self.games:
                    if strategy in game.player_strategies.values():
                        for color, strat in game.player_strategies.items():
                            if strat == strategy:
                                player_moves = [m for m in game.moves if m.player_color == color]
                                for move in player_moves:
                                    position_counts[move.to_position] += 1
                
                # Get top 5 preferred positions
                top_positions = sorted(
                    position_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                chars["preferred_positions"] = [pos for pos, _ in top_positions]
        
        return dict(strategy_characteristics)
    
    def find_optimal_strategy_combinations(self) -> Dict[str, Any]:
        """
        Find the most effective strategy combinations.
        
        Returns:
            Dictionary containing optimal strategy analysis
        """
        matchup_analysis = self.analyze_head_to_head_matchups()
        
        # Find most balanced matchups (close win rates)
        balanced_matchups = []
        dominant_matchups = []
        
        for matchup, stats in matchup_analysis.items():
            if stats["games_played"] < 5:  # Skip matchups with too few games
                continue
            
            light_rate = stats["light_win_rate"]
            dark_rate = stats["dark_win_rate"]
            
            balance_score = 1.0 - abs(light_rate - dark_rate)
            
            matchup_info = {
                "matchup": matchup,
                "balance_score": balance_score,
                "light_win_rate": light_rate,
                "dark_win_rate": dark_rate,
                "games_played": stats["games_played"],
                "average_game_length": stats["average_game_length"]
            }
            
            if balance_score > 0.7:  # Fairly balanced
                balanced_matchups.append(matchup_info)
            elif abs(light_rate - dark_rate) > 0.3:  # One side dominates
                dominant_matchups.append(matchup_info)
        
        # Sort by balance score and dominance
        balanced_matchups.sort(key=lambda x: x["balance_score"], reverse=True)
        dominant_matchups.sort(key=lambda x: abs(x["light_win_rate"] - x["dark_win_rate"]), reverse=True)
        
        return {
            "most_balanced_matchups": balanced_matchups[:5],
            "most_dominant_matchups": dominant_matchups[:5],
            "total_matchups_analyzed": len(matchup_analysis)
        }
    
    def analyze_learning_curves(self) -> Dict[str, Any]:
        """
        Analyze how strategy performance changes over time.
        
        Returns:
            Dictionary containing learning curve analysis
        """
        # Group games by strategy and time
        strategy_timeline = defaultdict(list)
        
        for game in self.games:
            for color, strategy in game.player_strategies.items():
                game_result = {
                    "timestamp": game.start_time,
                    "won": game.winner == color,
                    "game_length": game.total_moves,
                    "duration": game.game_duration_seconds
                }
                strategy_timeline[strategy].append(game_result)
        
        # Sort by timestamp for each strategy
        for strategy in strategy_timeline:
            strategy_timeline[strategy].sort(key=lambda x: x["timestamp"])
        
        # Calculate rolling averages
        learning_analysis = {}
        window_size = 10  # Games to include in rolling average
        
        for strategy, games in strategy_timeline.items():
            if len(games) < window_size:
                continue
            
            rolling_win_rates = []
            rolling_game_lengths = []
            
            for i in range(window_size - 1, len(games)):
                window_games = games[i - window_size + 1:i + 1]
                
                win_rate = sum(1 for g in window_games if g["won"]) / len(window_games)
                avg_length = sum(g["game_length"] for g in window_games) / len(window_games)
                
                rolling_win_rates.append(win_rate)
                rolling_game_lengths.append(avg_length)
            
            # Calculate trend (improvement/decline)
            if len(rolling_win_rates) >= 2:
                early_performance = statistics.mean(rolling_win_rates[:len(rolling_win_rates)//3])
                late_performance = statistics.mean(rolling_win_rates[-len(rolling_win_rates)//3:])
                performance_trend = late_performance - early_performance
            else:
                performance_trend = 0.0
            
            learning_analysis[strategy] = {
                "total_games": len(games),
                "rolling_win_rates": rolling_win_rates,
                "rolling_game_lengths": rolling_game_lengths,
                "performance_trend": performance_trend,
                "final_win_rate": rolling_win_rates[-1] if rolling_win_rates else 0.0,
                "initial_win_rate": rolling_win_rates[0] if rolling_win_rates else 0.0
            }
        
        return learning_analysis
    
    def generate_strategy_recommendations(self) -> List[str]:
        """
        Generate recommendations based on strategy analysis.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Analyze strategy effectiveness
        effectiveness = self.analyze_strategy_effectiveness()
        
        if not effectiveness:
            recommendations.append("No strategy data available for analysis.")
            return recommendations
        
        # Find best performing strategy
        best_strategy = max(effectiveness.items(), key=lambda x: x[1]["win_rate"])
        recommendations.append(
            f"Most effective strategy: {best_strategy[0]} with {best_strategy[1]['win_rate']:.1%} win rate"
        )
        
        # Find most aggressive strategy
        characteristics = self.analyze_strategy_characteristics()
        if characteristics:
            most_aggressive = max(characteristics.items(), key=lambda x: x[1]["aggressive_score"])
            recommendations.append(
                f"Most aggressive strategy: {most_aggressive[0]} (captures {most_aggressive[1]['average_captures_per_game']:.1f} pieces per game)"
            )
        
        # Analyze matchups
        matchups = self.analyze_head_to_head_matchups()
        if matchups:
            # Find most interesting matchup
            most_competitive = None
            min_win_diff = float('inf')
            
            for matchup, stats in matchups.items():
                if stats["games_played"] >= 5:  # Only consider well-tested matchups
                    win_diff = abs(stats["light_win_rate"] - stats["dark_win_rate"])
                    if win_diff < min_win_diff:
                        min_win_diff = win_diff
                        most_competitive = (matchup, stats)
            
            if most_competitive:
                matchup_name, stats = most_competitive
                recommendations.append(
                    f"Most competitive matchup: {matchup_name} "
                    f"(Light: {stats['light_win_rate']:.1%}, Dark: {stats['dark_win_rate']:.1%})"
                )
        
        # Learning curve analysis
        learning = self.analyze_learning_curves()
        if learning:
            improving_strategies = [
                (strategy, data["performance_trend"]) 
                for strategy, data in learning.items() 
                if data["performance_trend"] > 0.1
            ]
            
            if improving_strategies:
                best_improving = max(improving_strategies, key=lambda x: x[1])
                recommendations.append(
                    f"Most improved strategy: {best_improving[0]} "
                    f"(+{best_improving[1]:.1%} performance gain)"
                )
        
        return recommendations
    
    def generate_comprehensive_strategy_report(self) -> str:
        """
        Generate a comprehensive strategy analysis report.
        
        Returns:
            String containing the formatted report
        """
        report = []
        report.append("="*60)
        report.append("COMPREHENSIVE STRATEGY ANALYSIS REPORT")
        report.append("="*60)
        
        # Strategy effectiveness
        effectiveness = self.analyze_strategy_effectiveness()
        if effectiveness:
            report.append("STRATEGY EFFECTIVENESS")
            report.append("-" * 25)
            
            # Sort by win rate
            sorted_strategies = sorted(
                effectiveness.items(), 
                key=lambda x: x[1]["win_rate"], 
                reverse=True
            )
            
            for i, (strategy, stats) in enumerate(sorted_strategies, 1):
                report.append(f"{i}. {strategy.upper()}")
                report.append(f"   Win Rate: {stats['win_rate']:.1%}")
                report.append(f"   Games Played: {stats['games_played']}")
                report.append(f"   Avg Moves/Game: {stats['average_moves_per_game']:.1f}")
                report.append(f"   As Light: {stats['wins_as_light']}/{stats['games_as_light']}")
                report.append(f"   As Dark: {stats['wins_as_dark']}/{stats['games_as_dark']}")
                report.append("")
        
        # Head-to-head analysis
        matchups = self.analyze_head_to_head_matchups()
        if matchups:
            report.append("HEAD-TO-HEAD MATCHUP ANALYSIS")
            report.append("-" * 35)
            
            for matchup, stats in matchups.items():
                if stats["games_played"] >= 3:  # Only show meaningful matchups
                    report.append(f"{matchup}:")
                    report.append(f"  Games: {stats['games_played']}")
                    report.append(f"  Light wins: {stats['light_win_rate']:.1%}")
                    report.append(f"  Dark wins: {stats['dark_win_rate']:.1%}")
                    report.append(f"  Draws: {stats['draw_rate']:.1%}")
                    report.append("")
        
        # Strategy characteristics
        characteristics = self.analyze_strategy_characteristics()
        if characteristics:
            report.append("STRATEGY CHARACTERISTICS")
            report.append("-" * 25)
            
            for strategy, chars in characteristics.items():
                report.append(f"{strategy.upper()}:")
                report.append(f"  Aggressiveness: {chars['aggressive_score']:.2f}")
                report.append(f"  Avg Captures/Game: {chars['average_captures_per_game']:.1f}")
                report.append(f"  Preferred Positions: {chars['preferred_positions'][:3]}")
                
                # Most used piece sizes
                if chars['piece_size_preferences']:
                    most_used_size = max(
                        chars['piece_size_preferences'].items(), 
                        key=lambda x: x[1]
                    )
                    report.append(f"  Favorite Piece Size: {most_used_size[0].name}")
                
                report.append("")
        
        # Recommendations
        recommendations = self.generate_strategy_recommendations()
        if recommendations:
            report.append("RECOMMENDATIONS")
            report.append("-" * 15)
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("="*60)
        
        return "\n".join(report)
