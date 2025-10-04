import discord_logging
import traceback
import requests

log = discord_logging.get_logger()

import utils
import liquipedia_parser
import string_utils
from classes.settings import Settings


def update_sidebar(reddit, all_game_pairs, flairs):
	bldr = []
	for event, game in all_game_pairs:
		if game.complete:
			continue
		bldr.append(
			f">[]({event.get_url()})\n"
			f">###{event.name}\n"
			f">###{string_utils.make_time_string(game.date_time)}\n"
			f">###{game.home.name}\n"
			f">###{game.away.name}\n"
			f">###{flairs.get_flair(game.home.name, '[](#noflair)')}\n"
			f">###{flairs.get_flair(game.away.name, '[](#noflair)')}\n"
			f"\n[](#separator)\n\n"
		)
		if len(bldr) >= 5:
			break

	reddit.update_sidebar(''.join(bldr))


def update_listings(reddit, events, flairs):
	game_pairs = []
	for event in events:
		for game in event.get_games():
			game_pairs.append((event, game))
	game_pairs.sort(key=lambda pair: pair[1].date_time)

	update_sidebar(reddit, game_pairs, flairs)

	return


def ping_pending(events):
	for event in events:
		if event.last_pinged is None or event.last_pinged < utils.utcnow(offset=-60*60*4):
			for game in event.get_games(approved=False, pending=True):
				if utils.minutes_to_start(game.date_time) < 12 * 60:
					log.warning(f"Pending {game} starts in {string_utils.make_time_string(game.date_time)} : https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}")
					event.last_pinged = utils.utcnow()
			if event.discord_key is None or event.discord_roles == utils.DEFAULT_ROLES:
				next_approved_game = event.get_next_game()
				if next_approved_game is not None and utils.minutes_to_start(next_approved_game.date_time) < 12 * 60:
					log.warning(f"Upcoming matchday missing discord key or roles and starts in {string_utils.make_time_string(next_approved_game.date_time)} : https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}")
					event.last_pinged = utils.utcnow()

