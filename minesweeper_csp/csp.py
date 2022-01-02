from enum import Enum, auto
from .game_state import GameState
import random
import itertools

class GameAction(Enum):
    OPEN = auto()
    FLAG = auto()

class Variable:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.constraints = set()

    def add_constraint(self, x, y):
        self.constraints.add((x, y))
        if len(self.constraints) > 8:
            raise Exception(
                'A variable cannot be assotiated to more than 8 constraints')

class Constraint:
    def __init__(self, x, y, sum):
        if not 0 <= sum < 9:
            raise ValueError('Adjacent mine count (%d) must be in [0, 9)' % sum)

        self.x = x
        self.y = y
        self.sum = sum
        self.variables = set()

    def add_variable(self, x, y):
        self.variables.add((x, y))
        if len(self.variables) > 8:
            raise Exception('A constraint cannot have more than 8 variables')

class MinesweeperCSP:
    def __init__(self, game):
        self.game = game
        self.width = game.get_width()
        self.height = game.get_height()
        self.mine_count = game.get_mine_count()
        # Constraint graph
        self.constraints = {}
        self.variables = {}


    def create_constraint_graph(self):
        self.constraints = {}
        self.variables = {}
        # Iterate board and register constraints
        for x in range(self.width):
            for y in range(self.height):
                # Check if it is a constraint
                if self.game.get_adjacent_mines(x, y) > 0:
                    # Register constraint
                    self.register_constraint(x, y)


    def register_constraint(self, x, y):
        # Find unsolved constraint variables
        flagged_mines, constraint_variables = \
            self.find_constraint_variables(x, y)
        # Check if there is any
        if constraint_variables:
            # Create constraint
            adjacent_mine_count = self.game.get_adjacent_mines(x, y)
            constraint_value = adjacent_mine_count - len(flagged_mines)
            new_constraint = Constraint(x, y, constraint_value)
            self.constraints[(x, y)] = new_constraint
            # Register variables
            for variable_position in constraint_variables:
                # Get or create
                variable = self.variables.setdefault(variable_position, \
                    Variable(*variable_position))
                # Add constraint and variable
                variable.add_constraint(x, y)
                new_constraint.add_variable(*variable_position)


    def neighbours(self, x, y):
        for i in range(-1, 2):
            if 0 <= x-i < self.width:
                for j in range(-1, 2):
                    if 0 <= y-j < self.height:
                        if not i == j == 0:
                            yield (x-i, y-j)


    def find_constraint_variables(self, x, y):
        # Get neighbouring cells and classify them
        hidden_neighbours = {neighbour for neighbour in self.neighbours(x, y) \
            if self.game.is_hidden(*neighbour)}
        flagged_neighbours = {neighbour for neighbour in hidden_neighbours \
            if self.game.is_flagged(*neighbour)}
        unflagged_neighbours = hidden_neighbours - flagged_neighbours

        return flagged_neighbours, unflagged_neighbours


    def solve_trivial_constraints(self):
        solved_constraints = []
        for constraint in self.constraints.values():
            if constraint.sum == 0:
                for variable in constraint.variables:
                    solved_constraints.append((GameAction.OPEN, variable))
            elif constraint.sum == len(constraint.variables):
                for variable in constraint.variables:
                    solved_constraints.append((GameAction.FLAG, variable))

        return solved_constraints


    def attempt_simplify_constraints(self):
        constraints_simplified = False
        for a in self.constraints.values():
            for b in self.constraints.values():
                if not a is b:
                    if a.variables > b.variables:
                        a.variables -= b.variables
                        a.sum -= b.sum
                        constraints_simplified = True

        return constraints_simplified


    def apply_actions(self, actions):
        for action in actions:
            type, (x, y) = action
            if type == GameAction.OPEN:
                self.game.open_cell(x, y)
            else:
                self.game.flag_cell(x, y)


    def search_solution(self):
        def recursive_search(possible_solutions, variable_values, \
            current_variables, current_constraints):
            # Check if all the variables have been solved
            if not current_variables:
                # This makes the current configuration a possible solution
                possible_solutions.append(variable_values)
                return

            # Else pick the variablle with least constraints and check its
            # possible values
            variable = min(current_variables.values(),
                key=lambda x: len(x.constraints))
            values = tuple()

            # Check if it is possible for this variable to be 1 (the cell
            # contains a mine)
            for constraint in variable.constraints:
                # If any of its constraints has been satisfied, then this
                # variable cannot be 1 (this cell cannot contain a mine)
                if current_constraints[constraint].sum == 0:
                    break
            else:
                # Else, 1 is a possible value of this variable (this cell may
                # contain a mine)
                values += (1,)

            # Check if it is possible for this variable to be 0 (the cell
            # is empty)
            for constraint in variable.constraints:
                # If the remaining unset variables of one of its constraints is
                # equal to its constraint value, this variable cannot be 0
                unset_variables = current_constraints[constraint].variables
                if len(unset_variables) == current_constraints[constraint].sum:
                    break
            else:
                # Else, this variable being 0 is a possible solution
                values += (0,)

            # If there are any possible solutions with this current
            # configuration, probe them, else this branch is discarded
            if values:
                # Remove current variable
                del current_variables[(variable.x, variable.y)]
                for constraint in variable.constraints:
                    current_constraints[constraint].variables.remove( \
                        (variable.x, variable.y))

                if 0 in values:
                    # Set current value
                    current_value = (((variable.x, variable.y), 0),)
                    # Perform search
                    recursive_search(possible_solutions, \
                        variable_values + current_value, current_variables, \
                        current_constraints)

                if 1 in values:
                    # Set current value
                    current_value = (((variable.x, variable.y), 1),)
                    # Modify tentative constraint values
                    for constraint in variable.constraints:
                        current_constraints[constraint].sum -= 1
                    # Perform search
                    recursive_search(possible_solutions, \
                        variable_values + current_value, current_variables, \
                        current_constraints)
                    # Restore constraint values
                    for constraint in variable.constraints:
                        current_constraints[constraint].sum += 1

                # Restore variable
                current_variables[(variable.x, variable.y)] = variable
                for constraint in variable.constraints:
                    current_constraints[constraint].variables.add( \
                        (variable.x, variable.y))
        # END recursive_search

        variable_values = tuple()
        current_variables = self.variables
        current_constraints = self.constraints
        possible_solutions = []

        # Perform recursive search
        recursive_search(possible_solutions, variable_values, \
            current_variables, current_constraints)

        # Count mines and return those variables whose value is the same in all
        # the configurations. If no value found, guess the variable with less
        # chances of being a mine
        mine_counter = {}
        for configuration in possible_solutions:
            for key, value in configuration:
                mine_counter[key] = mine_counter.setdefault(key, 0) + value

        values_found = {
            (GameAction.FLAG if v else GameAction.OPEN, k) \
            for k, v in mine_counter.items() \
            if v == len(possible_solutions) or v == 0}

        if values_found:
            # Solutions found with 100% certainty
            return values_found
        elif mine_counter:
            # Solutions found, pick the one with best chance of not being mine
            return [(GameAction.OPEN, min(mine_counter))]
        else:
            # No possible solutions found. This happens when the remaining
            # hidden cells get landlocked
            hidden_cells = [cell for cell in itertools.product( \
                range(self.width), range(self.height)) if self.game.is_hidden(*cell) \
                and not self.game.is_flagged(*cell)]
            return [(GameAction.OPEN, random.choice(hidden_cells))]


    def step(self):
        # Check if game is not finished
        if self.game.get_game_state() in (GameState.LOSE, GameState.WIN):
            return

        # Check if it is the first move
        if self.game.get_game_state() == GameState.FIRST_MOVE:
            # Then open random cell
            self.game.open_cell(
                random.choice(range(self.width)),
                random.choice(range(self.height))
            )
            return

        # Generate constraint graph
        self.create_constraint_graph()

        # Attempt to solve trivial constraints
        trivial_constraints = self.solve_trivial_constraints()
        if trivial_constraints:
            self.apply_actions(trivial_constraints)
            return

        # Attempt to simplify and then solve trivial constraints
        while True:
            if not self.attempt_simplify_constraints():
                break
        trivial_constraints = self.solve_trivial_constraints()
        if trivial_constraints:
            self.apply_actions(trivial_constraints)
            return

        # Search for possible solutions
        self.create_constraint_graph()
        search_solutions = self.search_solution()
        self.apply_actions(search_solutions)


    def solve(self):
        # While game is not finished, step
        while self.game.get_game_state() not in \
            (GameState.LOSE, GameState.WIN):
            # Step
            self.step()

        return self.game.get_game_state()
