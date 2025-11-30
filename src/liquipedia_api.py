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


def parse_details_page(details_title, proxy_creds=None):
	games, event_name, streams, rev_id = parse_event(details_title, proxy_creds=proxy_creds, parse_matches=False)
	return streams


def parse_date_string(date_string, timezone_obj):
	format_strings = [
		"%Y-%m-%d - %H:%M",
		"%b %d, %Y - %H:%M",
		"%B %d, %Y - %H:%M",
	]

	parsed_datetime = None
	for format_string in format_strings:
		try:
			parsed_datetime = datetime.strptime(date_string, format_string)
			break
		except ValueError:
			continue

	if parsed_datetime is None:
		return None

	return parsed_datetime.replace(tzinfo=timezone_obj)



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
	param_value = single_template.get(1).value.strip()
	if param_value == "":
		return None
	return param_value


def parse_event(page_title, proxy_creds=None, page_content=None, parse_matches=True, print_templates=False):
	rev_id = "none"
	if page_content is None:
		base_url = "https://liquipedia.net/overwatch/api.php?action=query&prop=revisions&rvprop=content|timestamp|ids&titles={}&format=json&rvslots=main"
		api_result = call_api(base_url.format(page_title), proxy_creds)

		first_page = next(iter(api_result["query"]["pages"].values()))

		page_content = first_page["revisions"][0]["slots"]["main"]["*"]
		rev_id = str(first_page["revisions"][0]["revid"])

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
			if print_templates:
				log.debug(template)
			for param_name in stream_providers.keys():
				if not template.has(param_name):
					continue
				param = template.get(param_name)
				stream = f"{stream_providers[param_name]}{param.value.strip()}"
				streams.append(stream)
				log.debug(stream)
		elif parse_matches and template_name == "Match":
			game = Game()
			if print_templates:
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
				timezone_datetime = parse_date_string(date_str, timezone_obj)

				game.date_time = timezone_datetime.astimezone(utils.get_timezone("UTC"))
				log.debug(game.date_time)
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
			if team1_wins + team2_wins > 0:
				game.home.score = team1_wins
				game.away.score = team2_wins

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

			if game.home.name == "BYE" or game.away.name == "BYE" or game.date_time is None:
				continue

			games.append(game)

	try:
		games.sort(key=lambda game: game.date_time)
	except TypeError:
		log.warning(f"Unable to sort games due to no datetime")
		for game in games:
			log.warning(f"{game}")
		raise
	DirtyMixin.log = True

	return games, event_name, streams, rev_id


def update_event(event, username=None, approve_complete=False, proxy_creds=None):
	log.debug(f"Updating event: {event.title}")
	games, event_name, streams, rev_id = parse_event(event.title, proxy_creds=proxy_creds)
	if games is None:
		return
	if event.details_title is not None:
		details_streams = parse_details_page(event.details_title, proxy_creds=proxy_creds)
		for stream in details_streams:
			if stream not in streams:
				streams.append(stream)
	elif not len(streams):
		last_slash = event.title.rfind('/')
		if last_slash > 0:
			details_streams = parse_details_page(event.title[:last_slash], proxy_creds=proxy_creds)
			for stream in details_streams:
				if stream not in streams:
					streams.append(stream)

	if event_name != event.name:
		if event.name is None:
			event.name = event_name
			event.cached_name = event_name
		elif event.cached_name != event_name:
			event.cached_name = event_name
			message_link = string_utils.build_message_link(
				username,
				f"{event.id}:update settings",
				f"settings:name:{(event_name.replace(':', '?') if event_name else event_name)}"
			)
			log.warning(f"Event name changed from `{event.name}` to `{event_name}` : [update](<{message_link}>)")

	changed = False
	if len(event.streams) != 0:
		if len(event.streams) != len(streams):
			changed = True
		else:
			for i in range(len(streams)):
				if event.streams[i] != streams[i]:
					changed = True
	if changed:
		log.warning(f"Event {event.name} streams changed from `{'`, `'.join(event.streams)}` to `{'`, `'.join(streams)}`")
	event.streams = streams

	for game in games:
		event.add_game(game)

	event.sort_matches(approve_complete)
	event.last_revid = rev_id


def update_events(events_list, username=None, approve_complete=False, proxy_creds=None):
	titles = []
	for event in events_list:
		titles.append(event.title)

	base_url = "https://liquipedia.net/overwatch/api.php?action=query&prop=revisions&rvprop=timestamp|ids|flagged&titles={}&format=json&rvslots=main"
	api_result = call_api(base_url.format("|".join(titles)), proxy_creds)
	for api_page in api_result["query"]["pages"].values():
		api_page_title = api_page["title"].replace(" ", "_")
		api_page_latest_rev = str(api_page["revisions"][0]["revid"])

		# there will never be very many events, so this is simpler than the other options
		found_event = None
		for event in events_list:
			if event.title == api_page_title:
				found_event = event
				break
		if found_event is None:
			log.warning(f"Event title from api not found in list: {api_page_title}")
			continue

		override_event = "Finals"
		if found_event.last_revid == api_page_latest_rev and (override_event == "" or override_event not in api_page_title):
			log.debug(f"{api_page_title}: revid didnt change")
			continue

		log.info(f"{api_page_title}: {found_event.last_revid} to {api_page_latest_rev}")
		update_event(found_event, username, approve_complete, proxy_creds)



