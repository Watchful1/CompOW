from enum import Enum


class GameState(Enum):
	PENDING = 1
	IN_PROGRESS = 2
	COMPLETE = 3
	UNKNOWN = 4


class Winner(Enum):
	NONE = 1
	HOME = 2
	AWAY = 3
	TIED = 4


class DiscordType(Enum):
	COW = 1
	THEOW = 2
