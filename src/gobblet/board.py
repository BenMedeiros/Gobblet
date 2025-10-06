"""
Board representation for Gobblet game.
"""

from typing import List, Optional, Tuple, Set
from .piece import Piece, PieceColor


class BoardPosition:
    """Represents a position on the board that can hold multiple pieces."""
    
    def __init__(self):
        """Initialize an empty board position."""
        self.pieces: List[Piece] = []  # Stack of pieces, top piece is last
    
    def add_piece(self, piece: Piece) -> bool:
        """
        Add a piece to this position.
        
        Args:
            piece: The piece to add
            
        Returns:
            True if the piece was successfully added
        """
        if self.pieces and not piece.can_cover(self.top_piece()):
            return False
        
        self.pieces.append(piece)
        piece.position = None  # Will be set by board
        return True
    
    def remove_top_piece(self) -> Optional[Piece]:
        """
        Remove and return the top piece.
        
        Returns:
            The top piece, or None if empty
        """
        if not self.pieces:
            return None
        
        piece = self.pieces.pop()
        piece.position = None
        return piece
    
    def top_piece(self) -> Optional[Piece]:
        """
        Get the top piece without removing it.
        
        Returns:
            The top piece, or None if empty
        """
        return self.pieces[-1] if self.pieces else None
    
    def is_empty(self) -> bool:
        """Check if the position is empty."""
        return len(self.pieces) == 0
    
    def piece_count(self) -> int:
        """Get the number of pieces at this position."""
        return len(self.pieces)
    
    def has_piece_of_color(self, color: PieceColor) -> bool:
        """Check if the top piece belongs to the given color."""
        top = self.top_piece()
        return top is not None and top.color == color


class Board:
    """Represents the Gobblet game board."""
    
    def __init__(self, size: int = 4):
        """
        Initialize the board.
        
        Args:
            size: The size of the board (default 4x4)
        """
        self.size = size
        self.positions = [[BoardPosition() for _ in range(size)] for _ in range(size)]
    
    def place_piece(self, piece: Piece, row: int, col: int) -> bool:
        """
        Place a piece on the board.
        
        Args:
            piece: The piece to place
            row: Row position (0-indexed)
            col: Column position (0-indexed)
            
        Returns:
            True if the piece was successfully placed
        """
        if not self._is_valid_position(row, col):
            return False
        
        if self.positions[row][col].add_piece(piece):
            piece.position = (row, col)
            return True
        
        return False
    
    def remove_piece(self, row: int, col: int) -> Optional[Piece]:
        """
        Remove the top piece from a position.
        
        Args:
            row: Row position
            col: Column position
            
        Returns:
            The removed piece, or None if no piece to remove
        """
        if not self._is_valid_position(row, col):
            return None
        
        return self.positions[row][col].remove_top_piece()
    
    def get_top_piece(self, row: int, col: int) -> Optional[Piece]:
        """
        Get the top piece at a position.
        
        Args:
            row: Row position
            col: Column position
            
        Returns:
            The top piece, or None if empty or invalid position
        """
        if not self._is_valid_position(row, col):
            return None
        
        return self.positions[row][col].top_piece()
    
    def is_position_empty(self, row: int, col: int) -> bool:
        """Check if a position is empty."""
        if not self._is_valid_position(row, col):
            return False
        
        return self.positions[row][col].is_empty()
    
    def check_winner(self) -> Optional[PieceColor]:
        """
        Check if there's a winner on the board.
        
        Returns:
            The winning color, or None if no winner
        """
        # Check rows
        for row in range(self.size):
            winner = self._check_line([(row, col) for col in range(self.size)])
            if winner:
                return winner
        
        # Check columns
        for col in range(self.size):
            winner = self._check_line([(row, col) for row in range(self.size)])
            if winner:
                return winner
        
        # Check diagonals
        winner = self._check_line([(i, i) for i in range(self.size)])
        if winner:
            return winner
        
        winner = self._check_line([(i, self.size - 1 - i) for i in range(self.size)])
        if winner:
            return winner
        
        return None
    
    def is_board_full(self) -> bool:
        """Check if the board is full (no empty positions)."""
        for row in range(self.size):
            for col in range(self.size):
                if self.is_position_empty(row, col):
                    return False
        return True
    
    def get_valid_moves(self, color: PieceColor) -> List[Tuple[int, int]]:
        """
        Get all valid positions where a piece of the given color can be placed.
        
        Args:
            color: The color of the piece to place
            
        Returns:
            List of valid (row, col) positions
        """
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_position_empty(row, col):
                    valid_moves.append((row, col))
                else:
                    # Can place if we can cover the top piece
                    top_piece = self.get_top_piece(row, col)
                    if top_piece and top_piece.color != color:
                        valid_moves.append((row, col))
        
        return valid_moves
    
    def get_moveable_pieces(self, color: PieceColor) -> List[Tuple[int, int]]:
        """
        Get positions of pieces that can be moved by the given color.
        
        Args:
            color: The color of pieces to find
            
        Returns:
            List of (row, col) positions with moveable pieces
        """
        moveable = []
        for row in range(self.size):
            for col in range(self.size):
                top_piece = self.get_top_piece(row, col)
                if top_piece and top_piece.color == color:
                    moveable.append((row, col))
        
        return moveable
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board(self.size)
        for row in range(self.size):
            for col in range(self.size):
                for piece in self.positions[row][col].pieces:
                    # Create a copy of the piece
                    new_piece = Piece(piece.color, piece.size, piece.piece_id)
                    new_board.place_piece(new_piece, row, col)
        
        return new_board
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if the given position is valid."""
        return 0 <= row < self.size and 0 <= col < self.size
    
    def _check_line(self, positions: List[Tuple[int, int]]) -> Optional[PieceColor]:
        """
        Check if a line of positions has a winner.
        
        Args:
            positions: List of (row, col) positions to check
            
        Returns:
            The winning color, or None if no winner
        """
        if len(positions) < self.size:
            return None
        
        first_piece = self.get_top_piece(positions[0][0], positions[0][1])
        if not first_piece:
            return None
        
        color = first_piece.color
        for row, col in positions[1:]:
            piece = self.get_top_piece(row, col)
            if not piece or piece.color != color:
                return None
        
        return color
    
    def __str__(self) -> str:
        """String representation of the board."""
        result = []
        for row in range(self.size):
            row_str = []
            for col in range(self.size):
                top_piece = self.get_top_piece(row, col)
                if top_piece:
                    row_str.append(str(top_piece))
                else:
                    row_str.append("--")
            result.append(" | ".join(row_str))
        
        return "\n" + "-" * (self.size * 5 - 1) +"\n" + "\n".join(result) + "\n" + "-" * (self.size * 5 - 1)
