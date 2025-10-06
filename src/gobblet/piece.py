"""
Piece representation for Gobblet game.
"""

from enum import Enum
from typing import Optional


class PieceSize(Enum):
    """Enumeration for piece sizes."""
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


class PieceColor(Enum):
    """Enumeration for piece colors."""
    LIGHT = "light"
    DARK = "dark"


class Piece:
    """Represents a Gobblet piece."""
    
    def __init__(self, color: PieceColor, size: PieceSize, piece_id: int):
        """
        Initialize a piece.
        
        Args:
            color: The color of the piece
            size: The size of the piece
            piece_id: Unique identifier for the piece
        """
        self.color = color
        self.size = size
        self.piece_id = piece_id
        self.position: Optional[tuple] = None  # (row, col) on board, None if off-board
    
    def can_cover(self, other_piece: 'Piece') -> bool:
        """
        Check if this piece can cover another piece.
        
        Args:
            other_piece: The piece to potentially cover
            
        Returns:
            True if this piece can cover the other piece
        """
        return self.size.value > other_piece.size.value
    
    def __str__(self) -> str:
        """String representation of the piece."""
        color_char = 'L' if self.color == PieceColor.LIGHT else 'D'
        size_char = str(self.size.value)
        return f"{color_char}{size_char}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Piece(color={self.color.value}, size={self.size.value}, id={self.piece_id})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on piece ID."""
        if not isinstance(other, Piece):
            return False
        return self.piece_id == other.piece_id
    
    def __hash__(self) -> int:
        """Hash based on piece ID."""
        return hash(self.piece_id)
