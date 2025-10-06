"""
Board representation for Gobblet game.
"""

from typing import List, Optional, Tuple, Set
from .piece import Piece, PieceColor, PieceSize


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
    
    def place_piece(self, piece: Piece, row: int, col: int, is_new_piece: bool = True) -> bool:
        """
        Place a piece on the board following Gobblet rules.
        
        Args:
            piece: The piece to place
            row: Row position (0-indexed)
            col: Column position (0-indexed)
            is_new_piece: True if placing a new piece from off-board, False if moving existing piece
            
        Returns:
            True if the piece was successfully placed
        """
        if not self._is_valid_position(row, col):
            return False
        
        # Check if placement is valid according to Gobblet rules
        if not self._is_placement_valid(piece, row, col, is_new_piece):
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
    
    def get_valid_moves_for_new_piece(self, color: PieceColor, piece_size: PieceSize) -> List[Tuple[int, int]]:
        """
        Get all valid positions where a NEW piece can be placed (following Gobblet rules).
        
        Args:
            color: The color of the piece to place
            piece_size: The size of the piece to place
            
        Returns:
            List of valid (row, col) positions for new pieces
        """
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_position_empty(row, col):
                    # New pieces can always go on empty spaces
                    valid_moves.append((row, col))
                else:
                    # New pieces can only cover opponent pieces if blocking a 3-in-a-row threat
                    top_piece = self.get_top_piece(row, col)
                    if (top_piece and 
                        top_piece.color != color and 
                        piece_size.value > top_piece.size.value and
                        self._is_blocking_three_in_row(row, col, top_piece.color)):
                        valid_moves.append((row, col))
        
        return valid_moves
    
    def get_valid_moves_for_existing_piece(self, color: PieceColor, piece_size: PieceSize) -> List[Tuple[int, int]]:
        """
        Get all valid positions where an EXISTING piece can be moved.
        
        Args:
            color: The color of the piece to move
            piece_size: The size of the piece to move
            
        Returns:
            List of valid (row, col) positions for existing pieces
        """
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_position_empty(row, col):
                    valid_moves.append((row, col))
                else:
                    # Existing pieces can cover any opponent piece they're larger than
                    top_piece = self.get_top_piece(row, col)
                    if (top_piece and 
                        top_piece.color != color and 
                        piece_size.value > top_piece.size.value):
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
                    # When copying, we treat pieces as existing pieces (not new)
                    new_board.place_piece(new_piece, row, col, is_new_piece=False)
        
        return new_board
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if the given position is valid."""
        return 0 <= row < self.size and 0 <= col < self.size
    
    def _is_placement_valid(self, piece: Piece, row: int, col: int, is_new_piece: bool) -> bool:
        """
        Check if piece placement follows Gobblet rules.
        
        Args:
            piece: The piece being placed
            row: Target row
            col: Target column  
            is_new_piece: True if placing from off-board, False if moving existing piece
            
        Returns:
            True if placement is valid according to Gobblet rules
        """
        position = self.positions[row][col]
        
        # If position is empty, always valid
        if position.is_empty():
            return True
        
        top_piece = position.top_piece()
        
        # Can't place on your own piece
        if top_piece.color == piece.color:
            return False
        
        # Must be able to cover (larger piece covers smaller)
        if not piece.can_cover(top_piece):
            return False
        
        # NEW PIECE RULE: Can only place new pieces on empty spaces
        # EXCEPTION: Can cover opponent piece if they have 3-in-a-row (threatening win)
        if is_new_piece:
            # Check if covering opponent's piece that's part of a 3-in-a-row threat
            if self._is_blocking_three_in_row(row, col, top_piece.color):
                return True
            else:
                # New pieces can only go on empty spaces (already checked above)
                return False
        
        # Moving existing pieces can cover opponent pieces normally
        return True
    
    def _is_blocking_three_in_row(self, row: int, col: int, opponent_color: PieceColor) -> bool:
        """
        Check if position (row, col) is part of opponent's 3-in-a-row that could win next turn.
        
        Args:
            row: Row position
            col: Column position
            opponent_color: Color of opponent whose threat we're checking
            
        Returns:
            True if this position is part of a 3-in-a-row threat
        """
        # Check all possible lines through this position
        lines_to_check = []
        
        # Horizontal line
        lines_to_check.append([(row, c) for c in range(self.size)])
        
        # Vertical line  
        lines_to_check.append([(r, col) for r in range(self.size)])
        
        # Main diagonal (if position is on it)
        if row == col:
            lines_to_check.append([(i, i) for i in range(self.size)])
        
        # Anti-diagonal (if position is on it)
        if row + col == self.size - 1:
            lines_to_check.append([(i, self.size - 1 - i) for i in range(self.size)])
        
        # Check each line for 3-in-a-row threat
        for line in lines_to_check:
            if self._line_has_three_in_row_threat(line, opponent_color, (row, col)):
                return True
        
        return False
    
    def _line_has_three_in_row_threat(self, line: List[Tuple[int, int]], 
                                     opponent_color: PieceColor, 
                                     target_pos: Tuple[int, int]) -> bool:
        """
        Check if a line has exactly 3 opponent pieces in a row, with target_pos being one of them.
        
        Args:
            line: List of positions forming a line
            opponent_color: Opponent's color
            target_pos: The position we're considering covering
            
        Returns:
            True if line has 3-in-a-row threat including target_pos
        """
        opponent_count = 0
        target_pos_has_opponent = False
        
        for pos in line:
            r, c = pos
            top_piece = self.get_top_piece(r, c)
            
            if top_piece and top_piece.color == opponent_color:
                opponent_count += 1
                if pos == target_pos:
                    target_pos_has_opponent = True
        
        # Must have exactly 3 opponent pieces, and target position must be one of them
        return opponent_count == 3 and target_pos_has_opponent
    
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
