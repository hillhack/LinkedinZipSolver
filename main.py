"""Main application for Zip Game Solver."""

import tkinter as tk
from tkinter import ttk, messagebox
import queue
import threading

from worker import worker_extract_and_solve, result_queue, create_mock_puzzle
from visualizer import ZipGameVisualizer
from solver import ZipSolverCore

class ZipSolverApp:
    def __init__(self, root):
        self.root = root
        root.title("Zip Game Solver")
        root.geometry("500x400")
        self.build_ui()
        self.root.after(200, self.poll_result_queue)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main, text="Zip Game Solver", font=("Arial", 18, "bold")).pack(pady=10)
        ttk.Label(main, text="Automatically solve LinkedIn Zip puzzles", font=("Arial", 10)).pack(pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=20)
        
        self.solve_btn = ttk.Button(btn_frame, text="🎮 Solve Live Puzzle", 
                                   command=self.solve_live, width=20)
        self.solve_btn.pack(pady=10)
        
        ttk.Button(btn_frame, text="🧪 Test 5x5 Puzzle", 
                  command=self.test_solver, width=20).pack(pady=5)
        
        ttk.Button(btn_frame, text="❌ Exit", 
                  command=self.root.quit, width=20).pack(pady=5)
        
        # Status area
        self.status_label = ttk.Label(main, text="Ready to solve puzzles!", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(main, mode='indeterminate')
        
        # Instructions
        instructions = """Instructions:
• Make sure you're logged into LinkedIn
• Navigate to the Zip game first
• Click 'Solve Live Puzzle' 
• Use 'Test 5x5 Puzzle' to verify solver"""
        
        ttk.Label(main, text=instructions, justify=tk.LEFT, font=("Arial", 9)).pack(pady=10)

    def solve_live(self):
        """Solve the current puzzle on LinkedIn."""
        self.solve_btn.config(state=tk.DISABLED)
        self.status_label.config(text="🔄 Starting browser and extracting puzzle...")
        self.progress.pack(fill=tk.X, pady=5)
        self.progress.start()
        
        threading.Thread(target=worker_extract_and_solve, daemon=True).start()

    def test_solver(self):
        """Test the solver with the 5x5 mock puzzle."""
        try:
            self.status_label.config(text="🧪 Testing 5x5 mock puzzle...")
            
            test_parse = create_mock_puzzle()
            solver = ZipSolverCore(test_parse.grid, test_parse.blocked_edges)
            solution = solver.solve_zip_game()
            
            if solution:
                is_valid, message = solver.validate_solution(solution)
                if is_valid:
                    self.status_label.config(text="✅ 5x5 puzzle solved!", foreground="green")
                    ZipGameVisualizer(self.root, test_parse, solution)
                    messagebox.showinfo("Test Success", 
                                      f"✅ 5x5 puzzle solved successfully!\n\n"
                                      f"Path length: {len(solution)} steps\n"
                                      f"Numbers: {sorted(test_parse.numbered_cells.keys())}\n"
                                      f"Walls: {len(test_parse.blocked_edges)}")
                else:
                    self.status_label.config(text="❌ Solution invalid", foreground="red")
                    messagebox.showerror("Test Failed", f"Solution invalid: {message}")
            else:
                self.status_label.config(text="❌ No solution found", foreground="red")
                messagebox.showerror("Test Failed", "No solution found for 5x5 puzzle")
                
        except Exception as e:
            self.status_label.config(text="❌ Test error", foreground="red")
            messagebox.showerror("Test Error", f"Test failed: {e}")

    def poll_result_queue(self):
        """Check for results from the worker thread."""
        try:
            while True:
                result_type, parse_result, solution, message = result_queue.get_nowait()
                
                self.solve_btn.config(state=tk.NORMAL)
                self.progress.stop()
                self.progress.pack_forget()
                
                if result_type == "SUCCESS":
                    self.status_label.config(text="✅ Puzzle solved successfully!", foreground="green")
                    ZipGameVisualizer(self.root, parse_result, solution)
                    messagebox.showinfo("Success", 
                                      f"Solution found!\n\n"
                                      f"Grid: {parse_result.rows}x{parse_result.cols}\n"
                                      f"Numbers: {sorted(parse_result.numbered_cells.keys())}\n"
                                      f"Walls: {len(parse_result.blocked_edges)}\n\n"
                                      f"{message}")
                    
                elif result_type == "INVALID":
                    self.status_label.config(text="⚠️ Solution has issues", foreground="orange")
                    if solution:
                        ZipGameVisualizer(self.root, parse_result, solution)
                    messagebox.showwarning("Validation", message)
                    
                elif result_type == "NO_SOLUTION":
                    self.status_label.config(text="❌ No solution found", foreground="red")
                    if parse_result:
                        messagebox.showerror("No Solution", 
                                           f"No solution found for this puzzle.\n\n"
                                           f"Grid: {parse_result.rows}x{parse_result.cols}\n"
                                           f"Numbers: {sorted(parse_result.numbered_cells.keys())}\n"
                                           f"Walls: {len(parse_result.blocked_edges)}")
                    else:
                        messagebox.showerror("No Solution", "No solution found.")
                    
                elif result_type == "ERROR":
                    self.status_label.config(text="❌ Error occurred", foreground="red")
                    messagebox.showerror("Error", f"Failed to extract puzzle:\n\n{message}")
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(500, self.poll_result_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZipSolverApp(root)
    root.mainloop()
