import json
import requests
import discord_logging

import static
from classes_2.flair_object import FlairObject
from classes_2.enums import DiscordType


log = discord_logging.get_logger()


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
	'Overwatch League': '<:OWC:634068549970690063>',
	'Overwatch Contenders': '<:OWL:634068184856657930>',
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
		self.missing_flairs = set()

	@staticmethod
	def strip_name(name):
		return ''.join(x for x in name.lower() if x.isalnum())

	def get_flair(self, name):
		if name == "TBD":
			return ""
		stripped_name = FlairManager.strip_name(name)
		if stripped_name in self.flairs:
			flair = self.flairs[stripped_name]
			return f"[](#{flair.sheet}-c{flair.column}-r{flair.row})"
		else:
			if stripped_name not in self.missing_flairs:
				self.missing_flairs.add(stripped_name)
				log.warning(f"Could not find flair: {stripped_name}")
			return ""

	def update_flairs(self):
		try:
			response = requests.get(url=static.FLAIR_LIST, headers={'User-Agent': static.USER_AGENT}, timeout=5)
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

	def get_static_flair(self, name, discord_type):
		if discord_type == DiscordType.COW:
			if name in static_flairs_cow:
				return static_flairs_cow[name]
		elif discord_type == DiscordType.THEOW:
			if name in static_flairs_theow:
				return static_flairs_theow[name]
		return None
