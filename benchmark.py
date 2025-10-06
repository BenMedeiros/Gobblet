"""
Performance benchmark for the Gobblet simulator.
"""

import sys
import os
import time
from typing import Dict, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gobblet.simulator import GameSimulator
from gobblet.moves import GameDataManager


def benchmark_single_games():
    """Benchmark single game performance."""
    print("Benchmarking single game performance...")
    
    data_manager = GameDataManager("benchmark_data.json")
    simulator = GameSimulator(data_manager)
    
    strategies = ["random", "greedy", "defensive"]
    results = {}
    
    for light_strategy in strategies:
        for dark_strategy in strategies:
            matchup = f"{light_strategy}_vs_{dark_strategy}"
            
            start_time = time.time()
            
            # Run 50 games
            for _ in range(50):
                simulator.run_single_simulation(
                    light_strategy=light_strategy,
                    dark_strategy=dark_strategy,
                    verbose=False
                )
            
            end_time = time.time()
            duration = end_time - start_time
            games_per_second = 50 / duration
            
            results[matchup] = {
                "duration": duration,
                "games_per_second": games_per_second
            }
    
    return results


def benchmark_batch_performance():
    """Benchmark batch simulation performance."""
    print("Benchmarking batch simulation performance...")
    
    data_manager = GameDataManager("benchmark_batch_data.json")
    simulator = GameSimulator(data_manager)
    
    game_counts = [10, 50, 100]
    results = {}
    
    for num_games in game_counts:
        # Sequential
        start_time = time.time()
        simulator.run_batch_simulation(
            num_games=num_games,
            light_strategy="random",
            dark_strategy="random",
            verbose=False,
            parallel=False
        )
        sequential_time = time.time() - start_time
        
        # Parallel
        start_time = time.time()
        simulator.run_batch_simulation(
            num_games=num_games,
            light_strategy="random",
            dark_strategy="random",
            verbose=False,
            parallel=True
        )
        parallel_time = time.time() - start_time
        
        results[num_games] = {
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "speedup": sequential_time / parallel_time if parallel_time > 0 else 0,
            "sequential_gps": num_games / sequential_time,
            "parallel_gps": num_games / parallel_time
        }
    
    return results


def benchmark_tournament_performance():
    """Benchmark tournament performance."""
    print("Benchmarking tournament performance...")
    
    data_manager = GameDataManager("benchmark_tournament_data.json")
    simulator = GameSimulator(data_manager)
    
    strategies = ["random", "greedy"]
    games_per_matchup = 20
    
    start_time = time.time()
    tournament_results = simulator.run_tournament(
        strategies=strategies,
        games_per_matchup=games_per_matchup,
        verbose=False
    )
    duration = time.time() - start_time
    
    total_games = tournament_results["total_games"]
    games_per_second = total_games / duration
    
    return {
        "total_games": total_games,
        "duration": duration,
        "games_per_second": games_per_second
    }


def print_benchmark_results():
    """Run all benchmarks and print results."""
    print("=" * 60)
    print("GOBBLET SIMULATOR PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    # Single game benchmarks
    print("\n1. SINGLE GAME PERFORMANCE")
    print("-" * 30)
    single_results = benchmark_single_games()
    
    for matchup, data in single_results.items():
        print(f"{matchup}: {data['games_per_second']:.1f} games/sec")
    
    avg_gps = sum(data['games_per_second'] for data in single_results.values()) / len(single_results)
    print(f"Average: {avg_gps:.1f} games/sec")
    
    # Batch performance benchmarks
    print("\n2. BATCH SIMULATION PERFORMANCE")
    print("-" * 35)
    batch_results = benchmark_batch_performance()
    
    print(f"{'Games':<8} {'Sequential':<12} {'Parallel':<12} {'Speedup':<10}")
    print("-" * 45)
    for num_games, data in batch_results.items():
        print(f"{num_games:<8} {data['sequential_gps']:<12.1f} {data['parallel_gps']:<12.1f} {data['speedup']:<10.2f}x")
    
    # Tournament performance
    print("\n3. TOURNAMENT PERFORMANCE")
    print("-" * 25)
    tournament_results = benchmark_tournament_performance()
    
    print(f"Total games: {tournament_results['total_games']}")
    print(f"Duration: {tournament_results['duration']:.2f}s")
    print(f"Games per second: {tournament_results['games_per_second']:.1f}")
    
    # Memory usage estimation
    print("\n4. MEMORY USAGE ESTIMATION")
    print("-" * 30)
    data_manager = GameDataManager("benchmark_data.json")
    games = data_manager.load_games()
    
    if games:
        total_moves = sum(len(game.moves) for game in games)
        avg_moves_per_game = total_moves / len(games)
        
        print(f"Games analyzed: {len(games)}")
        print(f"Total moves: {total_moves}")
        print(f"Average moves per game: {avg_moves_per_game:.1f}")
        print(f"Estimated memory per game: ~{avg_moves_per_game * 0.5:.1f} KB")
    
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    print("Starting Gobblet Simulator Performance Benchmark...")
    print("This will run several tests to measure performance.")
    print("Please wait, this may take a few minutes...")
    print()
    
    try:
        print_benchmark_results()
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError during benchmark: {e}")
