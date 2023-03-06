from typing import List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import jsons
import discord_logging

log = discord_logging.get_logger()


def base36encode(integer: int) -> str:
	chars = '0123456789abcdefghijklmnopqrstuvwxyz'
	sign = '-' if integer < 0 else ''
	integer = abs(integer)
	result = ''
	while integer > 0:
		integer, remainder = divmod(integer, 36)
		result = chars[remainder] + result
	return sign + result


@dataclass
class Team:
	name: str = None
	score: int = None


@dataclass
class Game:
	id: str = field(default_factory=lambda: base36encode(random.randrange(1679616,  60466176)))
	home: Team = field(default_factory=Team)
	away: Team = field(default_factory=Team)
	complete: bool = False
	datetime: datetime = None

	def status(self):
		if self.complete:
			return "Complete"
		if self.home.score is not None or self.away.score is not None:
			return "In-progress"
		return "Not-started"

	def matches(self, game):
		return self.home.name == game.home.name and self.away.name == game.away.name and self.datetime == game.datetime

	def merge(self, game):
		self.home = game.home
		self.away = game.away
		self.complete = game.complete
		self.datetime = game.datetime

	def render_datetime(self):
		if self.datetime is None:
			return "None"
		return self.datetime.strftime('%Y-%m-%d %H:%M')

	def __str__(self):
		return f"{self.id} : {self.home.name} vs {self.away.name} : {self.home.score}-{self.away.score} : {self.status()} : {self.render_datetime()}"


@dataclass
class MatchDay:
	approved_games: List[Game] = field(default_factory=list)
	pending_games: List[Game] = field(default_factory=list)
	first_datetime: datetime = None
	last_datetime: datetime = None

	def add_game(self, game):
		if self.first_datetime is not None and \
				(game.datetime < self.first_datetime - timedelta(hours=4) or
				game.datetime > self.last_datetime + timedelta(hours=4)):
			return False
		self.pending_games.append(game)
		if self.first_datetime is None or game.datetime < self.first_datetime:
			self.first_datetime = game.datetime
		if self.last_datetime is None or game.datetime > self.last_datetime:
			self.last_datetime = game.datetime
		return True

	def is_complete(self):
		complete = True
		for game in self.pending_games:
			if not game.complete:
				complete = False
		return complete

	def merge_games(self):
		unmatched_games = []
		for pending_game in self.pending_games:
			matched = False
			for approved_game in self.approved_games:
				if approved_game.matches(pending_game):
					approved_game.merge(pending_game)
					matched = True
					break
			if not matched:
				unmatched_games.append(pending_game)
		self.pending_games = unmatched_games

	def __str__(self):
		return \
			f"{self.first_datetime.strftime('%Y-%m-%d %H:%M')} - " \
			f"{self.last_datetime.strftime('%Y-%m-%d %H:%M')} | " \
			f"{len(self.pending_games)} games | " \
			f"{('Complete' if self.is_complete() else 'Not-complete')}"


@dataclass
class Event:
	url: str
	name: str = None
	streams: List[str] = field(default_factory=list)
	match_days: List[MatchDay] = field(default_factory=list)

	def wiki_name(self):
		return "events/"+self.name.replace(" ", "-").replace("/", "-").replace(":", "").lower()

	def render_reddit(self):
		bldr = ["##", self.name, "\n\n"]
		for match_day in self.match_days:
			bldr.append("###")
			bldr.append(str(match_day))
			bldr.append("\n\n")
			bldr.append(f"Approved | Pending\n---|---\n")
			i = 0
			while True:
				if i < len(match_day.approved_games):
					bldr.append(str(match_day.approved_games[i]))
				bldr.append(" | ")
				if i < len(match_day.pending_games):
					bldr.append(str(match_day.pending_games[i]))
				bldr.append("\n")
				i += 1
				if i >= len(match_day.approved_games) and i >= len(
						match_day.pending_games):
					break

			bldr.append("\n\n")

		event_string = str(jsons.dumps(self, cls=Event, strip_nulls=True))

		bldr.append("[](#datatag")
		bldr.append(event_string)
		bldr.append(")")

		return ''.join(bldr)

	def add_game(self, game):
		for match_day in self.match_days:
			if match_day.add_game(game):
				return
		match_day = MatchDay()
		match_day.add_game(game)
		self.match_days.append(match_day)
		self.match_days.sort(key=lambda match_day: match_day.first_datetime)

	def log(self):
		log.info(self.name)
		for stream in self.streams:
			log.info(stream)
		log.info("")

		for match_day in self.match_days:
			log.info(match_day)
			for game in match_day.pending_games:
				log.info(game)
			log.info("")

	def __str__(self):
		return f"{self.name} - {len(self.match_days)} days"
