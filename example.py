import json
from enum import Enum
from minesweeper_csp.game_state import GameState
from minesweeper_csp.base_adapter import BaseAdapter
from minesweeper_csp.csp import MinesweeperCSP
from http.client import HTTPConnection

class CellContent(Enum):
    UNKNOWN = -1
    EMPTY = 0
    MINE = 9

game_state_dict = {
    'First Move': GameState.FIRST_MOVE,
    'Playing': GameState.PLAYING,
    'Win': GameState.WIN,
    'Lose': GameState.LOSE
}

class MinesweeperHTTPAdapter(BaseAdapter):
    def __init__(self, host, port, width=10, height=10, mine_count=10):
        super().__init__(width=width, height=height, mine_count=mine_count)

        # Connection related settings
        self.host = host
        self.port = port
        self.connection = HTTPConnection(self.host, self.port)

        self.state_buffer = None
        self.path = None
        self.cache_dirty = True

        # The MinesweeperHTTP backend does not store flagged mines, so this
        # has to be done locally
        self.flagged_mines = None
        self.new_game(width=width, height=height, mine_count=mine_count)

    def new_game(self, width=10, height=10, mine_count=10):
        # Create game
        self.connection.request('PUT', '/', body=json.dumps({
            'width': width,
            'height': height,
            'mine_count': mine_count
        }))
        response = self.connection.getresponse()
        if response.status != 200:
            raise Exception('Could not create game, %s' % response.reason)
        id = json.loads(response.read())['id']

        self.state_buffer = None
        self.path = '/%s' % id
        self.cache_dirty = True
        self.request_game_state()

        # The MinesweeperHTTP backend does not store flagged mines, so this
        # has to be done locally
        self.flagged_mines = [[False] * height for _ in range(width)]

    def request_game_state(self):
        # If game is already finished, do not update
        if self.state_buffer and self.state_buffer['state'] in ('Win', 'Lose'):
            return

        self.connection.request('GET', self.path)
        response = self.connection.getresponse()
        if response.status != 200:
            response.read()
            raise Exception('Could not get game state, %s' % response.reason)

        self.state_buffer = json.loads(response.read())
        self.cache_dirty = False

    def ensure_up_to_date(self):
        if self.cache_dirty:
            self.request_game_state()

    def is_hidden(self, x, y):
        self.ensure_up_to_date()
        return self.state_buffer['board'][x][y] == CellContent.UNKNOWN.value

    def is_flagged(self, x, y):
        return self.flagged_mines[x][y]

    def get_adjacent_mines(self, x, y):
        self.ensure_up_to_date()
        cell_value = self.state_buffer['board'][x][y]
        return cell_value if 0 <= cell_value < 9 else 0

    def flag_cell(self, x, y):
        self.flagged_mines[x][y] = True

    def open_cell(self, x, y):
        # If game is already finished, do not update
        if self.state_buffer and self.state_buffer['state'] in ('Win', 'Lose'):
            return
        self.cache_dirty = True

        self.connection.request('POST', self.path, body=json.dumps({
            'x': x,
            'y': y
        }))
        response = self.connection.getresponse()
        if response.status != 200:
            raise Exception('Could not open cell, %s' % response.reason)
        response_body = json.loads(response.read())
        new_state = response_body['new_state']
        self.state_buffer['state'] = new_state

    def get_game_state(self):
        self.ensure_up_to_date()
        return game_state_dict[self.state_buffer['state']]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_mine_count(self):
        return self.mine_count


# Main
game = MinesweeperHTTPAdapter(
    'localhost', 8080, width=8, height=8, mine_count=10)
result = {GameState.WIN: 0, GameState.LOSE: 0}
for i in range(100):
    print(i)
    mcsp = MinesweeperCSP(game)
    result[mcsp.solve()] += 1
    game.new_game(8, 8, 10)
print('Easy: ', result)
