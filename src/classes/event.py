from typing import List
from dataclasses import dataclass, field
import discord_logging

log = discord_logging.get_logger()

from utils import get_random_id
from classes.matchday import MatchDay


@dataclass
class Event:
	url: str
	id: str = field(default_factory=get_random_id)
	name: str = None
	streams: List[str] = field(default_factory=list)
	match_days: List[MatchDay] = field(default_factory=list)
	dirty: bool = False

	post_match_threads: bool = False
	match_thread_minutes_before: int = 15
	leave_thread_minutes_after: int = None
	use_pending_changes: bool = False

	discord_key: str = None
	discord_minutes_before: int = 15
	discord_roles: List[str] = field(default_factory=lambda: ['All-Notify', 'All-Matches', 'here'])

	details_url: str = None

	def is_dirty(self):
		if self.dirty:
			return True
		for match_day in self.match_days:
			if match_day.is_dirty():
				return True
		return False

	def clean(self):
		self.dirty = False
		for match_day in self.match_days:
			match_day.clean()

	def wiki_name(self):
		return "events/"+self.name.replace(" ", "-").replace("/", "-").replace(":", "").lower()

	def get_name(self):
		return self.name

	def get_match_day(self, match_day_id):
		for match_day in self.match_days:
			if match_day.id == match_day_id:
				return match_day
		return None

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
		if matches_approved > 0:
			self.dirty = True

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