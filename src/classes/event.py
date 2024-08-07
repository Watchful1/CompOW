from typing import List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import discord_logging

import utils

log = discord_logging.get_logger()

from utils import get_random_id, minutes_to_start, utcnow
from classes.matchday import MatchDay
from classes.settings import DirtyMixin


@dataclass
class Event(DirtyMixin):
	url: str = None
	id: str = field(default_factory=get_random_id)
	name: str = None
	streams: List[str] = field(default_factory=list)
	match_days: List[MatchDay] = field(default_factory=list)

	post_match_threads: bool = False
	match_thread_minutes_before: int = 15
	leave_thread_minutes_after: int = None
	use_pending_changes: bool = False

	discord_key: str = "cow"
	discord_minutes_before: int = 15
	discord_roles: List[str] = field(default_factory=lambda: utils.DEFAULT_ROLES.copy())

	details_url: str = None
	cached_name: str = None
	last_parsed: datetime = None
	last_pinged: datetime = None

	def should_parse(self):
		if self.last_parsed is None:
			return True
		next_game = self.get_next_game(approved=True, pending=True)
		if next_game is not None and minutes_to_start(next_game.date_time) < (4 * 60):  # if less than 4 hours to game start, scan faster
			return True
		if utcnow(offset=-20 * 60) > self.last_parsed:  # otherwise only scan every 20 minutes
			return True
		return False

	def is_dirty(self):
		if self._dirty:
			return True
		for match_day in self.match_days:
			if match_day.is_dirty():
				return True
		return False

	def clean(self):
		self._dirty = False
		for match_day in self.match_days:
			match_day.clean()

	def wiki_name(self):
		return "events/"+self.name.replace(" ", "-").replace("/", "-").replace(":", "").replace("---", "-").replace("--", "-").lower()

	def get_match_day(self, match_day_id):
		for match_day in self.match_days:
			if match_day.id == match_day_id:
				return match_day
		return None

	def get_next_game(self, approved=True, pending=False, complete=True):
		for game in self.get_games(approved, pending):
			if not complete:
				return game
			if not game.complete:
				return game
		return None

	def get_games(self, approved=True, pending=False):
		games = []
		for match_day in self.match_days:
			if approved:
				for game in match_day.approved_games:
					games.append(game)
			if pending:
				for game in match_day.pending_games:
					games.append(game)
		games.sort(key=lambda game: game.date_time)
		return games

	def get_match_day_from_match_id(self, match_id):
		for match_day in self.match_days:
			for match in match_day.approved_games:
				if match.id == match_id:
					return match_day
			for match in match_day.pending_games:
				if match.id == match_id:
					return match_day
		return None

	def add_game(self, game):
		for match_day in self.match_days:
			if match_day.add_game(game):
				return
		match_day = MatchDay()
		match_day.add_game(game)
		self.match_days.append(match_day)
		self.match_days.sort(key=lambda match_day: match_day.first_datetime)

	def sort_matches(self, approve_complete=False):
		for match_day in self.match_days:
			match_day.sort_games(approve_complete)

	def approve_all_games(self):
		matches_approved = 0
		for match_day in self.match_days:
			matches_approved += match_day.approve_all_games()

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