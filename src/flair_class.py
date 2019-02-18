import json
import requests
import logging.handlers

import globals


log = logging.getLogger("bot")


class FlairObject:
	def __init__(self, name, row, column, sheet):
		self.name = name
		self.row = row
		self.column = column
		self.sheet = sheet


class FlairManager:
	def __init__(self, flairs):
		self.flairs = flairs
		self.update_flairs()

	def get_flair(self, name):
		if name in self.flairs:
			flair = self.flairs[name]
			return f"[](#{flair.sheet}-c{flair.column}-r{flair.row})"
		else:
			log.info(f"Could not find flair: {name}")
			return ""

	def update_flairs(self):
		try:
			response = requests.get(url=globals.FLAIR_LIST, headers={'User-Agent': globals.USER_AGENT})
		except Exception as err:
			log.warning("Flair load request failed")
			return

		if response.status_code != 200:
			log.info(f"Failed to load flairs, bad status code: {response.status_code}")
			return

		try:
			json_data = json.loads(response.text)
		except Exception as err:
			log.warning("Failed to load flair json")
			return

		flairs = {}
		for key in json_data['flairs']:
			flair_json = json_data['flairs'][key]
			if flair_json['active']:
				flair = FlairObject(
					flair_json['name'],
					flair_json['row'],
					flair_json['col'],
					flair_json['sheet']
				)
				flairs[flair.name] = flair

		if len(flairs) > 20:
			self.flairs = flairs
		else:
			log.info(f"Only found {len(flairs)} flairs, not updating")