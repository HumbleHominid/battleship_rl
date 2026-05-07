import sys
from Code.Prerequisite.algorithm1_count_config import count_config

def compute_optimal(grid_width, grid_height, ships, hit_shots, miss_shots, memo=None):
    """
    Algorithm 2: Compute the optimal average number of shots
    
    Input:
    grid_width, grid_height: Dimensions of the board
    ships: List of integers representing ship sizes
    hit_shots: Set or list of (x, y) tuples representing hits
    miss_shots: Set or list of (x, y) tuples representing misses
    
    Output:
    Sum of heights of all branches from the root to a leaf
    """
    if memo is None:
        memo = {}
        
    state = (frozenset(hit_shots), frozenset(miss_shots))
    if state in memo:
        return memo[state]
        
    nb_configs = count_config(grid_width, grid_height, ships, hit_shots, miss_shots)
    if nb_configs == 0:
        return 0
        
    # Terminal condition: If all ships have been found, the game ends.
    total_ship_cells = sum(ships)
    if len(hit_shots) == total_ship_cells:
        return 0
        
    current_min_height = float('inf')
    
    # Iterate through all empty cells
    empty_cells = [
        (r, c) for r in range(grid_height) for c in range(grid_width)
        if (r, c) not in hit_shots and (r, c) not in miss_shots
    ]
    
    for c in empty_cells:
        # Simulate hitting the cell c
        after_hit_shots = set(hit_shots)
        after_hit_shots.add(c)
        after_hit_height = compute_optimal(grid_width, grid_height, ships, after_hit_shots, miss_shots, memo)
        
        # Simulate missing the cell c
        after_miss_shots = set(miss_shots)
        after_miss_shots.add(c)
        after_miss_height = compute_optimal(grid_width, grid_height, ships, hit_shots, after_miss_shots, memo)
        
        # Calculate current height
        current_height = nb_configs + after_hit_height + after_miss_height
        
        if current_height < current_min_height:
            current_min_height = current_height
            
    # Fallback if no empty cells are available (though shouldn't happen logically if hits < total_ship_cells)
    if current_min_height == float('inf'):
        current_min_height = 0
        
    memo[state] = current_min_height
    return current_min_height

# Example usage:
if __name__ == "__main__":
    # Test on a small grid
    grid_w, grid_h = 2, 2
    test_ships = [2]
    
    print("Computing optimal average shots for 2x2 grid with one ship of size 2...")
    sum_heights = compute_optimal(grid_w, grid_h, test_ships, set(), set())
    
    total_configs = count_config(grid_w, grid_h, test_ships, set(), set())
    
    if total_configs > 0:
        optimal_avg_shots = sum_heights / total_configs
        print(f"Total configurations: {total_configs}")
        print(f"Sum of heights: {sum_heights}")
        print(f"Optimal average number of shots: {optimal_avg_shots}")
    else:
        print("No valid configurations.")
