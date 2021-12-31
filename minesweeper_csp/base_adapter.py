class BaseAdapter:
    def __init__(self, width=10, height=10, mine_count=10):
        self.width = width
        self.height = height
        self.mine_count = mine_count

    def is_hidden(self, x, y):
        # Should return True if the cell has been revealed, else return False
        # A flagged cell is considered hidden
        raise NotImplementedError()

    def is_flagged(self, x, y):
        # Should return True if the cell has been flagged, else return False
        raise NotImplementedError()

    def get_adjacent_mines(self, x, y):
        # Should return the number of adjacent mines if the cell has been
        # revealed, else return 0
        raise NotImplementedError()

    def flag_cell(self, x, y):
        # Set a cell as flagged
        raise NotImplementedError()

    def open_cell(self, x, y):
        # Open a cell
        raise NotImplementedError()

    def get_game_state(self):
        # Return the corresponding GameState value
        raise NotImplementedError()

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_mine_count(self):
        return self.mine_count
