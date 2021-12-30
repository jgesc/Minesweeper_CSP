from Enum import enum, auto

class GameState(enum):
    FIRST_MOVE = auto()
    PLAYING = auto()
    WIN = auto()
    LOSE = auto()

class BaseAdapter:
    def __init__(self, width=10, height=10, mine_count=10):
        pass

    def is_hidden(self, x, y):
        # Should return True if the cell has been revealed, else return False
        pass

    def is_flagged(self, x, y):
        # Should return True if the cell has been flagged, else return False
        pass

    def get_adjacent_mines(self, x, y):
        # Should return the number of adjacent mines if the cell has been
        # revealed, else return 0
        pass

    def flag_cell(self, x, y):
        # Set a cell as flagged
        pass

    def open_cell(self, x, y):
        # Open a cell
        pass

    def get_game_state(self):
        # Return the corresponding GameState value
        pass
