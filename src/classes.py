from enum import Enum
from datetime import timedelta
import logging
from urllib.parse import urlparse

log = logging.getLogger("bot")


class GameState(Enum):
	PENDING = 1
	IN_PROGRESS = 2
	COMPLETE = 3
	UNKNOWN = 4


class Competition:
	def __init__(
			self,
			name,
			discord_minutes_ahead=None,
			discord_roles=[],
			discord_channel="348939546878017536",
			post_match_threads=False,
			post_minutes_ahead=15,
			day_in_title=False,
			prediction_thread_minutes_ahead=None
			):
		self.name = name
		if discord_minutes_ahead is not None and discord_minutes_ahead > post_minutes_ahead:
			self.discord_minutes_ahead = post_minutes_ahead
		else:
			self.discord_minutes_ahead = discord_minutes_ahead
		self.discord_roles = discord_roles
		self.discord_channel = discord_channel
		self.post_match_threads = post_match_threads
		self.post_minutes_ahead = post_minutes_ahead
		self.day_in_title = day_in_title
		self.prediction_thread_minutes_ahead = prediction_thread_minutes_ahead

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
		self.competition_url = None
		self.stage = None

		self.post_thread = None

		self.dirty = False

	def __str__(self):
		return f"{self.home.name} vs {self.away.name} : {self.start}"

	def __lt__(self, other):
		return self.start < other.start

	def __eq__(self, other):
		return self.id == other.id


class Event:
	def __init__(self, competition):
		self.competition = competition

		self.start = None
		self.last = None
		self.thread = None
		self.posted_discord = False
		self.dirty = False
		self.prediction_thread = None

		self.matches = []
		self.stage_names = []
		self.streams = []
		self.competition_url = None

	def add_match(self, match):
		found = False
		for event_match in self.matches:
			if event_match.id == match.id:
				if event_match.start != match.start:
					log.info(f"Updating match start in event: {match.id} : {event_match.start} : {match.start}")
					event_match.start = match.start
					self.rebuild_start_last()
				if event_match.url != match.url:
					log.warning(f"Url updated for match: {event_match.url} : {match.url}")
					event_match.url = match.url
				if event_match.home != match.home:
					log.warning(f"Home updated for match: {match.id} : {match.home}")
				if event_match.away != match.away:
					log.warning(f"Away updated for match: {match.id} : {match.away}")
				found = True
				break
		if not found:
			log.info(f"Adding match to event: {match.id} : {match.home.name} vs {match.away.name}")
			self.matches.append(match)
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

	def merge_match(self, match):
		if match.stage not in self.stage_names:
			self.stage_names.append(match.stage)
		if self.competition_url is None:
			self.competition_url = match.competition_url
		elif self.competition_url != match.competition_url:
			log.warning(f"Match competition url doesn't match event: {self.competition_url} : {match.competition_url}")
		if match.dirty:
			self.dirty = True
		for stream in match.streams:
			if stream not in self.streams:
				self.streams.append(stream)

	def match_fits(self, start, competition):
		if self.competition.name != competition:
			return False
		return self.start - timedelta(hours=3) < start < self.last + timedelta(hours=3)

	def clean(self):
		self.dirty = False
		for match in self.matches:
			match.dirty = False

	def game_state(self):
		all_complete = True
		for match in self.matches:
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
