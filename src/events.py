import discord_logging

log = discord_logging.get_logger()

import utils
import liquipedia_parser
from classes import Event


def update_events(reddit, events):
	for event in events:
		liquipedia_parser.update_event(event)
		reddit.update_page_from_event(event)


	# populate event
	# post match thread if close to start time
	# post post-match thread if event is complete
	# update match thread if there are changes
	# remove match thread if event complete and longer than set time
	# post predictions thread day before event week starts
	# remove prediction thread before posting event
	# post discord announcements
