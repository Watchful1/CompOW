import traceback
from lxml import etree
import bisect
import json
import discord_logging

import requests
from datetime import datetime
from datetime import timedelta

import static
from classes.stream import Stream
from classes.enums import GameState
from classes.enums import Winner
from classes.match import Match
from classes.event import Event
from classes.team import Team
from classes.map import Map
import mappings

log = discord_logging.get_logger()


def strip_string(value):
	return value.strip().replace('\n', '').replace('\t', '')


def parse_transfers(page_url):
	try:
		page_string = requests.get(page_url, headers={'User-Agent': static.USER_AGENT}, timeout=5).text
	except Exception:
		log.warning(f"Unable to fetch match page: {page_url}")
		log.warning(traceback.format_exc())
		return None

	tree = etree.fromstring(page_string, etree.HTMLParser())

	fields = {}

	paths = [
		{'field': 'date', 'required': True,
		 'path': ".//span[@class='txn-day-num']/text()"},
		{'field': 'username', 'required': True,
		 'path': ".//td[@class='txn-player']/a/div/div/div[1]/text()"},
		{'field': 'action', 'required': True,
		 'path': ".//td[@class='txn-action']/div/text()"},
		{'field': 'team', 'required': True,
		 'path': ".//td[@class='txn-team']/div/a/div/text()"},
		{'field': 'role', 'required': True,
		 'path': ".//td[@class='txn-team']/div/a/div/span/text()"},
		{'field': 'team_from', 'required': False,
		 'path': ".//td[@class='txn-team'][2]/div/a/div/text()"},
		{'field': 'role_from', 'required': False,
		 'path': ".//td[@class='txn-team'][2]/div/a/div/span/text()"},
	]

	for row in tree.xpath("//table[contains(@class, 'wf-table mod-transfers')]/tr"):
		row_fields = {}
		for path in paths:
			try:
				items = row.xpath(path['path'])
			except Exception as err:
				items = []
			for item in items:
				if item.strip() != "":
					row_fields[path['field']] = strip_string(item)
					break
			if path['field'] not in row_fields:
				if path['required']:
					log.debug(f"Could not find {path['field']}")
					return None
				continue
		log.info(f"{row_fields}")

	return fields


def parse_match(match_url, is_owl=False):
	try:
		page_string = requests.get(match_url, headers={'User-Agent': static.USER_AGENT}, timeout=5).text
	except Exception:
		log.warning(f"Unable to fetch match page: {match_url}")
		log.warning(traceback.format_exc())
		return None

	tree = etree.fromstring(page_string, etree.HTMLParser())

	fields = {}

	paths = [
		{'field': 'home', 'required': True,
		 'path': "//div[@class='match-header-link-name mod-1']/div[@class='wf-title-med']/text()"},
		{'field': 'away', 'required': True,
		 'path': "//div[@class='match-header-link-name mod-2']/div[@class='wf-title-med']/text()"},
		{'field': 'date', 'required': True,
		 'path': "//div[@class='match-header-date']/div/@data-utc-ts"},
		{'field': 'match_name', 'required': True,
		 'path': "//div[contains(@class, 'mod-match mod-bg-after')]/div[1]/div[1]/a/div/div[2]/text()"},
		{'field': 'tournament', 'required': True,
		 'path': "//div[contains(@class, 'mod-match mod-bg-after')]/div[1]/div[1]/a/div/div[1]/text()"},
		{'field': 'stream1url', 'required': False,
		 'path': "//a[contains(@class, 'match-streams-btn')][1]/@href"},
		{'field': 'stream2url', 'required': False,
		 'path': "//a[contains(@class, 'match-streams-btn')][2]/@href"},
		{'field': 'stream3url', 'required': False,
		 'path': "//a[contains(@class, 'match-streams-btn')][3]/@href"},
		{'field': 'stream1language', 'required': False,
		 'path': "//a[contains(@class, 'match-streams-btn')][1]/div/span[1]/text()"},
		{'field': 'stream2language', 'required': False,
		 'path': "//a[contains(@class, 'match-streams-btn')][2]/div/span[1]/text()"},
		{'field': 'stream3language', 'required': False,
		 'path': "//a[contains(@class, 'match-streams-btn')][3]/div/span[1]/text()"},
		{'field': 'home_score', 'required': False,
		 'path': "//div[@class='match-header-vs-score']/div/span[1]/text()"},
		{'field': 'away_score', 'required': False,
		 'path': "//div[@class='match-header-vs-score']/div/span[3]/text()"},
		{'field': 'state', 'required': False,
		 'path': "//div[@class='match-header-vs-note']/span/text()"},
		{'field': 'state2', 'required': False,
		 'path': "//div[@class='match-header-vs-note']/text()"},
		{'field': 'tournament_url', 'required': True,
		 'path': "//div[contains(@class, 'mod-match mod-bg-after')]/div[1]/div[1]/a/@href"},
		{'field': 'vod', 'required': False,
		 'path': "//div[@class='match-vods']/div[2]/a/@href"},
	]

	for path in paths:
		try:
			items = tree.xpath(path['path'])
		except Exception as err:
			items = []
		for item in items:
			if item.strip() != "":
				fields[path['field']] = strip_string(item)
				break
		if path['field'] not in fields:
			if path['required']:
				if is_owl and match_url not in static.unparsed_matches:
					static.unparsed_matches.add(match_url)
					log.warning("Unable to parse OWL match")
					log.warning(f"Could not find {path['field']}")
				else:
					log.debug(f"Could not find {path['field']}")
				return None
			continue

	fields['maps'] = []
	fields['maps_home'] = []
	fields['maps_away'] = []
	for i in range(1, 11):
		maps = tree.xpath(f"//div[contains(@class, 'game-switch-map-name')][1]/text()")
		if len(maps) < i or strip_string(maps[i - 1]) == "N/A":
			break
		fields['maps'].append(strip_string(maps[i - 1]))

		home = tree.xpath(f"//div[contains(@class, 'game ')][{i}]/div/div/div[1]/div/span/span/text()")
		fields['maps_home'].append(len(home) and home[0] != "")

		away = tree.xpath(f"//div[contains(@class, 'game ')][{i}]/div/div/div[2]/div/span/span/text()")
		fields['maps_away'].append(len(away) and away[0] != "")

	return fields


def merge_field(object, field, value):
	if getattr(object, field) != value:
		log.debug(f"Field changed \"{field}\": {getattr(object, field)} - {value}")
		object.dirty = True
		setattr(object, field, value)


def merge_fields_into_match(fields, match):
	if match.home.name != fields['home']:
		log.warning(f"Home team doesn't match: {match.home.name} to {fields['home']}")
	if match.away.name != fields['away']:
		log.warning(f"Away team doesn't match: {match.away.name} to {fields['away']}")

	merge_field(match, "stage", fields['match_name'])
	merge_field(match, "competition", fields['tournament'])
	merge_field(match, "competition_url", f"https://www.over.gg{fields['tournament_url']}")
	if 'vod' in fields:
		merge_field(match, "vod", fields['vod'])

	for stream_num in ["stream1", "stream2", "stream3"]:
		url_name = stream_num + "url"
		language_name = stream_num + "language"
		if url_name in fields:
			matched = False
			for match_stream in match.streams:
				if fields[url_name] == match_stream.url:
					matched = True

			if not matched:
				if language_name in fields:
					language = fields[language_name].strip("()")
				else:
					language = None
				bisect.insort(match.streams, Stream(fields[url_name], language))
				log.debug(f"Streams dirty: {fields[url_name]}")
				match.dirty = True

	if 'state2' in fields and fields['state2'] == "final":
		merge_field(match, "state", GameState.COMPLETE)
	elif 'state' in fields and fields['state'] == "live":
		merge_field(match, "state", GameState.IN_PROGRESS)
	else:
		merge_field(match, "state", GameState.PENDING)

	if match.state in [GameState.IN_PROGRESS, GameState.COMPLETE]:
		if 'home_score' in fields:
			merge_field(match, "home_score", int(fields['home_score']))
		else:
			merge_field(match, "home_score", 0)
		if 'away_score' in fields:
			merge_field(match, "away_score", int(fields['away_score']))
		else:
			merge_field(match, "away_score", 0)

	if match.state == GameState.COMPLETE:
		if match.home_score > match.away_score:
			merge_field(match, "winner", match.home.name)
		elif match.away_score > match.home_score:
			merge_field(match, "winner", match.away.name)
		else:
			merge_field(match, "winner", "Tied")

	for i, map_name in enumerate(fields['maps']):
		winner_home = fields['maps_home'][i]
		winner_away = fields['maps_away'][i]
		if winner_home and winner_away:
			winner = Winner.TIED
		elif winner_home:
			winner = Winner.HOME
		elif winner_away:
			winner = Winner.AWAY
		else:
			winner = Winner.NONE

		map_obj = Map(map_name, winner)
		if len(match.maps) < i + 1:
			match.maps.append(map_obj)
			match.dirty = True
		else:
			if match.maps[i] != map_obj:
				match.maps[i] = map_obj
				match.dirty = True


def populate_event(event, overwatch_api, is_owl=False):
	for match in event.matches:
		fields = parse_match(match.url, is_owl)
		if fields is None:
			log.debug(f"Fields is none in populate event: {match.url}")
			continue
		merge_fields_into_match(fields, match)
		event.merge_match(match)
		if is_owl and match.owl_complete is None:
			owl_match = overwatch_api.get_match(match)
			if owl_match['status'] == "CONCLUDED":
				match.owl_complete = datetime.utcnow()
				log.info(f"Setting OWL status to complete for {match}")


def get_upcoming_events(events):
	try:
		data = requests.get(static.OVER_GG_API, headers={'User-Agent': static.USER_AGENT}, timeout=5).json()
	except Exception as err:
		log.warning("Unable to fetch overgg api page")
		log.info(traceback.format_exc())
		return False

	for match_table in data['matches']:
		match = Match(
			id=match_table['id'],
			start=datetime.utcfromtimestamp(int(match_table['timestamp'])),
			url=match_table['match_link'],
			home=Team(match_table['teams'][0]['name'], match_table['teams'][0]['country']),
			away=Team(match_table['teams'][1]['name'], match_table['teams'][1]['country'])
		)

		fits_event = False
		for event in events:
			if event.match_fits(match.start, match_table['event_name'], match.id):
				event.add_match(match)
				fits_event = True
				break

		if not fits_event:
			rank, competition = mappings.get_competition(match_table['event_name'])
			if competition is None:
				if match_table['event_name'] not in static.missing_competition:
					static.missing_competition.add(match_table['event_name'])
					log.warning(f"Upcoming event not mapped: {match_table['event_name']} : {str(match.start)}")

			elif static.utcnow() + timedelta(hours=competition.event_build_hours_ahead) > \
					match.start > \
					static.utcnow() - timedelta(hours=10):
				log.debug(f"Found new upcoming event: {match_table['event_name']} : {str(match.start)}")

				event = Event(
					competition=competition
				)
				event.add_match(match)
				events.append(event)
