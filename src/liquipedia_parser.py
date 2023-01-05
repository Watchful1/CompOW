import traceback
from lxml import etree
import requests
import discord_logging
import static
from classes import Game
from datetime import datetime, timedelta

log = discord_logging.get_logger()


def get_page_text(page_url):
	try:
		return requests.get(page_url, headers={'User-Agent': static.USER_AGENT}, timeout=5).text
	except Exception:
		log.warning(f"Unable to fetch match page: {page_url}")
		log.warning(traceback.format_exc())
		return None


def get_text_from_paths(base_node, paths):
	for path in paths:
		items = base_node.xpath(path)
		if len(items):
			return items[0].strip()
	return None


def parse_event(page_url):
	page_string = get_page_text(page_url)
	tree = etree.fromstring(page_string, etree.HTMLParser())

	title_node = tree.xpath("//div[@id='main-content']/h1[@class='firstHeading']/span/text()")
	event_name = None
	if len(title_node):
		event_name = title_node[0]

	link_divs = tree.xpath("//div[@class='fo-nttax-infobox wiki-bordercolor-light']/div")
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

		game.home.score = get_text_from_paths(node,
			[".//div[contains(@class, 'brkts-popup-header-opponent-score-left')]/*/text()"])
		if game.home.score is None:
			game.home.score = get_text_from_paths(node,
				[".//div[contains(@class, 'brkts-popup-header-opponent-score-left')]/text()",
				 ".//td[@align='center'][1]/text()"])
		else:
			game.complete = True
		game.away.score = get_text_from_paths(node,
			[".//div[contains(@class, 'brkts-popup-header-opponent-score-right')]/*/text()"])
		if game.away.score is None:
			game.away.score = get_text_from_paths(node,
				[".//div[contains(@class, 'brkts-popup-header-opponent-score-right')]/text()",
				 ".//td[@align='center'][2]/text()"])
		else:
			game.complete = True
		if not game.complete:
			if get_text_from_paths(node, [".//td[@align='center'][@style='font-weight:bold;'][1]/text()"]):
				game.complete = True

		timestamp = get_text_from_paths(node,
			[".//span[@class='timer-object']/@data-timestamp"])
		if timestamp:
			game.datetime = datetime.utcfromtimestamp(int(timestamp))

		if game.home.name == "BYE" or game.away.name == "BYE":
			continue

		games.append(game)

	games.sort(key=lambda game: game.datetime)

	return games, event_name, streams

