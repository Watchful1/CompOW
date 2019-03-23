import logging.handlers
import traceback
from lxml import etree
import bisect

import requests
from datetime import datetime
from datetime import timedelta

import globals
from classes.stream import Stream
from classes.enums import GameState
from classes.match import Match
from classes.event import Event
from classes.team import Team
import mappings


log = logging.getLogger("bot")


def parse_match(match_url):
	try:
		page_string = requests.get(match_url).text
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
		 	'path': "//a[@class='match-info-section-event']/../text()"},
		{'field': 'tournament', 'required': True,
		 	'path': "//a[@class='match-info-section-event']/text()"},
		{'field': 'stream1url', 'required': True,
		 	'path': "//a[@class='wf-card mod-dark'][1]/@href"},
		{'field': 'stream2url', 'required': False,
		 	'path': "//a[@class='wf-card mod-dark'][2]/@href"},
		{'field': 'stream3url', 'required': False,
		 	'path': "//a[@class='wf-card mod-dark'][3]/@href"},
		{'field': 'stream1language', 'required': True,
		 	'path': "//a[@class='wf-card mod-dark'][1]/div/span[1]/text()"},
		{'field': 'stream2language', 'required': False,
		 	'path': "//a[@class='wf-card mod-dark'][2]/div/span[1]/text()"},
		{'field': 'stream3language', 'required': False,
		 	'path': "//a[@class='wf-card mod-dark'][3]/div/span[1]/text()"},
		{'field': 'home_score', 'required': False,
		 	'path': "//div[@class='match-header-vs-score']/div/span[1]/text()"},
		{'field': 'away_score', 'required': False,
		 	'path': "//div[@class='match-header-vs-score']/div/span[3]/text()"},
		{'field': 'state', 'required': False,
		 	'path': "//div[@class='match-header-vs-note']/span/text()"},
		{'field': 'state2', 'required': False,
		 	'path': "//div[@class='match-header-vs-note']/text()"},
		{'field': 'tournament_url', 'required': True,
		 	'path': "//a[@class='match-info-section-event']/@href"},
	]

	for path in paths:
		try:
			items = tree.xpath(path['path'])
		except Exception as err:
			items = []
		for item in items:
			if item.strip() != "":
				fields[path['field']] = item.strip().replace('\n', '').replace('\t', '')
				break
		if path['field'] not in fields:
			if path['required']:
				log.debug(f"Could not find {path['field']}")
			continue

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

	for stream_num in ["stream1", "stream2", "stream3"]:
		url_name = stream_num+"url"
		language_name = stream_num+"language"
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


def populate_event(event):
	for match in event.matches:
		fields = parse_match(match.url)
		if fields is None:
			log.warning("Fields is none in populate event")
			continue
		merge_fields_into_match(fields, match)
		event.merge_match(match)


def get_upcoming_events(events):
	try:
		data = requests.get(globals.OVER_GG_API).json()
	except Exception as err:
		log.warning("Unable to fetch overgg api page")
		log.warning(traceback.format_exc())
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

		if not fits_event and datetime.utcnow() + timedelta(hours=10) > match.start:
			rank, competition = mappings.get_competition(match_table['event_name'])
			if competition is None:
				pass # placeholder
				#log.debug(f"Upcoming event not mapped: {match_table['event_name']} : {str(match.start)}")
			else:
				log.debug(f"Found new upcoming event: {match_table['event_name']} : {str(match.start)}")

				event = Event(
					competition=competition
				)
				event.add_match(match)
				events.append(event)
