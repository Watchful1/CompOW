from typing import List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import discord_logging

log = discord_logging.get_logger()

from utils import get_random_id
from classes.team import Team


@dataclass
class Game:
	id: str = field(default_factory=get_random_id)
	home: Team = field(default_factory=Team)
	away: Team = field(default_factory=Team)
	complete: bool = False
	date_time: datetime = None

	post_thread_id: str = None
	dirty: bool = False

	def status(self):
		if self.complete:
			return "Complete"
		if self.home.score is not None or self.away.score is not None:
			return "In-progress"
		return "Not-started"

	def matches(self, game):
		return (self.home.name == game.home.name or (self.home.name is None and game.home.name is not None)) and \
			(self.away.name == game.away.name or (self.away.name is None and game.away.name is not None)) and \
			self.date_time == game.date_time

	def merge(self, game):
		if self.home != game.home:
			log.debug(f"dirty home {self.id}: {self.home} != {game.home}")
			self.dirty = True
			self.home = game.home
		if self.away != game.away:
			log.debug(f"dirty away {self.id}: {self.away} != {game.away}")
			self.dirty = True
			self.away = game.away
		if self.complete is not game.complete:
			log.debug(f"dirty complete {self.id}: {self.complete} != {game.complete}")
			self.dirty = True
			self.complete = game.complete
		if self.date_time != game.date_time:
			log.debug(f"dirty date_time {self.id}: {self.date_time} != {game.date_time}")
			self.dirty = True
			self.date_time = game.date_time

	def render_datetime(self):
		if self.date_time is None:
			return "None"
		return self.date_time.strftime('%Y-%m-%d %H:%M')

	def __str__(self):
		return f"{self.id}: {self.home.name} vs {self.away.name} : {self.home.score}-{self.away.score} : {self.status()} : {self.render_datetime()}"
