"""Background worker for browser automation."""

import queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import traceback

from extractor import extract_zip_grid_improved
from solver import ZipSolverCore
from models import GridParseResult

result_queue = queue.Queue()

def worker_extract_and_solve():
    """Worker function to extract and solve the puzzle."""
    driver = None
    try:
        print("🚀 Starting browser...")
        opts = Options()
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--no-sandbox")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=opts
        )
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🌐 Navigating to LinkedIn Zip...")
        driver.get("https://www.linkedin.com/games/zip/")
        time.sleep(3)

        # Handle iframe if present
        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            driver.switch_to.frame(iframe)
            print("🔀 Switched to iframe")
        except Exception:
            print("ℹ️ No iframe found")

        # Extract and solve
        parse_result = extract_zip_grid_improved(driver)
        solver = ZipSolverCore(parse_result.grid, parse_result.blocked_edges)
        solution = solver.solve_zip_game()
        
        if solution:
            is_valid, message = solver.validate_solution(solution)
            if is_valid:
                result_queue.put(("SUCCESS", parse_result, solution, message))
            else:
                result_queue.put(("INVALID", parse_result, solution, message))
        else:
            result_queue.put(("NO_SOLUTION", parse_result, None, "No solution found"))
            
    except Exception as e:
        error_msg = f"Error: {e}\n{traceback.format_exc()}"
        print(error_msg)
        result_queue.put(("ERROR", None, None, error_msg))
    finally:
        if driver:
            driver.quit()
        print("🔴 Browser closed")

def create_mock_puzzle():
    """Realistic 5x5 mock puzzle with walls."""
    grid = [
        [1,  0,  0,  0,  0],
        [0,  0,  2,  0,  0],
        [0,  0,  0,  0,  0],
        [0,  3,  0,  0,  0],
        [0,  0,  0,  0,  4]
    ]
    numbered_cells = {1: (0, 0), 2: (4, 4), 3: (3, 1), 4: (1, 2)}
    cell_rects = {i: (60 + (i % 5) * 52, 60 + (i // 5) * 52, 48, 48) for i in range(25)}
    
    # Wall layout
    blocked_edges = set()
    
    return GridParseResult(
        grid=grid,
        numbered_cells=numbered_cells,
        rows=5,
        cols=5,
        cell_rects=cell_rects,
        blocked_edges=blocked_edges
    )
