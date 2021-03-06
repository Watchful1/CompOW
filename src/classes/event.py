from datetime import timedelta
import bisect
import discord_logging

from classes.enums import GameState
import string_utils

log = discord_logging.get_logger()


class Event:
	def __init__(self, competition):
		self.competition = competition

		self.start = None
		self.last = None
		self.thread = None
		self.posted_discord = []
		self.dirty = False

		self.matches = []
		self.stage_names = []
		self.streams = []
		self.competition_url = None
		self.completion_time = None

	def add_match(self, match):
		found = False
		for event_match in self.matches:
			if event_match.id == match.id:
				if event_match.start != match.start:
					log.info(f"Updating match start in event: {match.id} : {event_match.start} : {match.start}")
					event_match.start = match.start
					self.rebuild_match_order()
					self.rebuild_start_last()
					self.dirty = True
				if event_match.url != match.url:
					log.info(f"Url updated for match: {event_match.url} : {match.url}")
					event_match.url = match.url
				if event_match.home != match.home:
					log.info(f"Home updated for match: {match.id} : {match.home}")
					event_match.home = match.home
				if event_match.away != match.away:
					log.info(f"Away updated for match: {match.id} : {match.away}")
					event_match.away = match.away
				found = True
				break
		if not found:
			log.info(f"Adding match to event {self.competition.name}: {match.id} : {match.home.name} vs {match.away.name}")
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

	def rebuild_match_order(self):
		new_matches = []
		for match in self.matches:
			bisect.insort(new_matches, match)
		if self.matches != new_matches:
			log.warning(f"Updating order for event: {self.__str__()}")
			log.warning(f"Old order: {string_utils.match_list_to_string(self.matches)}")
			log.warning(f"New order: {string_utils.match_list_to_string(new_matches)}")
			self.matches = new_matches

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
				bisect.insort(self.streams, stream)

	def match_fits(self, start, competition, match_id):
		if self.competition.name != competition:
			return False

		for event_match in self.matches:
			if event_match.id == match_id:
				if start < self.start - timedelta(hours=4) or start > self.last + timedelta(hours=4):
					log.warning(f"Match in event is now outside timebounds: {event_match}")
				return True

		return self.start - timedelta(hours=4) <= start <= self.last + timedelta(hours=4)

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

	def is_streamed(self):
		for match in self.matches:
			if len(match.streams):
				return True
		return False

	def stages_name(self):
		bldr = []
		for stage_name in self.stage_names:
			bldr.append(stage_name)

		return ' - '.join(bldr)

	def is_owl(self):
		return self.competition.name == "Overwatch League 2020 Season"

	def __str__(self):
		return f"{self.competition} : {self.start} : {len(self.matches)} matches"
