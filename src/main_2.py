import time

import discord_logging
import logging.handlers
import praw
import jsons
import argparse
import traceback
from datetime import datetime, timedelta
from collections import defaultdict

log = discord_logging.init_logging()

import flair_manager
import event_manager
import messages
import utils
from reddit_class import Reddit, Settings
from classes import Team, Game, MatchDay, Event


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Reddit liquipedia match thread bot")
	parser.add_argument("user", help="The reddit user account to use")
	parser.add_argument("subreddit", help="The subreddit to run against")
	parser.add_argument("--once", help="Only run the loop once", action='store_const', const=True, default=False)
	parser.add_argument(
		"--no_post", help="Print out reddit actions instead of posting to reddit", action='store_const', const=True,
		default=False)
	parser.add_argument("--debug", help="Set the log level to debug", action='store_const', const=True, default=False)
	parser.add_argument("--run_timestamp", help="Set the current time to this value for debugging (23-01-01 14:36)", type=lambda s: datetime.strptime(s, '%y-%m-%d %H:%M'))
	args = parser.parse_args()

	if args.debug:
		discord_logging.set_level(logging.DEBUG)

	if args.run_timestamp:
		utils.DEBUG_NOW = args.run_timestamp

	reddit = Reddit(args.user, args.subreddit, args.no_post)
	flairs = flair_manager.FlairManager()

	# sticky = sticky_manager.StickyManager(reddit, static.SUBREDDIT, state['stickies'])
	# flairs = flair_manager.FlairManager(state['flairs'])
	# overwatch_api = overwatch_api_parser.OverwatchAPI()

	timestamps = {}
	while True:
		events = {}
		parse_messages = utils.past_timestamp(timestamps, "messages", use_debug=False)
		parse_messages = False
		update_events = utils.past_timestamp(timestamps, "events", use_debug=False)

		if parse_messages or update_events:
			event_pages = reddit.list_event_pages()
			#log.debug(f"Loading {len(event_pages)} events")
			for event_page in event_pages:
				event = reddit.get_event_from_page(event_page)
				events[event.id] = event

		# if parse_messages:
		# 	messages.parse_messages(reddit, events)

		try:
			if update_events:
				timestamps["events"] = event_manager.update_events(reddit, events, flairs)
		except Exception as err:
			transient = utils.process_error(f"Error updating events", err, traceback.format_exc())
			if not transient:
				raise

		Settings.settings = None

		# TODO update sidebar
		# TODO update calendar
		# TODO post in discord when there's pending matches
		# TODO create an archive page of events
		# TODO add metrics

		if args.once:
			break
		time.sleep(15)

