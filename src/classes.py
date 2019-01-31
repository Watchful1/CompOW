from enum import Enum
from datetime import timedelta
import logging
import bisect


log = logging.getLogger("bot")


class GameState(Enum):
	PENDING = 1
	IN_PROGRESS = 2
	COMPLETE = 3
	UNKNOWN = 4


class Team:
	def __init__(self, name, country):
		self.name = "TBD" if name is None else name
		self.country = "TBD" if country is None else country

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

	def __lt__(self, other):
		return self.start < other.start


class Stage:
	def __init__(self, stage):
		self.start = None
		self.last = None
		self.matches = []
		self.stage = stage

		self.dirty = False
		self.thread = None
		self.streams = []

		self.state = GameState.PENDING

	def add_match(self, match):
		bisect.insort(self.matches, match)
		self.add_match_time(match.start)
		if match.dirty:
			self.dirty = True

	def add_match_time(self, match_time):
		if self.start is None or self.start > match_time:
			self.start = match_time
		if self.last is None or self.last < match_time:
			self.last = match_time

	def clean(self):
		self.dirty = False
		for match in self.matches:
			match.dirty = False

	def rebuild_start_last(self):
		self.start = None
		self.last = None
		matches_temp = []
		for match in self.matches:
			self.add_match_time(match.start)
			bisect.insort(matches_temp, match)
		self.matches = matches_temp


class Event:
	def __init__(self, competition):
		self.start = None
		self.last = None
		self.competition = competition

		self.matches = {}

		self.stages = []

	def add_match(self, match):
		if match.id in self.matches:
			if self.matches[match.id].start != match.start:
				log.info(f"Updating match start in event: {match.id} : {self.matches[match.id].start} : {match.start}")
				self.matches[match.id].start = match.start
				self.rebuild_start_last()
			if self.matches[match.id].url != match.url:
				log.warning(f"Url updated for match: {match.id}")
			if self.matches[match.id].home != match.home:
				log.warning(f"Home updated for match: {match.id} : {match.home}")
			if self.matches[match.id].away != match.away:
				log.warning(f"Away updated for match: {match.id} : {match.away}")
		else:
			log.info(f"Adding match to event: {match.id} : {match.home.name} vs {match.away.name}")
			self.matches[match.id] = match
			self.add_match_time(match.start)

	def add_match_time(self, match_time):
		if self.start is None or self.start > match_time:
			self.start = match_time
		if self.last is None or self.last < match_time:
			self.last = match_time

	def rebuild_start_last(self):
		self.start = None
		self.last = None
		for match in self.matches:
			self.add_match_time(match.start)
		for stage in self.stages:
			stage.rebuild_start_last()

	def match_fits(self, start, competition):
		if self.competition != competition:
			return False
		return self.start - timedelta(hours=3) < start < self.last + timedelta(hours=3)

	def clean(self):
		for stage in self.stages:
			stage.clean()

	def add_match_to_stage(self, match):
		fit_stage = False
		for stage in self.stages:
			if stage.stage == match.stage:
				fit_stage = True
				in_stage = False
				for stage_match in stage.matches:
					if stage_match.id == match.id:
						in_stage = True
						if match.dirty:
							stage.dirty = True
						break

				if not in_stage:
					stage.add_match(match)

		if not fit_stage:
			stage = Stage(match.stage)
			stage.add_match(match)
			self.stages.append(stage)

	def game_state(self):
		all_complete = True
		for stage in self.stages:
			if stage.state == GameState.IN_PROGRESS:
				return GameState.IN_PROGRESS
			if stage.state != GameState.COMPLETE:
				all_complete = False

		if all_complete:
			return GameState.COMPLETE
		else:
			return GameState.PENDING

	def __str__(self):
		return f"{self.competition} : {self.start}"
