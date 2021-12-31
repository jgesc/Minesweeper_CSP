from enum import Enum, auto

class GameState(Enum):
    FIRST_MOVE = auto()
    PLAYING = auto()
    WIN = auto()
    LOSE = auto()
