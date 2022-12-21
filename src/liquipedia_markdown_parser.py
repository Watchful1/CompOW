import traceback
from lxml import etree
import requests
import discord_logging
import re
from datetime import datetime

log = discord_logging.init_logging()


class Team:
	def __init__(self):
		self.name = None
		self.score = None


class Game:
	def __init__(self):
		self.home = Team()
		self.away = Team()
		self.complete = False
		self.datetime = None

	def status(self):
		if self.complete:
			return "Complete"
		if self.home.score is not None or self.away.score is not None:
			return "In-progress"
		return "Not-started"

	def render_datetime(self):
		if self.datetime is None:
			return "None"
		return self.datetime.strftime('%Y-%m-%d %H:%M')

	def __str__(self):
		return f"{self.home.name} vs {self.away.name} : {self.home.score}-{self.away.score} : {self.status()} : {self.render_datetime()}"


def get_page_text(page_url):
	try:
		return requests.get(page_url, headers={'User-Agent': "u/watchful1 test agent"}, timeout=5).text
	except Exception:
		log.warning(f"Unable to fetch match page: {page_url}")
		log.warning(traceback.format_exc())
		return None


def get_text_from_regex(text, regex):
	match = re.search(regex, text)
	if match:
		return match.group(0)
	return None


if __name__ == "__main__":
	#page_url = "https://liquipedia.net/overwatch/Calling_All_Heroes/Challengers_Cup"
	#page_url = "https://liquipedia.net/overwatch/Overwatch_Contenders/2022/Run_It_Back/North_America"
	#page_url = "https://liquipedia.net/dota2/Dota_Pro_Circuit/2023/1/North_America/Open_Qualifier/4"
	page_url = "https://liquipedia.net/overwatch/index.php?title=Overwatch_League/Season_5/Regular_Season/Kickoff_Clash&action=edit"

	page_string = get_page_text(page_url)
	tree = etree.fromstring(page_string, etree.HTMLParser())

	text = tree.xpath("//textarea[@id='wpTextbox1']/text()")[0]

	games = []
	for node in re.findall(r"{{MatchMaps((.*\n)*?)}}", text):
		game_text = node[0]
		date_string = get_text_from_regex(game_text, r"\|date=.*}}")
		log.info(date_string)

		#games.append(game)

	for game in games:
		log.info(str(game))

