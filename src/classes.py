from enum import Enum
from datetime import timedelta
import logging
import bisect
from urllib.parse import urlparse


log = logging.getLogger("bot")


class GameState(Enum):
	PENDING = 1
	IN_PROGRESS = 2
	COMPLETE = 3
	UNKNOWN = 4


class Competition:
	def __init__(self, name, post_discord=False, discord_role=None, post_match_threads=False):
		self.name = name
		self.post_discord = post_discord
		self.discord_role = discord_role
		self.post_match_threads = post_match_threads

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name


def extract_url_name(url):
	try:
		parsed_url = urlparse(url)
	except Exception as err:
		return url

	if "twitch.tv" in parsed_url.netloc.lower():
		last_slash = url.rfind("/", 0, len(url) - 1)
		if url[-1] == '/':
			return url[last_slash + 1:-1]
		else:
			return url[last_slash + 1:]
	else:
		return parsed_url.netloc


class Stream:
	def __init__(self, url, name=None):
		self.url = url
		if name is None:
			self.name = extract_url_name(url)
		else:
			self.name = name

	def __eq__(self, other):
		return self.url == other.url


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
		self.post_thread = None

		self.dirty = False

	def __str__(self):
		return f"{self.home.name} vs {self.away.name} : {self.start}"

	def __lt__(self, other):
		return self.start < other.start

	def __eq__(self, other):
		return self.id == other.id


class StageBak:
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
		self.competition = competition

		self.start = None
		self.last = None
		self.thread = None
		self.dirty = False

		self.matches_new = []
		self.stage_names = []
		self.streams = []

	def add_match(self, match):
		found = False
		for event_match in self.matches_new:
			if event_match.id == match.id:
				if event_match.start != match.start:
					log.info(f"Updating match start in event: {match.id} : {event_match.start} : {match.start}")
					event_match.start = match.start
					self.rebuild_start_last()
				if event_match.url != match.url:
					log.warning(f"Url updated for match: {match.id}")
				if event_match.home != match.home:
					log.warning(f"Home updated for match: {match.id} : {match.home}")
				if event_match.away != match.away:
					log.warning(f"Away updated for match: {match.id} : {match.away}")
				found = True
				break
		if not found:
			log.info(f"Adding match to event: {match.id} : {match.home.name} vs {match.away.name}")
			self.matches_new.append(match)
			self.add_match_time(match.start)

	def add_match_time(self, match_time):
		if self.start is None or self.start > match_time:
			self.start = match_time
		if self.last is None or self.last < match_time:
			self.last = match_time

	def rebuild_start_last(self):
		self.start = None
		self.last = None
		for match in self.matches_new:
			self.add_match_time(match.start)

	def match_fits(self, start, competition):
		if self.competition.name != competition:
			return False
		return self.start - timedelta(hours=3) < start < self.last + timedelta(hours=3)

	def clean(self):
		self.dirty = False
		for match in self.matches_new:
			match.dirty = False

	def add_stage_name(self, stage_name):
		if stage_name not in self.stage_names:
			self.stage_names.append(stage_name)

	def game_state(self):
		all_complete = True
		for match in self.matches_new:
			if match.state == GameState.IN_PROGRESS:
				return GameState.IN_PROGRESS
			if match.state != GameState.COMPLETE:
				all_complete = False

		if all_complete:
			return GameState.COMPLETE
		else:
			return GameState.PENDING

	def stages_name(self):
		bldr = []
		for stage_name in self.stage_names:
			bldr.append(stage_name)

		return ' - '.join(bldr)

	def __str__(self):
		return f"{self.competition} : {self.start}"
