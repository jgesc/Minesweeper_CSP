# Minesweeper_CSP
Solving minesweeper as a Constraint Satisfaction Problem, where the variables are the undiscovered mines, which may contain a mine or not, and the constraints are that the number of unflagged mines surrounding a cell must equal the number contained in such cell. A graph is built from these variables and constraints and all the possible solutions are searched by trying the possible values of each variable, beginning with those with the least constraints and prunning the branches in which a variable has no possible value. If no variable is assigned a value with 100% certainty, the cell with the least probability of holding a mine is opened.

To interface with the minesweeper game, an instance of a subclass of BaseAdapter has to be passed to the CSP solver, mapping the required methods to those provided by the game used. An example is included which uses my [Minesweeper HTTP API](https://github.com/jgesc/MinesweeperAPI) as the game back-end.

# Stats

On Intermediate level (16x16 board, 40 mines) achieves the following stats:
 * 62% win-rate (without loss on first cell open)
 * 38% loss-rate (all of them when opening a cell by chance is the only option)
 * ~0.2 seconds per board on average (depending on the board, some may take up to 10 seconds)
