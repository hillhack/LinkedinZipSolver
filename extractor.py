"""Grid extraction for LinkedIn Zip."""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import math

from models import GridParseResult
from solver import ZipSolverCore  # For reachability check

def extract_zip_grid_improved(driver: webdriver.Chrome) -> GridParseResult:
    """Minimal grid extraction."""
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cell-idx]'))
        )

        cell_elems = driver.find_elements(By.CSS_SELECTOR, '[data-cell-idx]')
        if not cell_elems:
            raise RuntimeError("No cells.")

        size = int(math.sqrt(len(cell_elems)))
        print(f"Grid size detected: {size}x{size}")

        grid = [[0] * size for _ in range(size)]
        numbered_cells = {}
        blocked_edges = set()
        
        # CORRECTED: Extract numbers from nested elements
        print("\n=== Extracting numbers ===")
        for el in cell_elems:
            idx_attr = el.get_attribute('data-cell-idx')
            if idx_attr and idx_attr.isdigit():
                idx = int(idx_attr)
                r, c = divmod(idx, size)
                
                # Look for number in child elements
                number_elements = el.find_elements(By.CSS_SELECTOR, '.trail-cell-content')
                if number_elements:
                    text = number_elements[0].text.strip()
                    if text.isdigit():
                        val = int(text)
                        grid[r][c] = val
                        numbered_cells[val] = (r, c)
                        print(f"Cell {idx} ({r},{c}) = {val}")
                else:
                    # Fallback: check the cell text
                    text = el.text.strip()
                    if text.isdigit():
                        val = int(text)
                        grid[r][c] = val
                        numbered_cells[val] = (r, c)
                        print(f"Cell {idx} ({r},{c}) = {val} (fallback)")

        # CORRECTED: Wall detection with better logic
        print("\n=== Detecting walls ===")
        wall_count = 0
        
        # First, let's see what wall classes exist
        wall_classes_found = set()
        for el in cell_elems[:min(10, len(cell_elems))]:
            wall_elements = el.find_elements(By.CSS_SELECTOR, '.trail-cell-wall')
            for wall in wall_elements:
                wall_class = wall.get_attribute('class')
                wall_classes_found.add(wall_class)
        
        print(f"Found wall classes: {wall_classes_found}")
        
        # Now detect walls properly
        for el in cell_elems:
            idx_attr = el.get_attribute('data-cell-idx')
            if not idx_attr or not idx_attr.isdigit():
                continue
                
            idx = int(idx_attr)
            r, c = divmod(idx, size)
            
            # Find wall elements
            wall_elements = el.find_elements(By.CSS_SELECTOR, '.trail-cell-wall')
            
            for wall in wall_elements:
                wall_class = wall.get_attribute('class') or ''
                
                # Check each possible wall direction
                if 'trail-cell-wall--right' in wall_class:
                    nr, nc = r, c + 1
                    if 0 <= nc < size:
                        edge = frozenset({(r, c), (nr, nc)})
                        if edge not in blocked_edges:
                            blocked_edges.add(edge)
                            wall_count += 1
                            print(f"Wall {wall_count}: Cell ({r},{c}) → ({nr},{nc}) [RIGHT]")
                
                if 'trail-cell-wall--left' in wall_class:
                    nr, nc = r, c - 1
                    if 0 <= nc < size:
                        edge = frozenset({(r, c), (nr, nc)})
                        if edge not in blocked_edges:
                            blocked_edges.add(edge)
                            wall_count += 1
                            print(f"Wall {wall_count}: Cell ({r},{c}) → ({nr},{nc}) [LEFT]")
                
                if 'trail-cell-wall--down' in wall_class:
                    nr, nc = r + 1, c
                    if 0 <= nr < size:
                        edge = frozenset({(r, c), (nr, nc)})
                        if edge not in blocked_edges:
                            blocked_edges.add(edge)
                            wall_count += 1
                            print(f"Wall {wall_count}: Cell ({r},{c}) → ({nr},{nc}) [DOWN/BOTTOM]")
                
                if 'trail-cell-wall--up' in wall_class:
                    nr, nc = r - 1, c
                    if 0 <= nr < size:
                        edge = frozenset({(r, c), (nr, nc)})
                        if edge not in blocked_edges:
                            blocked_edges.add(edge)
                            wall_count += 1
                            print(f"Wall {wall_count}: Cell ({r},{c}) → ({nr},{nc}) [UP/TOP]")
        
        print(f"\nTotal blocked edges: {len(blocked_edges)}")
        
        # Check reachability
        temp_solver = ZipSolverCore(grid, blocked_edges)
        if 1 in numbered_cells:
            start = numbered_cells[1]
            reachable = temp_solver.get_reachable_cells(start)
            print(f"\n=== Reachability Check ===")
            print(f"Start at cell {start} (number 1)")
            print(f"Reachable cells: {len(reachable)}/{size*size}")
            
            # Check if all numbered cells are reachable
            for num, pos in numbered_cells.items():
                if pos in reachable:
                    print(f"✓ Number {num} at {pos} is reachable")
                else:
                    print(f"✗ Number {num} at {pos} is NOT reachable!")

        # Debug visualization
        driver.execute_script("""
        // Highlight everything for debugging
        var style = document.createElement('style');
        style.textContent = `
            [data-cell-idx] {
                border: 1px solid rgba(0,0,0,0.2) !important;
            }
            .trail-cell-wall--right {
                border-right: 3px solid red !important;
                background: rgba(255,0,0,0.1) !important;
            }
            .trail-cell-wall--left {
                border-left: 3px solid green !important;
                background: rgba(0,255,0,0.1) !important;
            }
            .trail-cell-wall--down {
                border-bottom: 3px solid blue !important;
                background: rgba(0,0,255,0.1) !important;
            }
            .trail-cell-wall--up {
                border-top: 3px solid yellow !important;
                background: rgba(255,255,0,0.1) !important;
            }
            .trail-cell-content {
                background: rgba(0,255,255,0.2) !important;
                border: 2px solid cyan !important;
            }
        `;
        document.head.appendChild(style);
        """)

        return GridParseResult(
            grid=grid,
            numbered_cells=numbered_cells,
            rows=size,
            cols=size,
            cell_rects={},
            blocked_edges=blocked_edges
        )
    except TimeoutException:
        raise RuntimeError("Timeout.")
    except Exception as e:
        raise RuntimeError(str(e))