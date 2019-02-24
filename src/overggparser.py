import urllib.request
import logging.handlers
import traceback
from lxml import etree

import requests
from datetime import datetime
from datetime import timedelta

import globals
import classes
import mappings


log = logging.getLogger("bot")


def parse_match(match_url):
	response = urllib.request.urlopen(match_url)
	tree = etree.parse(response, etree.HTMLParser())

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
		{'field': 'stream1', 'required': True,
		 	'path': "//div[@class='match-streams']/div/a/@href"},
		{'field': 'stream2', 'required': False,
		 	'path': "//div[@class='match-streams']/div[3]/a/@href"},
		{'field': 'stream3', 'required': False,
		 	'path': "//div[@class='match-streams']/div[4]/a/@href"},
		{'field': 'stream_name1', 'required': True,
		 	'path': "//div[@class='match-streams']/div/a/text()"},
		{'field': 'stream_name2', 'required': False,
		 	'path': "//div[@class='match-streams']/div[3]/a/text()"},
		{'field': 'stream_name3', 'required': False,
		 	'path': "//div[@class='match-streams']/div[4]/a/text()"},
		{'field': 'home_score', 'required': False,
		 	'path': "//div[@class='match-header-vs-score']/div/span[1]/text()"},
		{'field': 'away_score', 'required': False,
		 	'path': "//div[@class='match-header-vs-score']/div/span[3]/text()"},
		{'field': 'state', 'required': False,
		 	'path': "//div[@class='match-header-vs-note']/span/text()"},
		{'field': 'state2', 'required': False,
		 	'path': "//div[@class='match-header-vs-note']/text()"},
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

	for stream_num in ["1", "2", "3"]:
		url_name = "stream"+stream_num
		if url_name in fields:
			matched = False
			for match_stream in match.streams:
				if fields[url_name] == match_stream.url:
					matched = True

			if not matched:
				match.streams.append(classes.Stream(fields[url_name], fields["stream_name"+stream_num]))
				log.debug(f"Streams dirty: {fields[url_name]}")
				match.dirty = True

	if 'state2' in fields and fields['state2'] == "final":
		merge_field(match, "state", classes.GameState.COMPLETE)
	elif 'state' in fields and fields['state'] == "live":
		merge_field(match, "state", classes.GameState.IN_PROGRESS)
	else:
		merge_field(match, "state", classes.GameState.PENDING)

	if match.state in [classes.GameState.IN_PROGRESS, classes.GameState.COMPLETE]:
		if 'home_score' in fields:
			merge_field(match, "home_score", int(fields['home_score']))
		else:
			merge_field(match, "home_score", 0)
		if 'away_score' in fields:
			merge_field(match, "away_score", int(fields['away_score']))
		else:
			merge_field(match, "away_score", 0)

	if match.state == classes.GameState.COMPLETE:
		if match.home_score > match.away_score:
			merge_field(match, "winner", match.home.name)
		elif match.away_score > match.home_score:
			merge_field(match, "winner", match.away.name)
		else:
			merge_field(match, "winner", "Tied")


def populate_event(event):
	for match in event.matches:
		fields = parse_match(match.url)
		merge_fields_into_match(fields, match)
		event.merge_match(match)


def get_upcoming_events(events):
	try:
		data = requests.get(globals.OVER_GG_API).json()
	except Exception as err:
		log.warning(traceback.format_exc())
		return False

	for match_table in data['matches']:
		match = classes.Match(
			id=match_table['id'],
			start=datetime.utcfromtimestamp(int(match_table['timestamp'])),
			url=match_table['match_link'],
			home=classes.Team(match_table['teams'][0]['name'], match_table['teams'][0]['country']),
			away=classes.Team(match_table['teams'][1]['name'], match_table['teams'][1]['country'])
		)

		fits_event = False
		for event in events:
			if event.match_fits(match.start, match_table['event_name']):
				event.add_match(match)
				fits_event = True
				break

		if not fits_event and datetime.utcnow() + timedelta(hours=1) > match.start:
			rank, competition = mappings.get_competition(match_table['event_name'])
			if competition is None:
				pass # placeholder
				#log.debug(f"Upcoming event not mapped: {match_table['event_name']} : {str(match.start)}")
			else:
				log.debug(f"Found new upcoming event: {match_table['event_name']} : {str(match.start)}")

				event = classes.Event(
					competition=competition
				)
				event.add_match(match)
				events.append(event)
