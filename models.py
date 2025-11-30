"""Data models for Zip Game Solver."""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Set, Optional

@dataclass
class GridParseResult:
    grid: List[List[int]]
    numbered_cells: Dict[int, Tuple[int, int]]
    rows: int
    cols: int
    cell_rects: Dict[int, Tuple[float, float, float, float]]
    blocked_edges: Set[frozenset]