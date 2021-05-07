import requests
import json
import discord_logging
from datetime import datetime, timedelta


log = discord_logging.get_logger()


class OverwatchAPI:
	def __init__(self):
		self.weeks_cache = {}
		self.matches_weeks = {}

	def get_match(self, match):
		if match.owl_id is not None and match.owl_id in self.matches_weeks:
			week_num = self.matches_weeks[match.owl_id]
			week = self.get_week(week_num)
			for owl_match in week:
				if owl_match['id'] == match.owl_id:
					return owl_match

		for week_num in range(1, 20):
			week = ScheduleWeek(week_num)
			week.update_week()
			for owl_id in week.matches:
				owl_match = week.matches[owl_id]
				if match.home.name == owl_match['competitors'][0]['name'] and \
						match.away.name == owl_match['competitors'][1]['name'] and \
						match.start - timedelta(hours=2) < datetime.utcfromtimestamp(owl_match['startDate'] / 1000) < match.start + timedelta(hours=2):
					match.owl_id = owl_match['id']
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

	def update_week(self):
		if self.last_updated is not None and self.last_updated > datetime.utcnow() - timedelta(minutes=1):
			return

		headers = {
			'authority': 'wzavfvwgfk.execute-api.us-east-2.amazonaws.com',
			'origin': 'https://overwatchleague.com',
			'x-origin': 'overwatchleague.com',
			'accept': '*/*',
			'sec-fetch-site': 'cross-site',
			'sec-fetch-mode': 'cors',
			'referer': 'https://overwatchleague.com/en-us/schedule?stage=regular_season&week={}'.format(self.week_num),
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'en-US,en;q=0.9',
		}
		params = (
			('stage', 'regular_season'),
			('page', '{}'.format(self.week_num)),
			('season', '2021'),
			('locale', 'en-us'),
		)
		response = requests.get('https://wzavfvwgfk.execute-api.us-east-2.amazonaws.com/production/owl/paginator/schedule', headers=headers, params=params)
		json_data = json.loads(response.text)
		matches = json_data['content']['tableData']['events'][0]['matches']

		self.matches = {}
		for match in matches:
			self.matches[match['id']] = match

		self.last_updated = datetime.utcnow()
