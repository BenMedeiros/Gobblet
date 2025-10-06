"""
Move tracking and storage for Gobblet game.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from .piece import Piece, PieceColor, PieceSize


@dataclass
class Move:
    """Represents a single move in the game."""
    player_color: PieceColor
    move_type: str  # "place", "move"
    piece_id: int
    piece_size: PieceSize
    from_position: Optional[Tuple[int, int]]  # None for new pieces
    to_position: Tuple[int, int]
    captured_piece_id: Optional[int]  # ID of piece that was covered
    move_number: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert move to dictionary for serialization."""
        return {
            "player_color": self.player_color.value,
            "move_type": self.move_type,
            "piece_id": self.piece_id,
            "piece_size": self.piece_size.value,
            "from_position": self.from_position,
            "to_position": self.to_position,
            "captured_piece_id": self.captured_piece_id,
            "move_number": self.move_number,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Move':
        """Create move from dictionary."""
        return cls(
            player_color=PieceColor(data["player_color"]),
            move_type=data["move_type"],
            piece_id=data["piece_id"],
            piece_size=PieceSize(data["piece_size"]),
            from_position=tuple(data["from_position"]) if data["from_position"] else None,
            to_position=tuple(data["to_position"]),
            captured_piece_id=data["captured_piece_id"],
            move_number=data["move_number"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


@dataclass
class GameRecord:
    """Represents a complete game record."""
    game_id: str
    start_time: datetime
    end_time: Optional[datetime]
    winner: Optional[PieceColor]
    moves: List[Move]
    player_strategies: Dict[PieceColor, str]
    total_moves: int
    game_duration_seconds: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game record to dictionary for serialization."""
        return {
            "game_id": self.game_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "winner": self.winner.value if self.winner else None,
            "moves": [move.to_dict() for move in self.moves],
            "player_strategies": {color.value: strategy for color, strategy in self.player_strategies.items()},
            "total_moves": self.total_moves,
            "game_duration_seconds": self.game_duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameRecord':
        """Create game record from dictionary."""
        return cls(
            game_id=data["game_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            winner=PieceColor(data["winner"]) if data["winner"] else None,
            moves=[Move.from_dict(move_data) for move_data in data["moves"]],
            player_strategies={PieceColor(color): strategy for color, strategy in data["player_strategies"].items()},
            total_moves=data["total_moves"],
            game_duration_seconds=data["game_duration_seconds"]
        )


class MoveTracker:
    """Tracks and stores moves during a game."""
    
    def __init__(self, game_id: str):
        """
        Initialize the move tracker.
        
        Args:
            game_id: Unique identifier for the game
        """
        self.game_id = game_id
        self.moves: List[Move] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.winner: Optional[PieceColor] = None
        self.player_strategies: Dict[PieceColor, str] = {}
        self.move_counter = 0
    
    def record_move(self, 
                   player_color: PieceColor,
                   move_type: str,
                   piece: Piece,
                   from_position: Optional[Tuple[int, int]],
                   to_position: Tuple[int, int],
                   captured_piece: Optional[Piece] = None) -> None:
        """
        Record a move in the game.
        
        Args:
            player_color: Color of the player making the move
            move_type: Type of move ("place" or "move")
            piece: The piece being moved
            from_position: Starting position (None for new pieces)
            to_position: Ending position
            captured_piece: Piece that was captured/covered
        """
        self.move_counter += 1
        
        move = Move(
            player_color=player_color,
            move_type=move_type,
            piece_id=piece.piece_id,
            piece_size=piece.size,
            from_position=from_position,
            to_position=to_position,
            captured_piece_id=captured_piece.piece_id if captured_piece else None,
            move_number=self.move_counter,
            timestamp=datetime.now()
        )
        
        self.moves.append(move)
    
    def set_player_strategy(self, color: PieceColor, strategy: str) -> None:
        """
        Set the strategy for a player.
        
        Args:
            color: Player color
            strategy: Strategy name/description
        """
        self.player_strategies[color] = strategy
    
    def end_game(self, winner: Optional[PieceColor]) -> None:
        """
        Mark the game as ended.
        
        Args:
            winner: The winning player color, or None for a draw
        """
        self.end_time = datetime.now()
        self.winner = winner
    
    def get_game_record(self) -> GameRecord:
        """
        Get the complete game record.
        
        Returns:
            GameRecord object containing all game data
        """
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return GameRecord(
            game_id=self.game_id,
            start_time=self.start_time,
            end_time=self.end_time,
            winner=self.winner,
            moves=self.moves.copy(),
            player_strategies=self.player_strategies.copy(),
            total_moves=len(self.moves),
            game_duration_seconds=duration
        )
    
    def get_moves_by_player(self, color: PieceColor) -> List[Move]:
        """
        Get all moves made by a specific player.
        
        Args:
            color: Player color
            
        Returns:
            List of moves made by the player
        """
        return [move for move in self.moves if move.player_color == color]
    
    def get_move_history_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the move history.
        
        Returns:
            Dictionary containing move statistics
        """
        if not self.moves:
            return {"total_moves": 0}
        
        light_moves = len(self.get_moves_by_player(PieceColor.LIGHT))
        dark_moves = len(self.get_moves_by_player(PieceColor.DARK))
        
        place_moves = len([m for m in self.moves if m.move_type == "place"])
        move_moves = len([m for m in self.moves if m.move_type == "move"])
        
        captures = len([m for m in self.moves if m.captured_piece_id is not None])
        
        return {
            "total_moves": len(self.moves),
            "light_moves": light_moves,
            "dark_moves": dark_moves,
            "place_moves": place_moves,
            "move_moves": move_moves,
            "captures": captures,
            "average_move_time": self._calculate_average_move_time()
        }
    
    def _calculate_average_move_time(self) -> Optional[float]:
        """Calculate average time between moves."""
        if len(self.moves) < 2:
            return None
        
        total_time = 0
        for i in range(1, len(self.moves)):
            time_diff = (self.moves[i].timestamp - self.moves[i-1].timestamp).total_seconds()
            total_time += time_diff
        
        return total_time / (len(self.moves) - 1)


class GameDataManager:
    """Manages storage and retrieval of game data."""
    
    def __init__(self, data_file: str = "data/games.json"):
        """
        Initialize the data manager.
        
        Args:
            data_file: Path to the data file
        """
        self.data_file = data_file
        self.games: List[GameRecord] = []
    
    def save_game(self, game_record: GameRecord) -> None:
        """
        Save a game record.
        
        Args:
            game_record: The game record to save
        """
        self.games.append(game_record)
        self._save_to_file()
    
    def load_games(self) -> List[GameRecord]:
        """
        Load all game records from file.
        
        Returns:
            List of game records
        """
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.games = [GameRecord.from_dict(record) for record in data]
        except FileNotFoundError:
            self.games = []
        except json.JSONDecodeError:
            print(f"Error reading {self.data_file}, starting with empty games list")
            self.games = []
        
        return self.games
    
    def get_games_by_winner(self, winner: Optional[PieceColor]) -> List[GameRecord]:
        """
        Get games filtered by winner.
        
        Args:
            winner: Winner to filter by (None for draws)
            
        Returns:
            List of matching game records
        """
        return [game for game in self.games if game.winner == winner]
    
    def get_games_by_strategy(self, color: PieceColor, strategy: str) -> List[GameRecord]:
        """
        Get games where a specific player used a specific strategy.
        
        Args:
            color: Player color
            strategy: Strategy name
            
        Returns:
            List of matching game records
        """
        return [game for game in self.games 
                if color in game.player_strategies and game.player_strategies[color] == strategy]
    
    def _save_to_file(self) -> None:
        """Save games to file."""
        try:
            import os
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'w') as f:
                json.dump([game.to_dict() for game in self.games], f, indent=2)
        except Exception as e:
            print(f"Error saving games to {self.data_file}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics from all games.
        
        Returns:
            Dictionary containing game statistics
        """
        if not self.games:
            return {"total_games": 0}
        
        total_games = len(self.games)
        light_wins = len(self.get_games_by_winner(PieceColor.LIGHT))
        dark_wins = len(self.get_games_by_winner(PieceColor.DARK))
        draws = len(self.get_games_by_winner(None))
        
        total_moves = sum(game.total_moves for game in self.games)
        avg_moves_per_game = total_moves / total_games if total_games > 0 else 0
        
        completed_games = [game for game in self.games if game.game_duration_seconds is not None]
        avg_duration = sum(game.game_duration_seconds for game in completed_games) / len(completed_games) if completed_games else 0
        
        return {
            "total_games": total_games,
            "light_wins": light_wins,
            "dark_wins": dark_wins,
            "draws": draws,
            "light_win_rate": light_wins / total_games if total_games > 0 else 0,
            "dark_win_rate": dark_wins / total_games if total_games > 0 else 0,
            "average_moves_per_game": avg_moves_per_game,
            "average_game_duration": avg_duration,
            "total_moves_recorded": total_moves
        }
