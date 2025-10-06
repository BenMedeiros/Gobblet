"""
Tests for the game simulator.
"""

import pytest
from src.gobblet.simulator import GameSimulator
from src.gobblet.moves import GameDataManager
from src.gobblet.piece import PieceColor


class TestGameSimulator:
    """Test cases for the GameSimulator class."""
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        simulator = GameSimulator()
        assert simulator.data_manager is not None
        assert "random" in simulator.player_types
        assert "greedy" in simulator.player_types
        assert "defensive" in simulator.player_types
    
    def test_single_simulation(self):
        """Test running a single game simulation."""
        data_manager = GameDataManager("test_data.json")
        simulator = GameSimulator(data_manager)
        
        result = simulator.run_single_simulation(
            light_strategy="random",
            dark_strategy="random",
            verbose=False
        )
        
        assert "game_id" in result
        assert "winner" in result
        assert result["winner"] in ["light", "dark", "draw"]
        assert "light_strategy" in result
        assert "dark_strategy" in result
        assert "turn_count" in result
        assert "duration_seconds" in result
        assert "move_count" in result
        assert "game_record" in result
        
        # Verify the game was saved
        assert len(data_manager.games) == 1
    
    def test_batch_simulation(self):
        """Test running multiple game simulations."""
        data_manager = GameDataManager("test_batch_data.json")
        simulator = GameSimulator(data_manager)
        
        num_games = 5
        analysis = simulator.run_batch_simulation(
            num_games=num_games,
            light_strategy="random",
            dark_strategy="greedy",
            verbose=False,
            parallel=False  # Use sequential for predictable testing
        )
        
        assert analysis["total_games"] == num_games
        assert "light_wins" in analysis
        assert "dark_wins" in analysis
        assert "draws" in analysis
        assert analysis["light_wins"] + analysis["dark_wins"] + analysis["draws"] == num_games
        
        assert "light_win_rate" in analysis
        assert "dark_win_rate" in analysis
        assert "draw_rate" in analysis
        
        assert "average_turns" in analysis
        assert "average_moves" in analysis
        assert "total_simulation_time" in analysis
        
        # Verify all games were saved
        assert len(data_manager.games) == num_games
    
    def test_tournament_simulation(self):
        """Test running a tournament with multiple strategies."""
        data_manager = GameDataManager("test_tournament_data.json")
        simulator = GameSimulator(data_manager)
        
        strategies = ["random", "greedy"]
        games_per_matchup = 2
        
        tournament_results = simulator.run_tournament(
            strategies=strategies,
            games_per_matchup=games_per_matchup,
            verbose=False
        )
        
        assert "strategies" in tournament_results
        assert tournament_results["strategies"] == strategies
        assert tournament_results["games_per_matchup"] == games_per_matchup
        
        assert "matchups" in tournament_results
        assert "overall_stats" in tournament_results
        
        # Should have 4 matchups (2x2 combinations)
        expected_matchups = len(strategies) * len(strategies)
        assert len(tournament_results["matchups"]) == expected_matchups
        
        # Check that each matchup has the expected number of games
        for matchup_key, matchup_data in tournament_results["matchups"].items():
            assert matchup_data["total_games"] == games_per_matchup
        
        # Check overall stats
        overall_stats = tournament_results["overall_stats"]
        assert "strategy_stats" in overall_stats
        assert "ranking" in overall_stats
        
        # All strategies should be in the stats
        for strategy in strategies:
            assert strategy in overall_stats["strategy_stats"]
            strategy_stats = overall_stats["strategy_stats"][strategy]
            assert "games_played" in strategy_stats
            assert "total_wins" in strategy_stats
            assert "win_rate" in strategy_stats
        
        # Total games should match
        total_expected_games = len(strategies) * len(strategies) * games_per_matchup
        assert tournament_results["total_games"] == total_expected_games
    
    def test_invalid_strategy(self):
        """Test that invalid strategies raise an error."""
        simulator = GameSimulator()
        
        with pytest.raises(ValueError):
            simulator._create_player("invalid_strategy", PieceColor.LIGHT)
    
    def test_parallel_vs_sequential(self):
        """Test that parallel and sequential execution produce similar results."""
        data_manager_parallel = GameDataManager("test_parallel.json")
        data_manager_sequential = GameDataManager("test_sequential.json")
        
        simulator_parallel = GameSimulator(data_manager_parallel)
        simulator_sequential = GameSimulator(data_manager_sequential)
        
        num_games = 4
        
        # Run parallel
        parallel_results = simulator_parallel.run_batch_simulation(
            num_games=num_games,
            light_strategy="random",
            dark_strategy="random",
            verbose=False,
            parallel=True
        )
        
        # Run sequential
        sequential_results = simulator_sequential.run_batch_simulation(
            num_games=num_games,
            light_strategy="random",
            dark_strategy="random",
            verbose=False,
            parallel=False
        )
        
        # Both should have same number of games
        assert parallel_results["total_games"] == sequential_results["total_games"]
        assert parallel_results["total_games"] == num_games
        
        # Both should have saved the same number of games
        assert len(data_manager_parallel.games) == num_games
        assert len(data_manager_sequential.games) == num_games
    
    def test_different_board_sizes(self):
        """Test simulation with different board sizes."""
        simulator = GameSimulator()
        
        # Test 3x3 board
        result_3x3 = simulator.run_single_simulation(
            light_strategy="random",
            dark_strategy="random",
            board_size=3,
            verbose=False
        )
        
        # Test 5x5 board
        result_5x5 = simulator.run_single_simulation(
            light_strategy="random",
            dark_strategy="random",
            board_size=5,
            verbose=False
        )
        
        assert "game_id" in result_3x3
        assert "game_id" in result_5x5
        assert result_3x3["game_id"] != result_5x5["game_id"]
    
    def test_strategy_matchups(self):
        """Test specific strategy matchups."""
        simulator = GameSimulator()
        
        # Test random vs greedy
        result = simulator.run_batch_simulation(
            num_games=3,
            light_strategy="random",
            dark_strategy="greedy",
            verbose=False,
            parallel=False
        )
        
        assert result["light_strategy"] == "random"
        assert result["dark_strategy"] == "greedy"
        assert result["total_games"] == 3
        
        # Test greedy vs defensive
        result = simulator.run_batch_simulation(
            num_games=3,
            light_strategy="greedy",
            dark_strategy="defensive",
            verbose=False,
            parallel=False
        )
        
        assert result["light_strategy"] == "greedy"
        assert result["dark_strategy"] == "defensive"
        assert result["total_games"] == 3
