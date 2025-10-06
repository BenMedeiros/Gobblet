"""
Player classes for Gobblet game.
"""

import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from .piece import Piece, PieceColor, PieceSize
from .board import Board


class Player(ABC):
    """Abstract base class for all players."""
    
    def __init__(self, color: PieceColor, name: str):
        """
        Initialize the player.
        
        Args:
            color: The player's color
            name: The player's name
        """
        self.color = color
        self.name = name
        self.pieces: List[Piece] = []
        self.strategy_name = "base"
        self._init_pieces()
    
    def _init_pieces(self) -> None:
        """Initialize the player's pieces."""
        piece_id = 0 if self.color == PieceColor.LIGHT else 12
        
        # Each player gets 3 pieces of each size (small, medium, large)
        for size in PieceSize:
            for _ in range(3):
                self.pieces.append(Piece(self.color, size, piece_id))
                piece_id += 1
    
    def get_available_pieces(self) -> List[Piece]:
        """
        Get pieces that are not on the board.
        
        Returns:
            List of available pieces
        """
        return [piece for piece in self.pieces if piece.position is None]
    
    def get_pieces_on_board(self, board: Board) -> List[Tuple[Piece, Tuple[int, int]]]:
        """
        Get pieces that are currently on the board.
        
        Args:
            board: The game board
            
        Returns:
            List of (piece, position) tuples for pieces on the board
        """
        pieces_on_board = []
        for row in range(board.size):
            for col in range(board.size):
                top_piece = board.get_top_piece(row, col)
                if top_piece and top_piece in self.pieces:
                    pieces_on_board.append((top_piece, (row, col)))
        
        return pieces_on_board
    
    @abstractmethod
    def choose_move(self, board: Board) -> Tuple[str, Dict[str, Any]]:
        """
        Choose the next move.
        
        Args:
            board: Current board state
            
        Returns:
            Tuple of (move_type, move_data) where:
            - move_type is "place" or "move"
            - move_data contains the move details
        """
        pass
    
    def __str__(self) -> str:
        """String representation of the player."""
        return f"{self.name} ({self.color.value})"


class RandomPlayer(Player):
    """Player that makes random moves."""
    
    def __init__(self, color: PieceColor, name: str = None):
        """Initialize random player."""
        if name is None:
            name = f"Random {color.value.capitalize()}"
        super().__init__(color, name)
        self.strategy_name = "random"
    
    def choose_move(self, board: Board) -> Tuple[str, Dict[str, Any]]:
        """Choose a random valid move."""
        available_pieces = self.get_available_pieces()
        pieces_on_board = self.get_pieces_on_board(board)
        
        possible_moves = []
        
        # Add place moves for available pieces (using new Gobblet rules)
        if available_pieces:
            for piece in available_pieces:
                valid_positions = board.get_valid_moves_for_new_piece(self.color, piece.size)
                for pos in valid_positions:
                    possible_moves.append(("place", {
                        "piece": piece,
                        "position": pos
                    }))
        
        # Add move moves for pieces on board (existing pieces have more flexibility)
        for piece, current_pos in pieces_on_board:
            valid_positions = board.get_valid_moves_for_existing_piece(self.color, piece.size)
            for new_pos in valid_positions:
                if new_pos != current_pos:
                    possible_moves.append(("move", {
                        "piece": piece,
                        "from_position": current_pos,
                        "to_position": new_pos
                    }))
        
        if not possible_moves:
            # No valid moves available
            return ("place", {"piece": None, "position": None})
        
        return random.choice(possible_moves)


class GreedyPlayer(Player):
    """Player that prioritizes winning moves and blocking opponent wins."""
    
    def __init__(self, color: PieceColor, name: str = None):
        """Initialize greedy player."""
        if name is None:
            name = f"Greedy {color.value.capitalize()}"
        super().__init__(color, name)
        self.strategy_name = "greedy"
    
    def choose_move(self, board: Board) -> Tuple[str, Dict[str, Any]]:
        """Choose a move that prioritizes winning or blocking."""
        # First, check for winning moves
        winning_move = self._find_winning_move(board)
        if winning_move:
            return winning_move
        
        # Then, check for blocking opponent's winning moves
        blocking_move = self._find_blocking_move(board)
        if blocking_move:
            return blocking_move
        
        # Otherwise, make a strategic move
        return self._make_strategic_move(board)
    
    def _find_winning_move(self, board: Board) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find a move that wins the game immediately."""
        return self._find_move_for_color(board, self.color)
    
    def _find_blocking_move(self, board: Board) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find a move that blocks the opponent from winning."""
        opponent_color = PieceColor.DARK if self.color == PieceColor.LIGHT else PieceColor.LIGHT
        
        # Find where opponent could win
        for row in range(board.size):
            for col in range(board.size):
                # Try placing our pieces to block
                available_pieces = self.get_available_pieces()
                for piece in available_pieces:
                    if self._would_block_win(board, piece, (row, col), opponent_color):
                        return ("place", {"piece": piece, "position": (row, col)})
                
                # Try moving our pieces to block
                pieces_on_board = self.get_pieces_on_board(board)
                for piece, current_pos in pieces_on_board:
                    if self._would_block_win(board, piece, (row, col), opponent_color):
                        return ("move", {
                            "piece": piece,
                            "from_position": current_pos,
                            "to_position": (row, col)
                        })
        
        return None
    
    def _find_move_for_color(self, board: Board, color: PieceColor) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find a winning move for the specified color."""
        # Check all possible positions
        for row in range(board.size):
            for col in range(board.size):
                # Try placing available pieces
                if color == self.color:
                    available_pieces = self.get_available_pieces()
                    for piece in available_pieces:
                        if self._would_win(board, piece, (row, col)):
                            return ("place", {"piece": piece, "position": (row, col)})
                    
                    # Try moving pieces on board
                    pieces_on_board = self.get_pieces_on_board(board)
                    for piece, current_pos in pieces_on_board:
                        if self._would_win(board, piece, (row, col)):
                            return ("move", {
                                "piece": piece,
                                "from_position": current_pos,
                                "to_position": (row, col)
                            })
        
        return None
    
    def _would_win(self, board: Board, piece: Piece, position: Tuple[int, int]) -> bool:
        """Check if placing/moving a piece would result in a win."""
        row, col = position
        
        # Create a copy of the board to test the move
        test_board = board.copy()
        
        # If piece is on board, remove it first
        if piece.position:
            test_board.remove_piece(piece.position[0], piece.position[1])
        
        # Try placing the piece
        if test_board.place_piece(piece, row, col):
            return test_board.check_winner() == self.color
        
        return False
    
    def _would_block_win(self, board: Board, piece: Piece, position: Tuple[int, int], opponent_color: PieceColor) -> bool:
        """Check if placing a piece would block opponent's win."""
        row, col = position
        
        # First check if opponent could win at this position
        test_board = board.copy()
        
        # Simulate opponent placing a piece here
        # We'll check if any opponent piece placement here would win
        existing_piece = test_board.get_top_piece(row, col)
        if existing_piece and existing_piece.color != opponent_color:
            return False  # Can't place opponent piece here
        
        # Check if our piece placement would prevent opponent win
        if piece.position:
            test_board.remove_piece(piece.position[0], piece.position[1])
        
        return test_board.place_piece(piece, row, col)
    
    def _make_strategic_move(self, board: Board) -> Tuple[str, Dict[str, Any]]:
        """Make a strategic move when no immediate win/block is needed."""
        # Prefer center positions and larger pieces
        center_positions = self._get_center_positions(board)
        
        available_pieces = self.get_available_pieces()
        if available_pieces:
            # Prefer larger pieces
            available_pieces.sort(key=lambda p: p.size.value, reverse=True)
            
            for piece in available_pieces:
                # Try center positions first (using new piece rules)
                valid_positions = board.get_valid_moves_for_new_piece(self.color, piece.size)
                center_valid = [pos for pos in center_positions if pos in valid_positions]
                
                for pos in center_valid:
                    return ("place", {"piece": piece, "position": pos})
                
                # Then try any valid position for new pieces
                for pos in valid_positions:
                    return ("place", {"piece": piece, "position": pos})
        
        # Fall back to random move
        random_player = RandomPlayer(self.color)
        return random_player.choose_move(board)
    
    def _get_center_positions(self, board: Board) -> List[Tuple[int, int]]:
        """Get positions closer to the center of the board."""
        center = board.size // 2
        positions = []
        
        # Add positions in order of distance from center
        for distance in range(center + 1):
            for row in range(board.size):
                for col in range(board.size):
                    if abs(row - center) + abs(col - center) == distance:
                        positions.append((row, col))
        
        return positions


class DefensivePlayer(Player):
    """Player that focuses on defensive play and board control."""
    
    def __init__(self, color: PieceColor, name: str = None):
        """Initialize defensive player."""
        if name is None:
            name = f"Defensive {color.value.capitalize()}"
        super().__init__(color, name)
        self.strategy_name = "defensive"
    
    def choose_move(self, board: Board) -> Tuple[str, Dict[str, Any]]:
        """Choose a defensive move."""
        # Check for winning moves first
        winning_move = self._find_winning_move(board)
        if winning_move:
            return winning_move
        
        # Priority on blocking opponent
        blocking_move = self._find_blocking_move(board)
        if blocking_move:
            return blocking_move
        
        # Focus on controlling key positions
        return self._make_defensive_move(board)
    
    def _find_winning_move(self, board: Board) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find immediate winning move."""
        for row in range(board.size):
            for col in range(board.size):
                available_pieces = self.get_available_pieces()
                for piece in available_pieces:
                    test_board = board.copy()
                    if test_board.place_piece(piece, row, col):
                        if test_board.check_winner() == self.color:
                            return ("place", {"piece": piece, "position": (row, col)})
                
                pieces_on_board = self.get_pieces_on_board(board)
                for piece, current_pos in pieces_on_board:
                    test_board = board.copy()
                    test_board.remove_piece(current_pos[0], current_pos[1])
                    if test_board.place_piece(piece, row, col):
                        if test_board.check_winner() == self.color:
                            return ("move", {
                                "piece": piece,
                                "from_position": current_pos,
                                "to_position": (row, col)
                            })
        
        return None
    
    def _find_blocking_move(self, board: Board) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find move that blocks opponent."""
        # Similar to greedy player but more thorough
        opponent_color = PieceColor.DARK if self.color == PieceColor.LIGHT else PieceColor.LIGHT
        
        # Check all positions for potential opponent wins
        for row in range(board.size):
            for col in range(board.size):
                # Test if opponent could win by placing at this position
                if self._opponent_could_win_here(board, (row, col), opponent_color):
                    # Try to block with our pieces
                    available_pieces = self.get_available_pieces()
                    for piece in available_pieces:
                        existing_piece = board.get_top_piece(row, col)
                        if existing_piece is None or piece.can_cover(existing_piece):
                            return ("place", {"piece": piece, "position": (row, col)})
        
        return None
    
    def _opponent_could_win_here(self, board: Board, position: Tuple[int, int], opponent_color: PieceColor) -> bool:
        """Check if opponent could win by playing at this position."""
        row, col = position
        test_board = board.copy()
        
        # Simulate opponent placing different sizes here
        for size in PieceSize:
            test_piece = Piece(opponent_color, size, -1)  # Temporary piece
            if test_board.place_piece(test_piece, row, col):
                if test_board.check_winner() == opponent_color:
                    return True
                test_board.remove_piece(row, col)  # Remove test piece
        
        return False
    
    def _make_defensive_move(self, board: Board) -> Tuple[str, Dict[str, Any]]:
        """Make a defensive move focusing on board control."""
        # Prioritize controlling corners and center
        strategic_positions = self._get_strategic_positions(board)
        
        available_pieces = self.get_available_pieces()
        if available_pieces:
            # Prefer medium to large pieces for defense
            available_pieces.sort(key=lambda p: p.size.value, reverse=True)
            
            for piece in available_pieces:
                for pos in strategic_positions:
                    existing_piece = board.get_top_piece(pos[0], pos[1])
                    if existing_piece is None or piece.can_cover(existing_piece):
                        return ("place", {"piece": piece, "position": pos})
        
        # Fall back to any valid move
        return self._make_any_valid_move(board)
    
    def _get_strategic_positions(self, board: Board) -> List[Tuple[int, int]]:
        """Get positions in order of strategic importance."""
        positions = []
        
        # Corners first
        corners = [(0, 0), (0, board.size-1), (board.size-1, 0), (board.size-1, board.size-1)]
        positions.extend(corners)
        
        # Center positions
        center = board.size // 2
        if board.size % 2 == 1:
            positions.append((center, center))
        else:
            positions.extend([(center-1, center-1), (center-1, center), 
                             (center, center-1), (center, center)])
        
        # Edges
        for i in range(board.size):
            positions.extend([(0, i), (board.size-1, i), (i, 0), (i, board.size-1)])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_positions = []
        for pos in positions:
            if pos not in seen:
                seen.add(pos)
                unique_positions.append(pos)
        
        return unique_positions
    
    def _make_any_valid_move(self, board: Board) -> Tuple[str, Dict[str, Any]]:
        """Make any valid move as fallback."""
        random_player = RandomPlayer(self.color)
        return random_player.choose_move(board)
