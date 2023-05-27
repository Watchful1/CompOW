import discord_logging
import traceback
import requests

log = discord_logging.get_logger()

import utils
import liquipedia_parser
import string_utils
from classes.settings import Settings


def update_sidebar(reddit, events):
	return


def ping_pending(events):
	for event in events:
		if event.last_pinged < utils.utcnow(offset=-60*60*4):
			for game in event.get_games(approved=False, pending=True):
				if utils.minutes_to_start(game.date_time) < 12 * 60:
					log.warning(f"Pending {game} starts in {string_utils.make_time_string(game.date_time)} : https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}")
					event.last_pinged = utils.utcnow()

