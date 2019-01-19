from enum import Enum
from datetime import timedelta


class GameState(Enum):
	PENDING = 1
	IN_PROGRESS = 2
	COMPLETE = 3
	UNKNOWN = 4


class Team:
	def __init__(self, name, country):
		self.name = name
		self.country = country

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.__dict__ == other.__dict__


class Match:
	def __init__(self, id, start, home, away, url):
		self.id = id
		self.start = start
		self.home = home
		self.away = away

		self.state = GameState.PENDING
		self.home_score = 0
		self.away_score = 0
		self.winner = None
		self.url = url
		self.streams = []
		self.competition = None
		self.stage = None

		self.dirty = False

	def __str__(self):
		return f"{self.home.name} vs {self.away.name} : {self.start}"


class Event:
	def __init__(self, match, competition, stage):
		self.start = match.start
		self.last = match.start
		self.matches = [match]
		self.competition = competition
		self.stage = stage

		self.dirty = False
		self.thread = None
		self.streams = []
		self.state = GameState.PENDING
		self.previous_sticky = None

	def add_match(self, match):
		self.matches.append(match)
		self.last = match.start

	def match_fits(self, match):
		return self.start - timedelta(hours=3) < match.start < self.last + timedelta(hours=3)

	def clean(self):
		self.dirty = False
		for match in self.matches:
			match.dirty = False

	def __str__(self):
		return f"{self.competition} - {self.stage} : {self.start}"
