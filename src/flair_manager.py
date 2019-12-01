import json
import requests
import discord_logging

import globals
from classes.flair_object import FlairObject
from classes.enums import DiscordType


log = discord_logging.get_logger()


static_flairs_cow = {
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


static_flairs_theow = {
	'Atlanta Reign': '<:AtlantaReign:522397819747958786>',
	'Boston Uprising': '<:BostonUprising:464517062170116097>',
	'Chengdu Hunters': '<:ChengduHunters:522397670128746498>',
	'Dallas Fuel': '<:DallasFuel:464517062350340106>',
	'Florida Mayhem': '<:FloridaMayhem:464517063768145941>',
	'Guangzhou Charge': '<:GuangzhouCharge:522397679343370261>',
	'Hangzhou Spark': '<:HangzhouSpark:545919246673117204>',
	'Houston Outlaws': '<:HoustonOutlaws:464517064187707395>',
	'London Spitfire': '<:LondonSpitfire:464517066733387806>',
	'Los Angeles Gladiators': '<:LosAngelesGladiators:464517074396381198>',
	'Los Angeles Valiant': '<:LosAngelesValiant:464517071787655198>',
	'New York Excelsior': '<:NewYorkExcelsior:464517068608503858>',
	'Paris Eternal': '<:ParisEternal:522397696103940124>',
	'Philadelphia Fusion': '<:PhiladelphiaFusion:464517073771560979>',
	'San Francisco Shock': '<:SanFranciscoShock:464517069791166464>',
	'Seoul Dynasty': '<:SeoulDynasty:464517074245648404>',
	'Shanghai Dragons': '<:ShanghaiDragons:464517072903471115>',
	'Toronto Defiant': '<:TorontoDefiant:522397789594976257>',
	'Vancouver Titans': '<:VancouverTitans:522397797907955714>',
	'Washington Justice': '<:WashingtonJustice:522397807617769472>',
	'Overwatch League': '<:OWL:376550786622291968>',
	'Overwatch Contenders': '<:Contenders:408733969102798848>',
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

	def get_static_flair(self, name, discord_type):
		if discord_type == DiscordType.COW:
			if name in static_flairs_cow:
				return static_flairs_cow[name]
		elif discord_type == DiscordType.THEOW:
			if name in static_flairs_theow:
				return static_flairs_theow[name]
		return None
