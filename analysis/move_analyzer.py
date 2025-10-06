"""
Move pattern analysis for Gobblet games.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
import numpy as np

from src.gobblet.moves import GameRecord, Move, GameDataManager
from src.gobblet.piece import PieceColor, PieceSize


class MoveAnalyzer:
    """Analyzes move patterns from game data."""
    
    def __init__(self, data_manager: GameDataManager):
        """
        Initialize the move analyzer.
        
        Args:
            data_manager: The game data manager
        """
        self.data_manager = data_manager
        self.games = data_manager.load_games()
    
    def analyze_opening_moves(self, num_moves: int = 5) -> Dict[str, Any]:
        """
        Analyze the most common opening moves.
        
        Args:
            num_moves: Number of opening moves to analyze
            
        Returns:
            Dictionary containing opening move analysis
        """
        opening_sequences = defaultdict(int)
        position_frequency = defaultdict(int)
        piece_size_frequency = defaultdict(int)
        
        for game in self.games:
            if len(game.moves) >= num_moves:
                # Extract opening sequence
                opening = []
                for i in range(min(num_moves, len(game.moves))):
                    move = game.moves[i]
                    opening.append(f"{move.to_position}")
                    
                    # Track individual position and piece frequencies
                    position_frequency[move.to_position] += 1
                    piece_size_frequency[move.piece_size] += 1
                
                opening_sequences[tuple(opening)] += 1
        
        # Find most common sequences
        most_common_sequences = Counter(opening_sequences).most_common(10)
        most_common_positions = Counter(position_frequency).most_common(10)
        most_common_sizes = Counter(piece_size_frequency).most_common()
        
        return {
            "most_common_sequences": most_common_sequences,
            "most_common_positions": most_common_positions,
            "most_common_piece_sizes": most_common_sizes,
            "total_games_analyzed": len([g for g in self.games if len(g.moves) >= num_moves])
        }
    
    def analyze_move_patterns_by_strategy(self) -> Dict[str, Any]:
        """
        Analyze move patterns for different strategies.
        
        Returns:
            Dictionary containing strategy-specific move patterns
        """
        strategy_patterns = defaultdict(lambda: {
            "position_preferences": defaultdict(int),
            "piece_size_preferences": defaultdict(int),
            "move_type_preferences": defaultdict(int),
            "average_moves_per_game": 0,
            "games_count": 0
        })
        
        for game in self.games:
            for color, strategy in game.player_strategies.items():
                player_moves = [m for m in game.moves if m.player_color == color]
                
                strategy_patterns[strategy]["games_count"] += 1
                strategy_patterns[strategy]["average_moves_per_game"] += len(player_moves)
                
                for move in player_moves:
                    strategy_patterns[strategy]["position_preferences"][move.to_position] += 1
                    strategy_patterns[strategy]["piece_size_preferences"][move.piece_size] += 1
                    strategy_patterns[strategy]["move_type_preferences"][move.move_type] += 1
        
        # Calculate averages
        for strategy, data in strategy_patterns.items():
            if data["games_count"] > 0:
                data["average_moves_per_game"] /= data["games_count"]
        
        return dict(strategy_patterns)
    
    def analyze_winning_move_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in winning vs losing games.
        
        Returns:
            Dictionary containing winning move pattern analysis
        """
        winning_patterns = defaultdict(lambda: {
            "position_frequency": defaultdict(int),
            "piece_size_frequency": defaultdict(int),
            "move_timing": [],
            "capture_frequency": 0,
            "total_moves": 0,
            "games_count": 0
        })
        
        for game in self.games:
            if game.winner is None:
                continue  # Skip draws
            
            # Analyze winner's moves
            winner_moves = [m for m in game.moves if m.player_color == game.winner]
            loser_moves = [m for m in game.moves if m.player_color != game.winner]
            
            # Winner analysis
            winning_patterns["winner"]["games_count"] += 1
            winning_patterns["winner"]["total_moves"] += len(winner_moves)
            
            for i, move in enumerate(winner_moves):
                winning_patterns["winner"]["position_frequency"][move.to_position] += 1
                winning_patterns["winner"]["piece_size_frequency"][move.piece_size] += 1
                winning_patterns["winner"]["move_timing"].append(move.move_number)
                
                if move.captured_piece_id is not None:
                    winning_patterns["winner"]["capture_frequency"] += 1
            
            # Loser analysis
            winning_patterns["loser"]["games_count"] += 1
            winning_patterns["loser"]["total_moves"] += len(loser_moves)
            
            for i, move in enumerate(loser_moves):
                winning_patterns["loser"]["position_frequency"][move.to_position] += 1
                winning_patterns["loser"]["piece_size_frequency"][move.piece_size] += 1
                winning_patterns["loser"]["move_timing"].append(move.move_number)
                
                if move.captured_piece_id is not None:
                    winning_patterns["loser"]["capture_frequency"] += 1
        
        return dict(winning_patterns)
    
    def analyze_positional_preferences(self) -> Dict[str, Any]:
        """
        Analyze positional preferences across all games.
        
        Returns:
            Dictionary containing positional analysis
        """
        position_stats = defaultdict(lambda: {
            "frequency": 0,
            "wins_from_position": 0,
            "losses_from_position": 0,
            "avg_move_number": 0,
            "piece_sizes": defaultdict(int)
        })
        
        for game in self.games:
            for move in game.moves:
                pos = move.to_position
                position_stats[pos]["frequency"] += 1
                position_stats[pos]["avg_move_number"] += move.move_number
                position_stats[pos]["piece_sizes"][move.piece_size] += 1
                
                # Track if this move contributed to a win
                if game.winner == move.player_color:
                    position_stats[pos]["wins_from_position"] += 1
                elif game.winner is not None:  # Not a draw
                    position_stats[pos]["losses_from_position"] += 1
        
        # Calculate averages and win rates
        for pos, stats in position_stats.items():
            if stats["frequency"] > 0:
                stats["avg_move_number"] /= stats["frequency"]
                total_decided_games = stats["wins_from_position"] + stats["losses_from_position"]
                if total_decided_games > 0:
                    stats["win_rate"] = stats["wins_from_position"] / total_decided_games
                else:
                    stats["win_rate"] = 0.0
        
        return dict(position_stats)
    
    def analyze_capture_patterns(self) -> Dict[str, Any]:
        """
        Analyze piece capture patterns.
        
        Returns:
            Dictionary containing capture analysis
        """
        capture_stats = {
            "total_captures": 0,
            "captures_by_piece_size": defaultdict(int),
            "captures_by_position": defaultdict(int),
            "captures_by_strategy": defaultdict(int),
            "capture_timing": [],
            "games_with_captures": 0,
            "average_captures_per_game": 0
        }
        
        games_with_captures = 0
        
        for game in self.games:
            game_captures = 0
            
            for move in game.moves:
                if move.captured_piece_id is not None:
                    capture_stats["total_captures"] += 1
                    capture_stats["captures_by_piece_size"][move.piece_size] += 1
                    capture_stats["captures_by_position"][move.to_position] += 1
                    capture_stats["capture_timing"].append(move.move_number)
                    game_captures += 1
                    
                    # Get strategy of capturing player
                    if move.player_color in game.player_strategies:
                        strategy = game.player_strategies[move.player_color]
                        capture_stats["captures_by_strategy"][strategy] += 1
            
            if game_captures > 0:
                games_with_captures += 1
        
        capture_stats["games_with_captures"] = games_with_captures
        if len(self.games) > 0:
            capture_stats["average_captures_per_game"] = capture_stats["total_captures"] / len(self.games)
        
        return capture_stats
    
    def create_move_frequency_heatmap(self, save_path: Optional[str] = None) -> None:
        """
        Create a heatmap showing move frequency by board position.
        
        Args:
            save_path: Optional path to save the plot
        """
        # Collect position frequencies
        position_freq = defaultdict(int)
        max_row, max_col = 0, 0
        
        for game in self.games:
            for move in game.moves:
                pos = move.to_position
                position_freq[pos] += 1
                max_row = max(max_row, pos[0])
                max_col = max(max_col, pos[1])
        
        # Create frequency matrix
        freq_matrix = np.zeros((max_row + 1, max_col + 1))
        for (row, col), freq in position_freq.items():
            freq_matrix[row, col] = freq
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(freq_matrix, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Move Frequency'})
        plt.title('Move Frequency Heatmap by Board Position')
        plt.xlabel('Column')
        plt.ylabel('Row')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_strategy_comparison_plot(self, save_path: Optional[str] = None) -> None:
        """
        Create a comparison plot of different strategies.
        
        Args:
            save_path: Optional path to save the plot
        """
        strategy_stats = self.analyze_move_patterns_by_strategy()
        
        if not strategy_stats:
            print("No strategy data available for plotting")
            return
        
        strategies = list(strategy_stats.keys())
        avg_moves = [strategy_stats[s]["average_moves_per_game"] for s in strategies]
        games_count = [strategy_stats[s]["games_count"] for s in strategies]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Average moves per game
        ax1.bar(strategies, avg_moves, color='skyblue')
        ax1.set_title('Average Moves per Game by Strategy')
        ax1.set_ylabel('Average Moves')
        ax1.tick_params(axis='x', rotation=45)
        
        # Games count
        ax2.bar(strategies, games_count, color='lightcoral')
        ax2.set_title('Number of Games by Strategy')
        ax2.set_ylabel('Games Count')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_comprehensive_report(self) -> str:
        """
        Generate a comprehensive analysis report.
        
        Returns:
            String containing the formatted report
        """
        report = []
        report.append("="*60)
        report.append("COMPREHENSIVE MOVE ANALYSIS REPORT")
        report.append("="*60)
        
        # Basic statistics
        total_games = len(self.games)
        total_moves = sum(len(game.moves) for game in self.games)
        report.append(f"Total games analyzed: {total_games}")
        report.append(f"Total moves analyzed: {total_moves}")
        
        if total_games > 0:
            avg_moves_per_game = total_moves / total_games
            report.append(f"Average moves per game: {avg_moves_per_game:.1f}")
        
        report.append("")
        
        # Opening moves analysis
        opening_analysis = self.analyze_opening_moves()
        report.append("OPENING MOVES ANALYSIS")
        report.append("-" * 30)
        report.append("Most common first positions:")
        for i, (pos, count) in enumerate(opening_analysis["most_common_positions"][:5], 1):
            report.append(f"{i}. Position {pos}: {count} times")
        
        report.append("")
        report.append("Most common piece sizes in opening:")
        for size, count in opening_analysis["most_common_piece_sizes"]:
            report.append(f"  {size.name}: {count} times")
        
        report.append("")
        
        # Strategy analysis
        strategy_analysis = self.analyze_move_patterns_by_strategy()
        if strategy_analysis:
            report.append("STRATEGY ANALYSIS")
            report.append("-" * 20)
            for strategy, data in strategy_analysis.items():
                report.append(f"{strategy.upper()} Strategy:")
                report.append(f"  Games played: {data['games_count']}")
                report.append(f"  Avg moves per game: {data['average_moves_per_game']:.1f}")
                
                # Top positions for this strategy
                top_positions = sorted(
                    data["position_preferences"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
                report.append(f"  Favorite positions: {[pos for pos, _ in top_positions]}")
                report.append("")
        
        # Winning patterns
        winning_patterns = self.analyze_winning_move_patterns()
        if "winner" in winning_patterns and "loser" in winning_patterns:
            report.append("WINNING VS LOSING PATTERNS")
            report.append("-" * 30)
            
            winner_data = winning_patterns["winner"]
            loser_data = winning_patterns["loser"]
            
            if winner_data["games_count"] > 0 and loser_data["games_count"] > 0:
                winner_avg = winner_data["total_moves"] / winner_data["games_count"]
                loser_avg = loser_data["total_moves"] / loser_data["games_count"]
                
                report.append(f"Winners average moves per game: {winner_avg:.1f}")
                report.append(f"Losers average moves per game: {loser_avg:.1f}")
                
                winner_captures = winner_data["capture_frequency"] / winner_data["games_count"]
                loser_captures = loser_data["capture_frequency"] / loser_data["games_count"]
                
                report.append(f"Winners average captures per game: {winner_captures:.1f}")
                report.append(f"Losers average captures per game: {loser_captures:.1f}")
        
        report.append("")
        
        # Capture analysis
        capture_analysis = self.analyze_capture_patterns()
        report.append("CAPTURE ANALYSIS")
        report.append("-" * 20)
        report.append(f"Total captures: {capture_analysis['total_captures']}")
        report.append(f"Games with captures: {capture_analysis['games_with_captures']}")
        report.append(f"Average captures per game: {capture_analysis['average_captures_per_game']:.2f}")
        
        if capture_analysis["capture_timing"]:
            avg_capture_timing = np.mean(capture_analysis["capture_timing"])
            report.append(f"Average capture timing (move number): {avg_capture_timing:.1f}")
        
        report.append("")
        report.append("="*60)
        
        return "\n".join(report)
