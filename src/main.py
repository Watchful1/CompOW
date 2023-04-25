import time

import discord_logging
import logging.handlers
import argparse
import traceback
from datetime import datetime, timedelta

log = discord_logging.init_logging()

import flair_manager
import event_manager
import messages
import utils
from reddit_class import Reddit
from classes.settings import Settings


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

	discord_logging.init_discord_logging(args.user, logging.WARNING, 1)

	if args.run_timestamp:
		utils.DEBUG_NOW = args.run_timestamp

	reddit = Reddit(args.user, args.subreddit, args.no_post)
	# TODO cache flairs locally
	flairs = flair_manager.FlairManager()

	# overwatch_api = overwatch_api_parser.OverwatchAPI()

	timestamps = {}
	while True:
		event_dict = {}
		parse_messages = utils.past_timestamp(timestamps, "messages", use_debug=False)
		update_events = utils.past_timestamp(timestamps, "events", use_debug=False)

		if parse_messages or update_events:
			event_pages = reddit.list_event_pages()
			#log.debug(f"Loading {len(event_pages)} events")
			for event_page in event_pages:
				event = reddit.get_event_from_page(event_page)
				event_dict[event.id] = event

		try:
			if parse_messages:
				processed_message = messages.parse_messages(reddit, event_dict)
				if processed_message:
					timestamps["last_message"] = utils.utcnow()
				if "last_message" in timestamps and timestamps["last_message"] > utils.utcnow(-60*10):
					timestamps["messages"] = utils.utcnow(10)  # if we processed a message in the last 10 minutes, check every next
				else:
					timestamps["messages"] = utils.utcnow(60*2)  # otherwise check every 2 minutes
		except Exception as err:
			transient = utils.process_error(f"Error processing messages", err, traceback.format_exc())
			if not transient:
				raise

		try:
			if update_events:
				timestamps["events"] = event_manager.update_events(reddit, event_dict, flairs)
		except Exception as err:
			transient = utils.process_error(f"Error updating events", err, traceback.format_exc())
			if not transient:
				raise

		Settings.settings = None

		if parse_messages or update_events:
			for event in event_dict.values():
				if event.is_dirty():
					event.clean()
					reddit.update_page_from_event(event)

		# TODO update sidebar
		# TODO update calendar
		# TODO post in discord when there's pending matches
		# TODO create an archive page of events
		# TODO add metrics
		# TODO parse vod and auto-update post match thread
		# TODO parse maps for post match thread

		if args.once:
			break
		time.sleep(15)
