The LinkedIn ZIP puzzle is essentially:

A Hamiltonian Path with fixed numbered checkpoints

You must visit every cell exactly once (or at least all free cells once).

You start at number 1.

You finish at the highest number (here 10).

You must pass through the numbers in order (1 → 2 → 3 → … → 10).

You cannot cross your own path.

Walls block you.

If you get stuck, you backtrack to the previous number.

This is exactly the same as:

✔ A maze solver
✔ + visiting all cells (Hamiltonian path)
✔ + ordered checkpoints
Puzzle Rules (The Game You Are Solving)
✔ The puzzle is a grid-based Hamiltonian path with constraints:

    Start at number 1

    End at the largest number (usually 9 or 10)

    Visit numbers in order:
    1 → 2 → 3 → … → N

    Every free cell must be visited exactly once

    You cannot cross your own path

    You cannot revisit a cell

    Red bars are walls (impassable)

    If there is no valid move → backtrack

➡️ This is NOT A*.
➡️ This is NOT shortest-path.
➡️ This is a DFS backtracking Hamiltonian path search.