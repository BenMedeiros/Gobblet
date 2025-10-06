"""
Tests for the Gobblet board functionality.
"""

import pytest
from src.gobblet.board import Board, BoardPosition
from src.gobblet.piece import Piece, PieceColor, PieceSize


class TestBoardPosition:
    """Test cases for the BoardPosition class."""
    
    def test_empty_position(self):
        """Test empty board position."""
        position = BoardPosition()
        assert position.is_empty()
        assert position.piece_count() == 0
        assert position.top_piece() is None
    
    def test_add_piece(self):
        """Test adding a piece to a position."""
        position = BoardPosition()
        piece = Piece(PieceColor.LIGHT, PieceSize.MEDIUM, 1)
        
        result = position.add_piece(piece)
        assert result is True
        assert not position.is_empty()
        assert position.piece_count() == 1
        assert position.top_piece() == piece
    
    def test_piece_covering(self):
        """Test that larger pieces can cover smaller pieces."""
        position = BoardPosition()
        
        small_piece = Piece(PieceColor.LIGHT, PieceSize.SMALL, 1)
        large_piece = Piece(PieceColor.DARK, PieceSize.LARGE, 2)
        
        # Add small piece first
        position.add_piece(small_piece)
        assert position.top_piece() == small_piece
        
        # Add large piece on top
        result = position.add_piece(large_piece)
        assert result is True
        assert position.top_piece() == large_piece
        assert position.piece_count() == 2
    
    def test_invalid_covering(self):
        """Test that smaller pieces cannot cover larger pieces."""
        position = BoardPosition()
        
        large_piece = Piece(PieceColor.LIGHT, PieceSize.LARGE, 1)
        small_piece = Piece(PieceColor.DARK, PieceSize.SMALL, 2)
        
        # Add large piece first
        position.add_piece(large_piece)
        
        # Try to add small piece on top (should fail)
        result = position.add_piece(small_piece)
        assert result is False
        assert position.top_piece() == large_piece
        assert position.piece_count() == 1
    
    def test_remove_piece(self):
        """Test removing pieces from a position."""
        position = BoardPosition()
        
        piece1 = Piece(PieceColor.LIGHT, PieceSize.SMALL, 1)
        piece2 = Piece(PieceColor.DARK, PieceSize.LARGE, 2)
        
        position.add_piece(piece1)
        position.add_piece(piece2)
        
        # Remove top piece
        removed = position.remove_top_piece()
        assert removed == piece2
        assert position.top_piece() == piece1
        assert position.piece_count() == 1
        
        # Remove last piece
        removed = position.remove_top_piece()
        assert removed == piece1
        assert position.is_empty()
        
        # Try to remove from empty position
        removed = position.remove_top_piece()
        assert removed is None


class TestBoard:
    """Test cases for the Board class."""
    
    def test_board_initialization(self):
        """Test board initialization."""
        board = Board(4)
        assert board.size == 4
        
        # All positions should be empty
        for row in range(4):
            for col in range(4):
                assert board.is_position_empty(row, col)
                assert board.get_top_piece(row, col) is None
    
    def test_piece_placement(self):
        """Test placing pieces on the board."""
        board = Board(4)
        piece = Piece(PieceColor.LIGHT, PieceSize.MEDIUM, 1)
        
        result = board.place_piece(piece, 1, 2)
        assert result is True
        assert board.get_top_piece(1, 2) == piece
        assert piece.position == (1, 2)
        assert not board.is_position_empty(1, 2)
    
    def test_invalid_placement(self):
        """Test invalid piece placement."""
        board = Board(4)
        piece = Piece(PieceColor.LIGHT, PieceSize.SMALL, 1)
        
        # Test out of bounds placement
        result = board.place_piece(piece, -1, 0)
        assert result is False
        
        result = board.place_piece(piece, 0, 4)
        assert result is False
        
        result = board.place_piece(piece, 4, 0)
        assert result is False
    
    def test_piece_removal(self):
        """Test removing pieces from the board."""
        board = Board(4)
        piece = Piece(PieceColor.DARK, PieceSize.LARGE, 1)
        
        board.place_piece(piece, 2, 2)
        
        removed = board.remove_piece(2, 2)
        assert removed == piece
        assert board.is_position_empty(2, 2)
        assert piece.position is None
    
    def test_piece_stacking(self):
        """Test stacking pieces on the board."""
        board = Board(4)
        
        small_piece = Piece(PieceColor.LIGHT, PieceSize.SMALL, 1)
        medium_piece = Piece(PieceColor.DARK, PieceSize.MEDIUM, 2)
        large_piece = Piece(PieceColor.LIGHT, PieceSize.LARGE, 3)
        
        # Place pieces in order
        board.place_piece(small_piece, 1, 1)
        board.place_piece(medium_piece, 1, 1)
        board.place_piece(large_piece, 1, 1)
        
        assert board.get_top_piece(1, 1) == large_piece
        
        # Remove top piece
        removed = board.remove_piece(1, 1)
        assert removed == large_piece
        assert board.get_top_piece(1, 1) == medium_piece
    
    def test_winner_detection_rows(self):
        """Test winner detection for rows."""
        board = Board(4)
        
        # Create a row of light pieces
        for col in range(4):
            piece = Piece(PieceColor.LIGHT, PieceSize.LARGE, col)
            board.place_piece(piece, 0, col)
        
        winner = board.check_winner()
        assert winner == PieceColor.LIGHT
    
    def test_winner_detection_columns(self):
        """Test winner detection for columns."""
        board = Board(4)
        
        # Create a column of dark pieces
        for row in range(4):
            piece = Piece(PieceColor.DARK, PieceSize.MEDIUM, row)
            board.place_piece(piece, row, 1)
        
        winner = board.check_winner()
        assert winner == PieceColor.DARK
    
    def test_winner_detection_diagonal(self):
        """Test winner detection for diagonals."""
        board = Board(4)
        
        # Create a diagonal of light pieces
        for i in range(4):
            piece = Piece(PieceColor.LIGHT, PieceSize.SMALL, i)
            board.place_piece(piece, i, i)
        
        winner = board.check_winner()
        assert winner == PieceColor.LIGHT
        
        # Test anti-diagonal
        board = Board(4)
        for i in range(4):
            piece = Piece(PieceColor.DARK, PieceSize.LARGE, i + 4)
            board.place_piece(piece, i, 3 - i)
        
        winner = board.check_winner()
        assert winner == PieceColor.DARK
    
    def test_no_winner(self):
        """Test that no winner is detected when there isn't one."""
        board = Board(4)
        
        # Place some pieces but no winning line
        pieces = [
            (PieceColor.LIGHT, 0, 0),
            (PieceColor.DARK, 0, 1),
            (PieceColor.LIGHT, 1, 0),
            (PieceColor.DARK, 1, 1)
        ]
        
        for i, (color, row, col) in enumerate(pieces):
            piece = Piece(color, PieceSize.MEDIUM, i)
            board.place_piece(piece, row, col)
        
        winner = board.check_winner()
        assert winner is None
    
    def test_board_full_detection(self):
        """Test detection of full board."""
        board = Board(2)  # Small board for easier testing
        
        assert not board.is_board_full()
        
        # Fill all positions
        piece_id = 0
        for row in range(2):
            for col in range(2):
                color = PieceColor.LIGHT if (row + col) % 2 == 0 else PieceColor.DARK
                piece = Piece(color, PieceSize.MEDIUM, piece_id)
                board.place_piece(piece, row, col)
                piece_id += 1
        
        assert board.is_board_full()
    
    def test_valid_moves(self):
        """Test getting valid moves for a color."""
        board = Board(3)
        
        # Initially, all positions should be valid
        valid_moves = board.get_valid_moves(PieceColor.LIGHT)
        assert len(valid_moves) == 9  # 3x3 board
        
        # Place a piece
        piece = Piece(PieceColor.DARK, PieceSize.SMALL, 1)
        board.place_piece(piece, 1, 1)
        
        # Light should still be able to move to all positions (can cover)
        valid_moves = board.get_valid_moves(PieceColor.LIGHT)
        assert len(valid_moves) == 9
        
        # But if we place a light piece, dark can't place a smaller piece there
        large_piece = Piece(PieceColor.LIGHT, PieceSize.LARGE, 2)
        board.place_piece(large_piece, 1, 1)
        
        valid_moves = board.get_valid_moves(PieceColor.DARK)
        assert (1, 1) not in valid_moves or len([p for p in valid_moves if p == (1, 1)]) == 0
    
    def test_moveable_pieces(self):
        """Test getting moveable pieces for a color."""
        board = Board(3)
        
        # No pieces on board initially
        moveable = board.get_moveable_pieces(PieceColor.LIGHT)
        assert len(moveable) == 0
        
        # Place some pieces
        light_piece = Piece(PieceColor.LIGHT, PieceSize.MEDIUM, 1)
        dark_piece = Piece(PieceColor.DARK, PieceSize.LARGE, 2)
        
        board.place_piece(light_piece, 0, 0)
        board.place_piece(dark_piece, 1, 1)
        
        # Check moveable pieces
        light_moveable = board.get_moveable_pieces(PieceColor.LIGHT)
        dark_moveable = board.get_moveable_pieces(PieceColor.DARK)
        
        assert (0, 0) in light_moveable
        assert (1, 1) in dark_moveable
        assert len(light_moveable) == 1
        assert len(dark_moveable) == 1
    
    def test_board_copy(self):
        """Test creating a copy of the board."""
        board = Board(3)
        
        # Place some pieces
        piece1 = Piece(PieceColor.LIGHT, PieceSize.SMALL, 1)
        piece2 = Piece(PieceColor.DARK, PieceSize.LARGE, 2)
        
        board.place_piece(piece1, 0, 0)
        board.place_piece(piece2, 1, 1)
        
        # Create copy
        board_copy = board.copy()
        
        # Verify copy has same state
        assert board_copy.size == board.size
        assert board_copy.get_top_piece(0, 0) is not None
        assert board_copy.get_top_piece(1, 1) is not None
        
        # Verify it's actually a copy (not the same object)
        assert board_copy is not board
        
        # Modify original and ensure copy is unchanged
        board.remove_piece(0, 0)
        assert board.get_top_piece(0, 0) is None
        assert board_copy.get_top_piece(0, 0) is not None
