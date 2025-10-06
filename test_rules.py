"""
Test script to demonstrate the new Gobblet rules.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gobblet.board import Board
from gobblet.piece import Piece, PieceColor, PieceSize


def test_new_piece_rules():
    """Test the new piece placement rules."""
    print("Testing New Gobblet Rules")
    print("=" * 30)
    
    board = Board(4)
    
    # Create some pieces
    light_large = Piece(PieceColor.LIGHT, PieceSize.LARGE, 1)
    dark_small = Piece(PieceColor.DARK, PieceSize.SMALL, 10)
    dark_medium = Piece(PieceColor.DARK, PieceSize.MEDIUM, 11)
    
    print("1. Testing new piece on empty space (should work):")
    result = board.place_piece(light_large, 1, 1, is_new_piece=True)
    print(f"   Placed light large piece at (1,1): {result}")
    print(f"   Board position (1,1): {board.get_top_piece(1, 1)}")
    
    print("\n2. Testing new piece on occupied space (should fail - no 3-in-a-row):")
    result = board.place_piece(dark_medium, 1, 1, is_new_piece=True)
    print(f"   Tried to place dark medium on light large: {result}")
    
    print("\n3. Testing existing piece move on occupied space (should work):")
    # First place the dark piece somewhere else
    board.place_piece(dark_medium, 2, 2, is_new_piece=True)
    print(f"   Placed dark medium at (2,2): {board.get_top_piece(2, 2)}")
    
    # Now move it to cover the light piece
    board.remove_piece(2, 2)  # Remove from original position
    result = board.place_piece(dark_medium, 1, 1, is_new_piece=False)
    print(f"   Moved dark medium to cover light large: {result}")
    print(f"   Board position (1,1) now: {board.get_top_piece(1, 1)}")
    
    print("\n4. Testing 3-in-a-row blocking rule:")
    # Create a 3-in-a-row threat
    board2 = Board(4)
    
    # Place 3 dark pieces in a row
    dark1 = Piece(PieceColor.DARK, PieceSize.SMALL, 12)
    dark2 = Piece(PieceColor.DARK, PieceSize.SMALL, 13) 
    dark3 = Piece(PieceColor.DARK, PieceSize.SMALL, 14)
    
    board2.place_piece(dark1, 0, 0, is_new_piece=True)
    board2.place_piece(dark2, 0, 1, is_new_piece=True)
    board2.place_piece(dark3, 0, 2, is_new_piece=True)
    
    print(f"   Created 3-in-a-row: {board2.get_top_piece(0, 0)}, {board2.get_top_piece(0, 1)}, {board2.get_top_piece(0, 2)}")
    
    # Now light should be able to place a new piece to block the 4th position
    light_medium = Piece(PieceColor.LIGHT, PieceSize.MEDIUM, 2)
    can_block = board2._is_blocking_three_in_row(0, 1, PieceColor.DARK)
    print(f"   Position (0,1) is part of 3-in-a-row threat: {can_block}")
    
    # Try to place new piece to block
    result = board2.place_piece(light_medium, 0, 1, is_new_piece=True)
    print(f"   Light can place new piece to block 3-in-a-row: {result}")
    print(f"   Board position (0,1) now: {board2.get_top_piece(0, 1)}")


if __name__ == "__main__":
    test_new_piece_rules()
