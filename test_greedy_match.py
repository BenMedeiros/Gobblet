#!/usr/bin/env python3

"""
Simple test script to watch a single greedy vs greedy game in detail.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gobblet.game import Game
from gobblet.player import GreedyPlayer
from gobblet.piece import PieceColor

def main():
    print("Testing Greedy vs Greedy Match")
    print("=" * 50)
    
    # Create players
    light_player = GreedyPlayer(PieceColor.LIGHT, "Greedy Light")
    dark_player = GreedyPlayer(PieceColor.DARK, "Greedy Dark")
    
    # Create and run game
    game = Game(light_player, dark_player, board_size=4)
    
    print(f"Starting game: {light_player} vs {dark_player}")
    print()
    
    turn = 1
    max_turns = 100  # Prevent infinite games
    
    while not game.is_game_over() and turn <= max_turns:
        current_player = game.get_current_player()
        print(f"Turn {turn}: {current_player}'s move")
        
        # Show board before move
        print("\nBoard before move:")
        print(game.board)
        
        # Make move
        try:
            move_made = game.make_move()
            if not move_made:
                print(f"No valid moves available for {current_player}")
                break
                
            # Show move details if possible
            if hasattr(game, 'last_move'):
                print(f"Move: {game.last_move}")
            
        except Exception as e:
            print(f"Error making move: {e}")
            break
        
        print("\nBoard after move:")
        print(game.board)
        print("-" * 30)
        
        turn += 1
    
    print("\nFinal Results:")
    print("=" * 30)
    print(f"Final board:")
    print(game.board)
    
    winner = game.get_winner()
    if winner:
        print(f"Winner: {winner}")
    else:
        print("Game ended in a draw")
    
    print(f"Total turns: {turn - 1}")
    print(f"Total moves: {len(game.moves)}")
    
    # Show some recent moves
    if game.moves:
        print(f"\nLast few moves:")
        for i, move in enumerate(game.moves[-5:], 1):
            print(f"  {len(game.moves) - 5 + i}: {move}")

if __name__ == "__main__":
    main()
