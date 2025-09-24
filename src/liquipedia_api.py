import time
import traceback
from lxml import etree
import requests
import discord_logging
import pytz
from fake_useragent import UserAgent
from datetime import datetime, timezone, timedelta
import mwparserfromhell

log = discord_logging.get_logger()

import utils
import string_utils
import counters
from classes.game import Game
from classes.settings import DirtyMixin


stream_providers = {
	"twitch": "https://www.twitch.tv/",
	"youtube": "https://www.youtube.com/",
	"bilibili": "https://space.bilibili.com/",
	"afreeca": "http://afreecatv.com/",
}


def call_api(page_url, proxy_creds=None, retries=0):
	log.debug(f"Calling api url: {page_url}")
	try:
		if proxy_creds is not None:
			proxy_url = f'http://customer-{proxy_creds["username"]}-cc-US:{proxy_creds["password"]}@pr.oxylabs.io:7777'
			proxies = {"https": proxy_url, "http": proxy_url}

			result = requests.get(page_url, headers={'User-Agent': UserAgent().chrome}, proxies=proxies, timeout=5)
		else:
			result = requests.get(page_url, headers={'User-Agent': utils.USER_AGENT}, timeout=5)
		counters.queries.labels(site="liquipedia", response=str(result.status_code)).inc()
		if not result.ok:
			log.warning(f"{result.status_code} fetching match page: {page_url}")
			return None
		else:
			return result.json()
	except requests.ReadTimeout as err:
		counters.queries.labels(site="liquipedia", response="timeout").inc()
		log.info(f"ReadTimeout fetching match page: {err} : {page_url}")
		return None
	except Exception as err:
		counters.queries.labels(site="liquipedia", response="err").inc()
		if retries < 5:
			log.info(f"{retries} fetching match page, sleeping 30 seconds: {err} : {page_url}")
			time.sleep(30)
			return call_api(page_url, proxy_creds, retries + 1)
		else:
			log.warning(f"Unable to fetch match page after {retries} retries: {err} : {page_url}")
			raise


def param_from_template_name(template, name):
	if not template.has(name):
		return None
	param = template.get(name)
	templates = param.value.filter_templates()
	if len(templates) == 0:
		return None
	single_template = templates[0]
	if len(single_template.params) == 0:
		return None
	return single_template.get(1).value.strip()


def parse_event(page_title, proxy_creds=None):
	base_url = "https://liquipedia.net/overwatch/api.php?action=query&prop=revisions&rvprop=content|timestamp|ids&titles={}&format=json&rvslots=main"
	api_result = call_api(base_url.format(page_title), proxy_creds)

	page_content = api_result["query"]["pages"][0]["revisions"][0]["slots"]["main"]["*"]

	wikicode = mwparserfromhell.parse(page_content)

	DirtyMixin.log = False
	games, event_name, streams = [], None, []
	templates = wikicode.filter_templates()
	for template in templates:
		template_name = template.name.strip()
		if template_name.startswith("DISPLAYTITLE"):
			event_name = template_name[len("DISPLAYTITLE")+1:]
			log.debug(event_name)
		elif template_name == "Infobox league":
			log.info(template)
			for param_name in stream_providers.keys():
				param = template.get(param_name)
				if param is None:
					continue
				stream = f"{stream_providers[param_name]}{param.value.strip()}"
				streams.append(stream)
				log.info(stream)
		elif template_name == "Match":
			game = Game()
			log.debug(template)
			game.home.name = param_from_template_name(template, "opponent1")
			log.debug(game.home.name)
			game.away.name = param_from_template_name(template, "opponent2")
			log.debug(game.away.name)

			date_code = template.get("date").value
			date_str = date_code.nodes[0].strip()
			if date_str:
				date_timezone = date_code.nodes[1].name
				date_timezone = date_timezone.split("/")[1]

				timezone_obj = utils.get_timezone(date_timezone)
				timezone_datetime = datetime.strptime(date_str, "%Y-%m-%d - %H:%M").replace(tzinfo=timezone_obj)

				game_datetime = timezone_datetime.astimezone(utils.get_timezone("UTC"))
				log.debug(game_datetime)
			else:
				log.debug("Game has no date")

			team1_wins, team2_wins, total_maps = 0, 0, 0
			for map_num in range(1, 15):
				if not template.has(f"map{map_num}"):
					break
				total_maps += 1
				map_code = template.get(f"map{map_num}").value
				map_template = map_code.filter_templates()[0]
				map_winner = map_template.get("winner").value.strip()
				if map_winner:
					if map_winner == "1":
						team1_wins += 1
					elif map_winner == "2":
						team2_wins += 1
					else:
						log.warning(f"something went wrong: {map_winner}")
			game.home.set_score(team1_wins)
			game.away.set_score(team2_wins)

			if team1_wins > total_maps / 2 or team2_wins > total_maps / 2:
				if team1_wins > team2_wins:
					game.complete = True
					log.debug(f"{game.home.name} wins {team1_wins} to {team2_wins}")
				elif team1_wins < team2_wins:
					game.complete = True
					log.debug(f"{game.away.name} wins {team2_wins} to {team1_wins}")
				else:
					log.debug(f"Something's wrong. Wins greater than half maps, but still tied")
			elif team1_wins + team2_wins > 0:
				log.debug(f"Game in progress")
			elif team1_wins + team2_wins == 0:
				log.debug(f"Game not started")
			else:
				log.warning(f"Something went wrong determining winner")
			games.append(game)

	try:
		games.sort(key=lambda game: game.date_time)
	except TypeError:
		log.warning(f"Unable to sort games due to no datetime")
		for game in games:
			log.warning(f"{game}")
		raise
	DirtyMixin.log = True

	return games, event_name, streams


def update_event(event, username=None, approve_complete=False, proxy_creds=None):
	parse_event(event.title, proxy_creds)


def update_events(events_list, proxy_creds=None):
	titles = []
	for event in events_list:
		titles.append(event.title)

	base_url = "https://liquipedia.net/overwatch/api.php?action=query&prop=revisions&rvprop=timestamp|ids|flagged&titles={}&format=json&rvslots=main"
	api_result = call_api(base_url.format("|".join(titles)), proxy_creds)
	for api_page in api_result.json()["query"]["pages"].values():
		api_page_title = api_page["title"]
		api_page_latest_rev = api_page["revisions"][0]["revid"]

		# there will never be very many events, so this is simpler than the other options
		found_event = None
		for event in events_list:
			if event.title == api_page_title:
				found_event = event
				break
		if found_event is None:
			log.warning(f"Event title from api not found in list: {api_page_title}")
			continue

		if found_event.last_revid == api_page_latest_rev:
			log.info(f"{api_page_title}: revid didnt change")
			continue

		log.info(f"{api_page_title}: {found_event.last_revid} to {api_page_latest_rev}")



