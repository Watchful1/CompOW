import json
import requests
import discord_logging

log = discord_logging.get_logger()

import utils


static_flairs_cow = {
	'Atlanta Reign': '<:OWLAtlantaReign:590633799583268884>',
	'Boston Uprising': '<:OWLBostonUprising:775909232486645791>',
	'Chengdu Hunters': '<:OWLChengduHunters:590633797741969460>',
	'Dallas Fuel': '<:OWLDallasFuel:590633798480166922>',
	'Florida Mayhem': '<:OWLFloridaMayhem:665445079703486464>',
	'Guangzhou Charge': '<:OWLGuangzhouCharge:590633798136365084>',
	'Hangzhou Spark': '<:OWLHangzhouSpark:590633798304137237>',
	'Houston Outlaws': '<:OWLHoustonOutlaws:590633798199148565>',
	'London Spitfire': '<:OWLLondonSpitfire:590633798568247332>',
	'Los Angeles Gladiators': '<:OWLLosAngelesGladiators:590633798480298038>',
	'Los Angeles Valiant': '<:OWLLosAngelesValiant:665445127535198209>',
	'New York Excelsior': '<:OWLNewYorkExcelsior:590633798035832859>',
	'Paris Eternal': '<:OWLParisEternal:590633798354468883>',
	'Philadelphia Fusion': '<:OWLPhiladelphiaFusion:590633800094973974>',
	'San Francisco Shock': '<:OWLSanFranciscoShock:665445127619084299>',
	'Seoul Dynasty': '<:OWLSeoulDynasty:590633798601801777>',
	'Shanghai Dragons': '<:OWLShanghaiDragons:590633798035832839>',
	'Toronto Defiant': '<:OWLTorontoDefiant:590633797628985345>',
	'Vancouver Titans': '<:OWLVancouverTitans:590633798153011221>',
	'Washington Justice': '<:OWLWashingtonJustice:590633798178439195>',
	'Vegas Eternal': '<:OWLVegasEternal:1061664007754358784>',
	'Seoul Infernal': '<:OWLSeoulInfernal:1061664061751836795>',
	'Overwatch League': '<:OWC:634068549970690063>',
	'Overwatch Contenders': '<:OWL:634068184856657930>',
}


class FlairObject:
	def __init__(self, name, row, column, sheet):
		self.name = name
		self.row = row
		self.column = column
		self.sheet = sheet


class FlairManager:
	def __init__(self):
		self.flairs = {}
		self.update_flairs()
		self.missing_flairs = set()

	@staticmethod
	def strip_name(name):
		return ''.join(x for x in name.lower() if x.isalnum())

	def get_flair(self, name, default=""):
		if name is None or name == "TBD":
			return ""
		stripped_name = FlairManager.strip_name(name)
		if stripped_name in self.flairs:
			flair = self.flairs[stripped_name]
			return f"[](#{flair.sheet}-c{flair.column}-r{flair.row})"
		else:
			if stripped_name not in self.missing_flairs:
				self.missing_flairs.add(stripped_name)
				log.warning(f"Could not find flair: {stripped_name}")
			return default

	def update_flairs(self):
		log.info(f"Updating flair list from site")
		try:
			response = requests.get(url="http://rcompetitiveoverwatch.com/static/data/flairs.json", headers={'User-Agent': utils.USER_AGENT}, timeout=5)
		except Exception as err:
			log.warning(f"Flair load request failed {err}")
			return

		if response.status_code != 200:
			log.info(f"Failed to load flairs, bad status code: {response.status_code}")
			return

		try:
			json_data = json.loads(response.text)
		except Exception as err:
			log.warning(f"Failed to load flair json {err}")
			return

		flairs = {}
		for key in json_data:
			flair_json = json_data[key]
			flair = FlairObject(
				flair_json['name'],
				flair_json['row'],
				flair_json['col'],
				flair_json['sheet']
			)
			flairs[FlairManager.strip_name(flair.name)] = flair

		if len(flairs) > 20:
			self.flairs = flairs
		else:
			log.info(f"Only found {len(flairs)} flairs, not updating")

	def get_static_flair(self, name):
		if name in static_flairs_cow:
			return static_flairs_cow[name]
		return None
