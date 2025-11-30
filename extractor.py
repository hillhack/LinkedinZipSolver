"""Grid extraction for LinkedIn Zip."""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import math

from models import GridParseResult

def extract_zip_grid_improved(driver: webdriver.Chrome) -> GridParseResult:
    """Minimal grid extraction."""
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cell-idx]'))
        )

        cell_elems = driver.find_elements(By.CSS_SELECTOR, '[data-cell-idx]')
        if not cell_elems:
            raise RuntimeError("No cells.")

        # Short JS for borders
        cell_styles = driver.execute_script("""
var s = {};
document.querySelectorAll('[data-cell-idx]').forEach(el => {
  var i = parseInt(el.getAttribute('data-cell-idx'));
  if (!isNaN(i)) {
    var a = getComputedStyle(el, '::after');
    s[i] = {
      t: a.borderTopWidth+'|'+a.borderTopColor,
      r: a.borderRightWidth+'|'+a.borderRightColor,
      b: a.borderBottomWidth+'|'+a.borderBottomColor,
      l: a.borderLeftWidth+'|'+a.borderLeftColor
    };
  }
});
return s;
""")

        size = int(math.sqrt(len(cell_elems)))
        grid = [[0] * size for _ in range(size)]
        numbered_cells = {}
        for el in cell_elems:
            idx_attr = el.get_attribute('data-cell-idx')
            if idx_attr and idx_attr.isdigit():
                idx = int(idx_attr)
                r, c = divmod(idx, size)
                text = el.text.strip()
                if text.isdigit():
                    val = int(text)
                    grid[r][c] = val
                    numbered_cells[val] = (r, c)

        blocked_edges = set()
        wall_colors = ['rgb(0, 0, 0)', 'rgb(34, 34, 34)', 'rgb(51, 51, 51)', 'rgba(0, 0, 0, 1)', 'rgba(197, 168, 164, 0.75)', 'rgb(197, 168, 164)']
        dirs = [('t', (0,-1)), ('r', (1,0)), ('b', (0,1)), ('l', (-1,0))]

        def is_wall(w, col):
            return w != '0px' and any(wc in col.lower() for wc in wall_colors)

        for idx_str, styles in cell_styles.items():
            idx = int(idx_str)
            r, c = divmod(idx, size)
            for dname, (dr, dc) in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    w, col = styles[dname].split('|')
                    if is_wall(w, col):
                        blocked_edges.add(frozenset({(r, c), (nr, nc)}))

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
