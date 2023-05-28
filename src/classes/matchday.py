from typing import List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import discord_logging

log = discord_logging.get_logger()

from utils import get_random_id
from classes.game import Game
from classes.settings import DirtyMixin


@dataclass
class MatchDay(DirtyMixin):
	id: str = field(default_factory=get_random_id)
	approved_games: List[Game] = field(default_factory=list)
	pending_games: List[Game] = field(default_factory=list)
	_loading_games: List[Game] = field(default_factory=list)
	approved_start_datetime: datetime = None
	first_datetime: datetime = None
	last_datetime: datetime = None

	thread_id: str = None
	thread_removed: bool = False
	thread_complete_time: datetime = None

	predictions_thread: str = None
	discord_posted: bool = False
	spoiler_prevention: bool = False

	def add_game(self, game):
		if self.first_datetime is not None and \
				(game.date_time < self.first_datetime - timedelta(hours=4) or
				game.date_time > self.last_datetime + timedelta(hours=4)):
			return False
		if self.first_datetime is None or game.date_time < self.first_datetime:
			self.first_datetime = game.date_time
		if self.last_datetime is None or game.date_time > self.last_datetime:
			self.last_datetime = game.date_time
		for approved_game in self.approved_games:
			if approved_game.matches(game):
				game._dirty = True
				approved_game.merge(game)
				return True
		for pending_game in self.pending_games:
			if pending_game.matches(game):
				game._dirty = True
				pending_game.merge(game)
				self._loading_games.append(pending_game)
				return True
		self._loading_games.append(game)
		return True

	def sort_games(self, approve_complete=False):
		if len(self._loading_games):
			if approve_complete:
				for game in self._loading_games:
					if game.complete:
						self.approved_games.append(game)
					else:
						self.pending_games.append(game)
			else:
				self.pending_games = self._loading_games
			self._loading_games = []
		self.pending_games.sort(key=lambda game: game.date_time)
		self.approved_games.sort(key=lambda game: game.date_time)
		if len(self.approved_games):
			self.approved_start_datetime = self.approved_games[0].date_time

	def approve_game(self, source_id, target_id):
		copy_pending = []
		target_found = False
		for pending_game in self.pending_games:
			if pending_game.id == source_id:
				if target_id is not None:
					for approved_game in self.approved_games:
						if approved_game.id == target_id:
							approved_game.merge(pending_game)
							log.info(f"Merged game {pending_game} into {approved_game}")
							target_found = True
					if not target_found:
						log.warning(f"Target game not found when merging {pending_game}")
						copy_pending.append(pending_game)
				else:
					pending_game._dirty = True
					self.approved_games.append(pending_game)
					log.info(f"Approved game {pending_game}")
					target_found = True
			else:
				copy_pending.append(pending_game)
		self.pending_games = copy_pending
		return target_found

	def delete_game(self, game_id):
		new_approved_games = []
		target_found = False
		for approved_game in self.approved_games:
			if approved_game.id == game_id:
				log.info(f"Deleted game {approved_game}")
				target_found = True
			else:
				new_approved_games.append(approved_game)
		self.approved_games = new_approved_games
		new_pending_games = []
		for pending_games in self.pending_games:
			if pending_games.id == game_id:
				log.info(f"Deleted game {pending_games}")
				target_found = True
			else:
				new_pending_games.append(pending_games)
		self.pending_games = new_pending_games
		if target_found:
			self._dirty = True
		return target_found

	def approve_all_games(self):
		games_approved = len(self.pending_games)
		for game in self.pending_games:
			game._dirty = True
		self.approved_games.extend(self.pending_games)
		log.info(f"Approved {len(self.pending_games)} games for {self}")
		self.pending_games = []
		self.sort_games()
		return games_approved

	def is_complete(self):
		complete = True
		if len(self.approved_games):
			for game in self.approved_games:
				if not game.complete:
					complete = False
		else:
			for game in self.pending_games:
				if not game.complete:
					complete = False
		return complete

	def is_dirty(self):
		if self._dirty:
			return True
		for game in self.approved_games:
			if game.is_dirty():
				return True
		for game in self.pending_games:
			if game.is_dirty():
				return True
		return False

	def is_thread_dirty(self):
		if self._dirty:
			return True
		for game in self.approved_games:
			if game.is_dirty():
				return True
		return False

	def clean(self):
		self._dirty = False
		for game in self.approved_games:
			game.clean()
		for game in self.pending_games:
			game.clean()

	def __str__(self):
		return \
			f"{self.id}: " \
			f"{(self.first_datetime.strftime('%Y-%m-%d %H:%M') if self.first_datetime else 'None')} - " \
			f"{(self.last_datetime.strftime('%Y-%m-%d %H:%M') if self.last_datetime else 'None')} | " \
			f"{len(self.approved_games)} games ({len(self.pending_games)}) | " \
			f"{('Complete' if self.is_complete() else 'Not-complete')}"