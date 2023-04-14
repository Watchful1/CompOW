from typing import List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import jsons
import discord_logging

log = discord_logging.get_logger()


id_range_start = int("10000", 36)
id_range_end = int("zzzzz", 36)


def base36encode(integer: int) -> str:
	chars = '0123456789abcdefghijklmnopqrstuvwxyz'
	sign = '-' if integer < 0 else ''
	integer = abs(integer)
	result = ''
	while integer > 0:
		integer, remainder = divmod(integer, 36)
		result = chars[remainder] + result
	return sign + result


def get_random_id():
	return base36encode(random.randrange(id_range_start, id_range_end))


@dataclass
class Team:
	name: str = None
	score: int = None

	def set_score(self, score):
		if score is not None:
			self.score = int(score)

	def get_name(self):
		if self.name is None:
			return "TBD"
		return self.name

	def __eq__(self, other):
		if not isinstance(other, Team):
			return False
		return self.name == other.name and self.score == other.score

	def __str__(self):
		return f"{self.name}: {self.score}"


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


@dataclass
class MatchDay:
	id: str = field(default_factory=get_random_id)
	approved_games: List[Game] = field(default_factory=list)
	pending_games: List[Game] = field(default_factory=list)
	loading_games: List[Game] = field(default_factory=list)
	approved_start_datetime: datetime = None
	first_datetime: datetime = None
	last_datetime: datetime = None
	dirty: bool = False

	thread_id: str = None

	predictions_thread: str = None
	match_thread: str = None
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
				approved_game.merge(game)
				return True
		for pending_game in self.pending_games:
			if pending_game.matches(game):
				pending_game.merge(game)
				self.loading_games.append(pending_game)
				return True
		self.loading_games.append(game)
		return True

	def sort_games(self):
		self.approved_games.sort(key=lambda game: game.date_time)
		if len(self.approved_games):
			self.approved_start_datetime = self.approved_games[0].date_time
		if len(self.loading_games):
			self.pending_games = self.loading_games
			self.loading_games = []
		self.pending_games.sort(key=lambda game: game.date_time)

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
					self.approved_games.append(pending_game)
					log.info(f"Approved game {pending_game}")
			else:
				copy_pending.append(pending_game)
		self.pending_games = copy_pending

	def delete_game(self, game_id):
		new_approved_games = []
		for approved_game in self.approved_games:
			if approved_game.id == game_id:
				log.info(f"Deleted game {approved_game}")
			else:
				new_approved_games.append(approved_game)
		self.approved_games = new_approved_games
		new_pending_games = []
		for pending_games in self.pending_games:
			if pending_games.id == game_id:
				log.info(f"Deleted game {pending_games}")
			else:
				new_pending_games.append(pending_games)
		self.pending_games = new_pending_games

	def approve_all_games(self):
		games_approved = len(self.pending_games) > 0
		self.approved_games.extend(self.pending_games)
		log.info(f"Approved {len(self.pending_games)} games for {self}")
		self.pending_games = []
		self.approved_games.sort(key=lambda game: game.date_time)
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
		if self.dirty:
			return True
		for game in self.approved_games:
			if game.dirty:
				return True
		return False

	def clean(self):
		self.dirty = False
		for game in self.approved_games:
			game.dirty = False

	def __str__(self):
		return \
			f"{self.id}: " \
			f"{(self.first_datetime.strftime('%Y-%m-%d %H:%M') if self.first_datetime else 'None')} - " \
			f"{(self.last_datetime.strftime('%Y-%m-%d %H:%M') if self.last_datetime else 'None')} | " \
			f"{len(self.approved_games)} games ({len(self.pending_games)}) | " \
			f"{('Complete' if self.is_complete() else 'Not-complete')}"


@dataclass
class Event:
	url: str
	id: str = field(default_factory=get_random_id)
	name: str = None
	streams: List[str] = field(default_factory=list)
	match_days: List[MatchDay] = field(default_factory=list)
	wiki_dirty: bool = False

	post_match_threads: bool = False
	match_thread_minutes_before: int = 15
	leave_thread_minutes_after: int = None
	use_pending_changes: bool = False

	discord_key: str = None
	discord_minutes_before: int = 15
	discord_roles: List[str] = field(default_factory=lambda: ['All-Notify', 'All-Matches', 'here'])

	details_url: str = None

	def wiki_name(self):
		return "events/"+self.name.replace(" ", "-").replace("/", "-").replace(":", "").lower()

	def get_name(self):
		return self.name

	def get_match_day(self, match_day_id):
		for match_day in self.match_days:
			if match_day.id == match_day_id:
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

	def sort_matches(self):
		for match_day in self.match_days:
			match_day.sort_games()

	def approve_all_games(self):
		for match_day in self.match_days:
			self.wiki_dirty = self.wiki_dirty or match_day.approve_all_games()

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


@dataclass
class Settings:
	stickies: List[str] = field(default_factory=list)

	# class var
	settings = None

	@classmethod
	def get_settings(cls, reddit):
		if cls.settings is None:
			cls.settings = reddit.get_settings()
		return cls.settings

	def save(self, reddit):
		reddit.save_settings(self)

	def __str__(self):
		return f"stickies: {(','.join(self.stickies) if self.stickies else 'None')}"

