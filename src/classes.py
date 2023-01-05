from typing import List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import discord_logging

log = discord_logging.get_logger()

import liquipedia_parser


@dataclass
class Team:
	name: str = None
	score: int = None


@dataclass
class Game:
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

	def render_datetime(self):
		if self.datetime is None:
			return "None"
		return self.datetime.strftime('%Y-%m-%d %H:%M')

	def __str__(self):
		return f"{self.home.name} vs {self.away.name} : {self.home.score}-{self.away.score} : {self.status()} : {self.render_datetime()}"


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
		return "events/"+self.name.replace(" ", "-").replace(":", "")

	def add_game(self, game):
		for match_day in self.match_days:
			if match_day.add_game(game):
				return
		match_day = MatchDay()
		match_day.add_game(game)
		self.match_days.append(match_day)
		self.match_days.sort(key=lambda match_day: match_day.first_datetime)

	def parse_from_url(self):
		games, event_name, streams = liquipedia_parser.parse_event(self.url)

		if self.name is not None and event_name != self.name:
			log.warning(f"Event name changed from `{self.name}` to `{event_name}`")
		self.name = event_name

		changed = False
		if len(self.streams) != 0:
			if len(self.streams) != len(streams):
				changed = True
			else:
				for i in range(len(streams)):
					if self.streams[i] != streams[i]:
						changed = True
		if changed:
			log.warning(f"Event {self.name} streams changed from `{'`, `'.join(self.streams)}` to `{'`, `'.join(streams)}`")
		self.streams = streams

		for game in games:
			self.add_game(game)
