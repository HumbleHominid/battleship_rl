import math
from collections import Counter

def count_config(grid_width, grid_height, ships, hit_shots, miss_shots):
    """
    Algorithm 1: Count the ship configurations
    
    Input:
    grid_width, grid_height: Dimensions of the board
    ships: List of integers representing ship sizes (e.g. [5, 4, 3, 3, 2])
    hit_shots: List or set of (x, y) tuples representing hits
    miss_shots: List or set of (x, y) tuples representing misses
    
    Output:
    number of valid ship configurations
    """
    hit_shots = set(hit_shots)
    miss_shots = set(miss_shots)
    
    def is_valid(ship_size, r, c, direction, current_pos):
        if direction == 'H':
            if c + ship_size > grid_width: return False
            cells = [(r, c + k) for k in range(ship_size)]
        else:
            if r + ship_size > grid_height: return False
            cells = [(r + k, c) for k in range(ship_size)]
            
        for cell in cells:
            if cell in current_pos or cell in miss_shots:
                return False
        return cells

    def count(i, current_pos):
        if i >= len(ships):
            # All ships placed. Check if all hits are covered.
            for hit in hit_shots:
                if hit not in current_pos:
                    return 0
            return 1
            
        nb_configs = 0
        ship_size = ships[i]
        
        for r in range(grid_height):
            for c in range(grid_width):
                for direction in ['H', 'V']:
                    # Avoid duplicate placements for 1x1 ships
                    if ship_size == 1 and direction == 'V':
                        continue 
                        
                    cells = is_valid(ship_size, r, c, direction, current_pos)
                    if cells is not False:
                        new_pos = current_pos.union(cells)
                        # If the remaining hits cannot be covered by the remaining ships, prune.
                        remaining_hits = [hit for hit in hit_shots if hit not in new_pos]
                        remaining_ship_cells = sum(ships[i+1:]) if i + 1 < len(ships) else 0
                        if len(remaining_hits) > remaining_ship_cells:
                            continue
                            
                        r_val = count(i + 1, new_pos)
                        nb_configs += r_val
                        
        return nb_configs

    total = count(0, set())
    # if i = 1 and two ships of size 3 are used then return nbConfigs/2
    # To handle identical ships dynamically, divide by the factorial of their counts.
    counts = Counter(ships)
    divisor = 1
    for size, c in counts.items():
        divisor *= math.factorial(c)
        
    return total // divisor

# Example usage:
if __name__ == "__main__":
    import time
    grid_w, grid_h = 10, 10
    standard_fleet = [5, 4, 3, 3, 2]
    
    print(f"Computing total configurations for a {grid_w}x{grid_h} board with ships {standard_fleet}...")
    start_time = time.time()
    configs = count_config(grid_w, grid_h, standard_fleet, set(), set())
    elapsed = time.time() - start_time
    
    print(f"Total configurations: {configs}")
    print(f"Computed in {elapsed:.2f} seconds.")
