import traceback
from lxml import etree
import requests
import discord_logging
import pytz
from datetime import datetime, timedelta

log = discord_logging.get_logger()

import utils
import string_utils
import counters
from classes.game import Game
from classes.settings import DirtyMixin


def get_page_text(page_url):
	try:
		result = requests.get(page_url, headers={'User-Agent': utils.USER_AGENT}, timeout=5)
		counters.queries.labels(site="liquipedia", response=str(result.status_code)).inc()
		return result.text
	except requests.ReadTimeout as err:
		counters.queries.labels(site="liquipedia", response="timeout").inc()
		log.info(f"ReadTimeout fetching match page: {err} : {page_url}")
		return None
	except Exception as err:
		counters.queries.labels(site="liquipedia", response="err").inc()
		log.warning(f"Unable to fetch match page: {err} : {page_url}")
		raise


def get_text_from_paths(base_node, paths):
	for path in paths:
		items = base_node.xpath(path)
		if len(items):
			result = items[0].strip().encode('ascii', 'ignore').decode("utf-8")
			if result:
				return result
	return None


def extract_details(tree):
	link_divs = tree.xpath("//div[@class='fo-nttax-infobox']/div")
	# if len(link_divs) == 0:
	# 	link_divs = tree.xpath("//div[@class='fo-nttax-infobox wiki-bordercolor-light']/div")

	found_links = False
	streams = []
	for div in link_divs:
		if found_links:
			hrefs = div.xpath(".//a[@class='external text']/@href")
			for href in hrefs:
				if "youtube.com" in href or "twitch.tv" in href:
					streams.append(href)
			break

		else:
			texts = div.xpath(".//div[contains(@class, 'infobox-header')]/text()")
			if len(texts):
				text = texts[0]
				if text.lower() == "links":
					found_links = True

	return streams


def parse_details_page(page_url):
	page_string = get_page_text(page_url)
	if page_string is None:
		return []
	tree = etree.fromstring(page_string, etree.HTMLParser())

	streams = extract_details(tree)

	return streams


def parse_event(page_url):
	# TODO parse out the match day and bracket levels
	page_string = get_page_text(page_url)
	if page_string is None:
		return None, None, None
	tree = etree.fromstring(page_string, etree.HTMLParser())

	title_node = tree.xpath("//div[@id='main-content']/h1[@class='firstHeading']/span/text()")
	event_name = None
	if len(title_node):
		event_name = str(title_node[0])

	streams = extract_details(tree)

	DirtyMixin.log = False
	games = []

	game_nodes = tree.xpath("//div[@class='brkts-popup brkts-match-info-popup']")
	if not len(game_nodes):
		game_nodes = tree.xpath("//tr[@class='match-row']")
	for node in game_nodes:
		game = Game()
		game.home.name = get_text_from_paths(node,
			[".//div[contains(@class, 'brkts-popup-header-opponent-left')]/*/*/*/a/@title",
			 ".//div[contains(@class, 'bracket-popup-header-left')]/*/*/a/@title",
			 ".//div[contains(@class, 'brkts-popup-header-opponent-left')]/div[@class='brkts-opponent-block-literal']/text()"])
		game.away.name = get_text_from_paths(node,
			[".//div[contains(@class, 'brkts-popup-header-opponent-right')]/*/*/*/a/@title",
			 ".//div[contains(@class, 'bracket-popup-header-right')]/*/*/a/@title",
			 ".//div[contains(@class, 'brkts-popup-header-opponent-right')]/div[@class='brkts-opponent-block-literal']/text()"])

		game.home.set_score(get_text_from_paths(node,
			[".//div[contains(@class, 'brkts-popup-header-opponent-score-left')]/*/text()"]))
		if game.home.score is None:
			game.home.set_score(get_text_from_paths(node,
				[".//div[contains(@class, 'brkts-popup-header-opponent-score-left')]/text()",
				 ".//td[@align='center'][1]/text()"]))
		else:
			game.complete = True
		game.away.set_score(get_text_from_paths(node,
			[".//div[contains(@class, 'brkts-popup-header-opponent-score-right')]/*/text()"]))
		if game.away.score is None:
			game.away.set_score(get_text_from_paths(node,
				[".//div[contains(@class, 'brkts-popup-header-opponent-score-right')]/text()",
				 ".//td[@align='center'][2]/text()"]))
		else:
			game.complete = True
		if not game.complete:
			if get_text_from_paths(node, [".//td[@align='center'][@style='font-weight:bold;'][1]/text()"]):
				game.complete = True

		timestamp = get_text_from_paths(node,
			[".//span[@class='timer-object']/@data-timestamp"])
		if timestamp:
			try:
				game.date_time = datetime.utcfromtimestamp(int(timestamp)).replace(tzinfo=pytz.utc)
			except ValueError:
				log.info(f"Invalid timestamp: {timestamp}")

		if game.home.name == "BYE" or game.away.name == "BYE":
			continue

		games.append(game)

	games.sort(key=lambda game: game.date_time)
	DirtyMixin.log = True

	return games, event_name, streams


def update_event(event, username=None, approve_complete=False):
	url = event.url
	if event.use_pending_changes:
		url = url + "?stable=0"
	log.debug(f"Pulling page from liquipedia: {url}")
	games, event_name, streams = parse_event(url)
	if games is None:
		return
	if event.details_url is not None:
		details_streams = parse_details_page(event.details_url)
		for stream in details_streams:
			if stream not in streams:
				streams.append(stream)
	elif not len(streams):
		last_slash = event.url.rfind('/')
		if last_slash > 0:
			details_streams = parse_details_page(event.url[:last_slash])
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
	event.last_parsed = utils.utcnow()
