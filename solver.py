"""Zip Game Solver."""

from typing import List, Tuple, Optional, Dict, Set

from models import GridParseResult

class ZipSolverCore:
    def __init__(self, grid: List[List[int]], blocked_edges: Optional[Set[frozenset]] = None):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows else 0
        self.numbered_cells = {
            grid[r][c]: (r, c) 
            for r in range(self.rows) 
            for c in range(self.cols) 
            if grid[r][c] > 0
        }
        self.blocked = blocked_edges or set()
        self.max_number = max(self.numbered_cells.keys()) if self.numbered_cells else 0

    def _neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get valid neighbors considering walls and grid boundaries."""
        neighbors = []
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if frozenset({(r, c), (nr, nc)}) not in self.blocked:
                    neighbors.append((nr, nc))
        return neighbors

    def get_reachable_cells(self, start: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """BFS to find all reachable cells from start position."""
        reachable = set()
        queue = [start]
        visited = {start}
        
        while queue:
            curr = queue.pop(0)
            reachable.add(curr)
            for nb in self._neighbors(*curr):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        return reachable




    def solve_zip_game(self) -> Optional[List[Tuple[int, int]]]:
        """Solve using A*-guided backtracking."""
        if 1 not in self.numbered_cells:
            return None

        start = self.numbered_cells[1]
        reachable = self.get_reachable_cells(start)
        total_cells = len(reachable)
        
        # Verify all numbered cells are reachable
        for num, pos in self.numbered_cells.items():
            if pos not in reachable:
                return None


        def backtrack(path: List[Tuple[int, int]], next_target: int, 
                     visited: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
            current_pos = path[-1]
            current_r, current_c = current_pos
            
            # Check current cell value FIRST
            current_val = self.grid[current_r][current_c]
            if current_val > 0:
                if current_val != next_target:
                    return None
                next_target += 1
            
            # Check completion AFTER number match: full coverage, all numbers, ENDS at max_number pos
            if len(path) == total_cells and next_target > self.max_number:
                max_pos = self.numbered_cells[self.max_number]
                if current_pos == max_pos:
                    return path
                return None
            
            # Get neighbors in fixed order (pure DFS)
            neighbors = [nb for nb in self._neighbors(current_r, current_c) if nb not in visited]
            
            if not neighbors:
                return None

            # Try neighbors in fixed order (no heuristic sorting/pruning)
            for neighbor in neighbors:
                visited.add(neighbor)
                result = backtrack(path + [neighbor], next_target, visited)
                if result:
                    return result
                visited.remove(neighbor)

            return None

        initial_visited = {start}
        solution = backtrack([start], 1, initial_visited)
        return solution

    def validate_solution(self, sol: List[Tuple[int, int]]) -> tuple[bool, str]:
        """Validate the solution path."""
        if not sol:
            return False, "No solution provided"

        start = sol[0]
        reachable = self.get_reachable_cells(start)
        expected_length = len(reachable)

        if len(sol) != expected_length:
            return False, f"Path length {len(sol)} but expected {expected_length}"

        if len(set(sol)) != len(sol):
            return False, "Duplicate cells in path"

        # Check moves are valid and not blocked
        for i in range(len(sol) - 1):
            current, next_cell = sol[i], sol[i + 1]
            if abs(current[0] - next_cell[0]) + abs(current[1] - next_cell[1]) != 1:
                return False, f"Non-adjacent move {current} -> {next_cell}"
            
            if frozenset({current, next_cell}) in self.blocked:
                return False, f"Blocked move {current} -> {next_cell}"

        # Check number sequence
        expected_num = 1
        for pos in sol:
            r, c = pos
            cell_value = self.grid[r][c]
            if cell_value > 0:
                if cell_value != expected_num:
                    return False, f"Expected {expected_num} at {pos} but found {cell_value}"
                expected_num += 1

        if expected_num <= self.max_number:
            return False, f"Missing numbers from {expected_num} to {self.max_number}"

        return True, "Valid solution"
