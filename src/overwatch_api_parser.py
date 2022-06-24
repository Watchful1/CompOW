import requests
import json
import discord_logging
import traceback
from datetime import datetime, timedelta


log = discord_logging.get_logger()


class OverwatchAPI:
	def __init__(self):
		self.weeks_cache = {}

	def get_match(self, match):
		log.debug(f"Getting match: {match.id} : {match.owl_id} : {match.owl_week}")
		if match.owl_id is not None and match.owl_week is not None:
			week = self.get_week(match.owl_week)
			for owl_match_id in week.matches:
				if owl_match_id == match.owl_id:
					return week.matches[owl_match_id]

		for week_num in range(1, 24):
			week = self.get_week(week_num)
			week.update_week()
			for owl_id in week.matches:
				owl_match = week.matches[owl_id]
				if match.home.name == owl_match['competitors'][0]['name'] and \
						match.away.name == owl_match['competitors'][1]['name'] and \
						match.start - timedelta(hours=2) < datetime.utcfromtimestamp(owl_match['startDate'] / 1000) < match.start + timedelta(hours=2):
					match.owl_id = owl_match['id']
					match.owl_week = week_num
					return owl_match

		return None

	def get_week(self, week_num):
		if week_num in self.weeks_cache:
			week = self.weeks_cache[week_num]
		else:
			week = ScheduleWeek(week_num)
			self.weeks_cache[week_num] = week
		week.update_week()
		return week


class ScheduleWeek:
	def __init__(self, week_num):
		self.matches = {}
		self.week_num = week_num
		self.last_updated = None

	def update_week(self, force=False):
		if not force and self.last_updated is not None and self.last_updated > datetime.utcnow() - timedelta(minutes=1):
			#log.debug(f"Skipping overwatch api query: {self.last_updated} > {datetime.utcnow() - timedelta(minutes=1)}")
			return
		#log.debug(f"Querying overwatch api: {force} : {self.last_updated} < {datetime.utcnow() - timedelta(minutes=1)}")

		headers = {
			'x-origin': 'overwatchleague.com',
		}
		params = (
			('locale', 'en-us'),
		)
		try:
			log.debug(f"Querying overwatch api for week: {self.week_num}")
			response = requests.get('https://pk0yccosw3.execute-api.us-east-2.amazonaws.com/production/v2/content-types/schedule/blt78de204ce428f00c/week/{}/team/allteams'.format(self.week_num), headers=headers, params=params)
			json_data = json.loads(response.text)
			matches = json_data['data']['tableData']['events'][0]['matches']

			self.matches = {}
			for match in matches:
				if not match['isEncore']:
					self.matches[match['id']] = match
		except Exception as err:
			log.warning(f"Failed to read overwatch api for week {self.week_num}: {err}")
			log.info(traceback.format_exc())

		self.last_updated = datetime.utcnow()
