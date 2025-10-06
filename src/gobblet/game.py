"""
Core game logic for Gobblet.
"""

import uuid
from typing import Optional, Tuple, Dict, Any
from .board import Board
from .player import Player, PieceColor
from .moves import MoveTracker
from .piece import Piece


class GobbletGame:
    """Main game class for Gobblet."""
    
    def __init__(self, light_player: Player, dark_player: Player, board_size: int = 4):
        """
        Initialize a new game.
        
        Args:
            light_player: Player playing with light pieces
            dark_player: Player playing with dark pieces
            board_size: Size of the board (default 4x4)
        """
        self.game_id = str(uuid.uuid4())
        self.board = Board(board_size)
        self.light_player = light_player
        self.dark_player = dark_player
        self.current_player = light_player  # Light always goes first
        self.move_tracker = MoveTracker(self.game_id)
        self.game_over = False
        self.winner: Optional[PieceColor] = None
        self.max_turns = 200  # Prevent infinite games
        self.turn_count = 0
        
        # Set player strategies in move tracker
        self.move_tracker.set_player_strategy(light_player.color, light_player.strategy_name)
        self.move_tracker.set_player_strategy(dark_player.color, dark_player.strategy_name)
    
    def play_turn(self) -> bool:
        """
        Play one turn of the game.
        
        Returns:
            True if the game should continue, False if game is over
        """
        if self.game_over:
            return False
        
        self.turn_count += 1
        
        # Check for max turns (draw condition)
        if self.turn_count > self.max_turns:
            self._end_game(None)
            return False
        
        # Get the current player's move
        try:
            move_type, move_data = self.current_player.choose_move(self.board)
        except Exception as e:
            print(f"Error getting move from {self.current_player}: {e}")
            self._end_game(self._get_opponent_color())
            return False
        
        # Execute the move
        if not self._execute_move(move_type, move_data):
            # Invalid move, current player loses
            self._end_game(self._get_opponent_color())
            return False
        
        # Check for winner
        winner = self.board.check_winner()
        if winner:
            self._end_game(winner)
            return False
        
        # Check for draw (board full with no winner)
        if self.board.is_board_full():
            self._end_game(None)
            return False
        
        # Switch players
        self._switch_player()
        return True
    
    def play_game(self) -> Optional[PieceColor]:
        """
        Play a complete game.
        
        Returns:
            The winning color, or None for a draw
        """
        while not self.game_over:
            if not self.play_turn():
                break
        
        return self.winner
    
    def _execute_move(self, move_type: str, move_data: Dict[str, Any]) -> bool:
        """
        Execute a move on the board.
        
        Args:
            move_type: Type of move ("place" or "move")
            move_data: Move details
            
        Returns:
            True if move was successful, False otherwise
        """
        if move_type == "place":
            return self._execute_place_move(move_data)
        elif move_type == "move":
            return self._execute_piece_move(move_data)
        else:
            return False
    
    def _execute_place_move(self, move_data: Dict[str, Any]) -> bool:
        """Execute a piece placement move."""
        piece = move_data.get("piece")
        position = move_data.get("position")
        
        if not piece or not position:
            return False
        
        # Verify piece belongs to current player
        if piece not in self.current_player.pieces:
            return False
        
        # Verify piece is available (not on board)
        if piece.position is not None:
            return False
        
        row, col = position
        
        # Get piece that might be captured
        captured_piece = self.board.get_top_piece(row, col)
        
        # Try to place the piece
        if self.board.place_piece(piece, row, col):
            # Record the move
            self.move_tracker.record_move(
                player_color=self.current_player.color,
                move_type="place",
                piece=piece,
                from_position=None,
                to_position=position,
                captured_piece=captured_piece
            )
            return True
        
        return False
    
    def _execute_piece_move(self, move_data: Dict[str, Any]) -> bool:
        """Execute a piece movement move."""
        piece = move_data.get("piece")
        from_position = move_data.get("from_position")
        to_position = move_data.get("to_position")
        
        if not piece or not from_position or not to_position:
            return False
        
        # Verify piece belongs to current player
        if piece not in self.current_player.pieces:
            return False
        
        # Verify piece is at the from_position
        from_row, from_col = from_position
        current_top_piece = self.board.get_top_piece(from_row, from_col)
        if current_top_piece != piece:
            return False
        
        to_row, to_col = to_position
        
        # Get piece that might be captured at destination
        captured_piece = self.board.get_top_piece(to_row, to_col)
        
        # Remove piece from current position
        removed_piece = self.board.remove_piece(from_row, from_col)
        if removed_piece != piece:
            # Something went wrong, put piece back
            if removed_piece:
                self.board.place_piece(removed_piece, from_row, from_col)
            return False
        
        # Try to place piece at new position
        if self.board.place_piece(piece, to_row, to_col):
            # Record the move
            self.move_tracker.record_move(
                player_color=self.current_player.color,
                move_type="move",
                piece=piece,
                from_position=from_position,
                to_position=to_position,
                captured_piece=captured_piece
            )
            return True
        else:
            # Failed to place at new position, put piece back
            self.board.place_piece(piece, from_row, from_col)
            return False
    
    def _switch_player(self) -> None:
        """Switch to the other player."""
        self.current_player = (self.dark_player if self.current_player == self.light_player 
                             else self.light_player)
    
    def _get_opponent_color(self) -> PieceColor:
        """Get the color of the opponent of the current player."""
        return (PieceColor.DARK if self.current_player.color == PieceColor.LIGHT 
                else PieceColor.LIGHT)
    
    def _end_game(self, winner: Optional[PieceColor]) -> None:
        """
        End the game.
        
        Args:
            winner: The winning color, or None for a draw
        """
        self.game_over = True
        self.winner = winner
        self.move_tracker.end_game(winner)
    
    def get_game_state(self) -> Dict[str, Any]:
        """
        Get the current game state.
        
        Returns:
            Dictionary containing game state information
        """
        return {
            "game_id": self.game_id,
            "turn_count": self.turn_count,
            "current_player": str(self.current_player),
            "game_over": self.game_over,
            "winner": self.winner.value if self.winner else None,
            "board_state": str(self.board),
            "light_pieces_remaining": len(self.light_player.get_available_pieces()),
            "dark_pieces_remaining": len(self.dark_player.get_available_pieces()),
            "move_count": len(self.move_tracker.moves)
        }
    
    def get_move_history(self) -> Dict[str, Any]:
        """Get the move history for this game."""
        return self.move_tracker.get_move_history_summary()
    
    def get_game_record(self):
        """Get the complete game record."""
        return self.move_tracker.get_game_record()
    
    def __str__(self) -> str:
        """String representation of the game."""
        state = f"Game {self.game_id[:8]}...\n"
        state += f"Turn {self.turn_count}: {self.current_player}\n"
        state += str(self.board)
        
        if self.game_over:
            if self.winner:
                state += f"\nWinner: {self.winner.value.capitalize()}"
            else:
                state += "\nGame ended in a draw"
        
        return state
