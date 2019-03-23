from enum import Enum


class GameState(Enum):
	PENDING = 1
	IN_PROGRESS = 2
	COMPLETE = 3
	UNKNOWN = 4
