# LinkedIn ZIP Game Solver 🧩

Automated solver for the LinkedIn ZIP puzzle: **Hamiltonian path visiting all free cells exactly once, hitting numbered checkpoints (1→N) in order, avoiding walls. Uses DFS backtracking (not A*/shortest-path).**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4-green.svg)](https://selenium.dev/)

## Features
- ✅ **Live extraction**: Auto-opens Chrome, scrapes puzzle from LinkedIn game page.
- ✅ **Test mode**: 5x5 mock puzzle for quick verification.
- ✅ **Animated visualization**: Step-by-step path replay (play/pause/step, speed control).
- ✅ **Validation**: Checks path coverage, numbers order, no crossings/walls.
  
## Installation
1. Clone/download project.
2. Install deps:
   ```
   pip install -r LinkedinZipSolver/requirements.txt
   ```
   (selenium, webdriver-manager – auto-downloads ChromeDriver)

**Requirements**: Python 3.8+, Chrome browser.

## Quick Start
```
cd LinkedinZipSolver
python main.py
```
GUI opens:

| Button | Action |
|--------|--------|
| 🎮 **Solve Live Puzzle** | Opens browser → LinkedIn ZIP → extracts → solves → animates. **Login to LinkedIn first!** |
| 🧪 **Test 5x5 Puzzle** | Mock grid → solves → animates (for testing). |
| ❌ **Exit** | Quit. |

**Live Workflow**:
1. Navigate browser to [LinkedIn ZIP](https://www.linkedin.com/games/zip/).
2. Click "Solve Live" → Auto-extracts grid/numbers/walls → Finds path → Opens viz window.
3. Use controls: ▶ Play, ⏮ Start, ⏩ Next, speed slider.

**Viz Controls**:
- Step through path, see green lines/dots (red current), **numbers always visible**.
- Status: Position/Value, progress bar.

## Full Workflow
```
GUI (main.py)
├── Test: Mock puzzle (worker.py) → Solver → Visualizer
└── Live: Worker thread → Selenium browser → Extractor → Parser (models) → Solver → Queue → Visualizer
```

**ASCII Flow**:
```
Live Puzzle (LinkedIn)
     ↓ (Selenium)
Extractor.py (grid, numbers, walls)
     ↓
Models.py (GridParseResult)
     ↓
Solver.py (BFS reachable + DFS backtrack)
     ↓ Validate
Visualizer.py (Tkinter animation)
```

## File Structure
| File | Purpose |
|------|---------|
| `main.py` | Tkinter GUI: Buttons, status, result polling, viz launcher. |
| `worker.py` | Background threads: Selenium setup, mock puzzle, queue results. |
| `extractor.py` | Parses live DOM → grid (0=free, N=number), walls (blocked edges). |
| `models.py` | Data: `GridParseResult` (grid, rows/cols, blocked_edges, etc.). |
| `solver.py` | `ZipSolverCore`: `_neighbors`, reachable BFS, `solve_zip_game` (backtrack), `validate_solution`. |
| `visualizer.py` | Tkinter canvas: Grid/walls/path animation (lines/dots, numbers on top). |
| `requirements.txt` | selenium, webdriver-manager. |

## How It Works
1. **Extraction**: Selenium loads game → Finds canvas/elements → Computes positions → Builds grid/walls.
2. **Parsing**: Grid[int[][]]: 0=empty, N=checkpoint. Walls as `frozenset({(r1,c1),(r2,c2)})` edges.
3. **Solve**:
   - BFS: All reachable from #1.
   - Backtrack: From #1, extend path to unvisited neighbors, match next number, full coverage + end at max N.
4. **Viz**: Canvas grid (blue=#cells), black walls, green path lines, small dots (red current), numbers overlaid.

**Puzzle Rules** (enforced):
- Start #1 → End max N, numbers in order.
- Visit **all reachable free cells exactly once** (no crosses/revisits).
- Walls block moves.
- Backtrack if stuck.

## Customization
- **Mock puzzle**: Edit `create_mock_puzzle()` in worker.py.
- **Viz tweaks**: Colors/sizes/speed in visualizer.py.
- **Solver**: Adjust neighbor order for faster paths.

## Troubleshooting
| Issue | Fix |
|-------|-----|
| **ChromeDriver error** | Re-run `pip install -r requirements.txt` (auto-installs). |
| **Login fails** | Manually login to LinkedIn before "Solve Live". |
| **No solution** | Unreachable numbers/walls → Check console. |
| **Extraction fails** | Game updated? Update extractor.py selectors. |
| **Viz numbers hidden** | Fixed: Smaller dots + redraw on top. |
| **Slow solve** | Large grids → Pure DFS exponential, but puzzles small. |

## Development
- **Run**: `python main.py`
- **Test live**: Ensure ZIP page loaded.
- **Standards**: DRY/KISS, documented, end-to-end testable.

**Recent Updates**:
- Numbers visible during path visits.
- Visualizer concise (~25% shorter).

Enjoy solving! 🚀
