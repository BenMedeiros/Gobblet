"""
Tests for the Gobblet game core functionality.
"""

import pytest
from src.gobblet.game import GobbletGame
from src.gobblet.player import RandomPlayer, GreedyPlayer, PieceColor
from src.gobblet.piece import Piece, PieceSize


class TestGobbletGame:
    """Test cases for the GobbletGame class."""
    
    def test_game_initialization(self):
        """Test that a game initializes correctly."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        assert game.light_player == light_player
        assert game.dark_player == dark_player
        assert game.current_player == light_player  # Light goes first
        assert not game.game_over
        assert game.winner is None
        assert game.turn_count == 0
    
    def test_player_turn_switching(self):
        """Test that players switch turns correctly."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        initial_player = game.current_player
        game._switch_player()
        assert game.current_player != initial_player
        
        game._switch_player()
        assert game.current_player == initial_player
    
    def test_piece_placement(self):
        """Test basic piece placement functionality."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        # Get a piece from the current player
        available_pieces = game.current_player.get_available_pieces()
        assert len(available_pieces) > 0
        
        piece = available_pieces[0]
        
        # Test valid placement
        move_data = {"piece": piece, "position": (0, 0)}
        result = game._execute_place_move(move_data)
        assert result is True
        
        # Verify piece is on the board
        assert game.board.get_top_piece(0, 0) == piece
        assert piece.position == (0, 0)
    
    def test_invalid_piece_placement(self):
        """Test that invalid piece placements are rejected."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        # Test placement with None piece
        move_data = {"piece": None, "position": (0, 0)}
        result = game._execute_place_move(move_data)
        assert result is False
        
        # Test placement with invalid position
        piece = game.current_player.get_available_pieces()[0]
        move_data = {"piece": piece, "position": None}
        result = game._execute_place_move(move_data)
        assert result is False
        
        # Test placement of opponent's piece
        opponent_piece = game.dark_player.get_available_pieces()[0]
        move_data = {"piece": opponent_piece, "position": (0, 0)}
        result = game._execute_place_move(move_data)
        assert result is False
    
    def test_piece_covering(self):
        """Test that larger pieces can cover smaller pieces."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        # Place a small piece
        small_piece = None
        for piece in game.current_player.get_available_pieces():
            if piece.size == PieceSize.SMALL:
                small_piece = piece
                break
        
        assert small_piece is not None
        game._execute_place_move({"piece": small_piece, "position": (1, 1)})
        
        # Switch players and try to cover with a large piece
        game._switch_player()
        large_piece = None
        for piece in game.current_player.get_available_pieces():
            if piece.size == PieceSize.LARGE:
                large_piece = piece
                break
        
        assert large_piece is not None
        result = game._execute_place_move({"piece": large_piece, "position": (1, 1)})
        assert result is True
        
        # Verify the large piece is now on top
        assert game.board.get_top_piece(1, 1) == large_piece
    
    def test_game_completion(self):
        """Test that the game ends correctly."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        # Manually create a winning condition
        # Place light pieces in a row
        light_pieces = [p for p in light_player.pieces if p.size == PieceSize.LARGE][:4]
        
        for i, piece in enumerate(light_pieces):
            game.board.place_piece(piece, 0, i)
        
        # Check for winner
        winner = game.board.check_winner()
        assert winner == PieceColor.LIGHT
        
        # End the game
        game._end_game(winner)
        assert game.game_over is True
        assert game.winner == PieceColor.LIGHT
    
    def test_move_tracking(self):
        """Test that moves are properly tracked."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        # Make a move
        piece = game.current_player.get_available_pieces()[0]
        move_data = {"piece": piece, "position": (2, 2)}
        game._execute_place_move(move_data)
        
        # Check that the move was recorded
        assert len(game.move_tracker.moves) == 1
        
        move = game.move_tracker.moves[0]
        assert move.player_color == game.light_player.color
        assert move.move_type == "place"
        assert move.piece_id == piece.piece_id
        assert move.to_position == (2, 2)
        assert move.from_position is None
    
    def test_full_game_simulation(self):
        """Test that a full game can be played to completion."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        # Set a lower max turns to avoid long test
        game.max_turns = 50
        
        winner = game.play_game()
        
        # Game should be over
        assert game.game_over is True
        
        # Winner should be a valid color or None (draw)
        assert winner is None or winner in [PieceColor.LIGHT, PieceColor.DARK]
        
        # Should have some moves recorded
        assert len(game.move_tracker.moves) > 0
        
        # Game record should be complete
        game_record = game.get_game_record()
        assert game_record.game_id == game.game_id
        assert game_record.winner == winner
        assert game_record.end_time is not None
    
    def test_game_state_tracking(self):
        """Test that game state is tracked correctly."""
        light_player = RandomPlayer(PieceColor.LIGHT)
        dark_player = RandomPlayer(PieceColor.DARK)
        game = GobbletGame(light_player, dark_player)
        
        initial_state = game.get_game_state()
        assert initial_state["turn_count"] == 0
        assert initial_state["game_over"] is False
        assert initial_state["winner"] is None
        assert initial_state["current_player"] == str(light_player)
        
        # Play one turn
        game.play_turn()
        
        updated_state = game.get_game_state()
        assert updated_state["turn_count"] == 1
        assert updated_state["move_count"] >= 1
