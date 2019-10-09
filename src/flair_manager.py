import json
import requests
import discord_logging

import globals
from classes.flair_object import FlairObject


log = discord_logging.get_logger()


static_flairs = {
	'Atlanta Reign': ':ATL:',
	'Boston Uprising': ':BOS:',
	'Chengdu Hunters': ':CDH:',
	'Dallas Fuel': ':DAL:',
	'Florida Mayhem': ':FLA:',
	'Guangzhou Charge': ':GZC:',
	'Hangzhou Spark': ':HZS:',
	'Houston Outlaws': ':HOU:',
	'London Spitfire': ':LDN:',
	'Los Angeles Gladiators': ':GLA:',
	'Los Angeles Valiant': ':VAL:',
	'New York Excelsior': ':NYE:',
	'Paris Eternal': ':PAR:',
	'Philadelphia Fusion': ':PHI:',
	'San Francisco Shock': ':SFS:',
	'Seoul Dynasty': ':SEO:',
	'Shanghai Dragons': ':SHD:',
	'Toronto Defiant': ':TOR:',
	'Vancouver Titans': ':VAN:',
	'Washington Justice': ':WAS:',
	'Overwatch League': ':OWL:',
	'Overwatch Contenders': ':OWC:',
}


class FlairManager:
	def __init__(self, flairs):
		self.flairs = flairs
		self.update_flairs()

	def get_flair(self, name):
		if name == "TBD":
			return ""
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

	def get_static_flair(self, name):
		if name in static_flairs:
			return static_flairs[name]
		else:
			return None
