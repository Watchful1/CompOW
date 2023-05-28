import time
import discord_logging
import logging.handlers
import argparse
import traceback
from datetime import datetime, timedelta

log = discord_logging.init_logging(add_trace=True)

import flair_manager
import event_manager
import listings
import messages
import utils
from reddit_class import Reddit
import counters

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Reddit liquipedia match thread bot")
	parser.add_argument("user", help="The reddit user account to use")
	parser.add_argument("subreddit", help="The subreddit to run against")
	parser.add_argument("--once", help="Only run the loop once", action='store_const', const=True, default=False)
	parser.add_argument(
		"--no_post", help="Print out reddit actions instead of posting to reddit", action='store_const', const=True,
		default=False)
	parser.add_argument('--verbose', '-v', help="Increase the log level", action='count', default=0)
	parser.add_argument("--debug", help="Set the log level to debug", action='store_const', const=True, default=False)
	parser.add_argument("--run_timestamp", help="Set the current time to this value for debugging (23-01-01 14:36)", type=lambda s: datetime.strptime(s, '%y-%m-%d %H:%M'))
	args = parser.parse_args()

	if args.verbose == 1:
		discord_logging.set_level(logging.DEBUG)
	elif args.verbose == 2:
		discord_logging.set_level(logging.TRACE)

	discord_logging.init_discord_logging(args.user, logging.WARNING, 1)
	counters.init(8006)

	if args.run_timestamp:
		utils.DEBUG_NOW = args.run_timestamp

	reddit = Reddit(args.user, args.subreddit, args.no_post)
	# TODO cache flairs locally
	flairs = flair_manager.FlairManager()

	timestamps = {}
	first_loop = True
	while True:
		event_dict = {}
		parse_messages = utils.past_timestamp(timestamps, "messages", use_debug=False)
		update_events = utils.past_timestamp(timestamps, "events", use_debug=False)
		update_listings = utils.past_timestamp(timestamps, "listings", use_debug=False)

		transient_error = False

		try:
			if parse_messages or update_events or update_listings:
				reasons = []
				if parse_messages:
					reasons.append("parse_messages")
				if update_events:
					reasons.append("update_events")
				if update_listings:
					reasons.append("update_listings")
				log.debug(','.join(reasons))
				event_pages = reddit.list_event_pages()
				counters.events.set(len(event_pages))
				for event_page in event_pages:
					event = reddit.get_event_from_page(event_page)
					event_dict[event.id] = event
		except Exception as err:
			transient_error = utils.process_error(f"Error loading pages", err, traceback.format_exc())
			if not transient_error:
				raise
			time.sleep(30)
			continue

		try:
			if parse_messages and not transient_error:
				counters.process.labels(type="messages").inc()
				processed_message = messages.parse_messages(reddit, event_dict)
				if processed_message or first_loop:
					timestamps["last_message"] = utils.utcnow()
				if "last_message" in timestamps and timestamps["last_message"] > utils.utcnow(-60*10):
					timestamps["messages"] = utils.utcnow(10)  # if we processed a message in the last 10 minutes, check every next
				else:
					timestamps["messages"] = utils.utcnow(60*2)  # otherwise check every 2 minutes
		except Exception as err:
			transient_error = utils.process_error(f"Error processing messages", err, traceback.format_exc())
			if not transient_error:
				raise

		try:
			if update_events and not transient_error:
				counters.process.labels(type="events").inc()
				timestamps["events"] = event_manager.update_events(reddit, event_dict, flairs, first_loop)
		except Exception as err:
			transient_error = utils.process_error(f"Error updating events", err, traceback.format_exc())
			if not transient_error:
				raise

		try:
			if update_listings and not transient_error:
				counters.process.labels(type="listing").inc()
				log.debug("Updating listing pages")
				listings.ping_pending(event_dict.values())

				settings = reddit.get_settings()
				reddit.save_settings(settings, event_dict.values())
				reddit.settings = None

				timestamps["listings"] = utils.utcnow(offset=60*15)  # update the listings automatically every 15 minutes
		except Exception as err:
			transient_error = utils.process_error(f"Error updating listings", err, traceback.format_exc())
			if not transient_error:
				raise

		try:
			if not transient_error:
				if reddit.settings is not None:
					reddit.save_settings(reddit.settings, event_dict.values())
					reddit.settings = None

				if parse_messages or update_events:
					for event in event_dict.values():
						if event.is_dirty():
							log.debug(f"Updating event page {event.id}")
							reddit.update_page_from_event(event)
		except Exception as err:
			transient_error = utils.process_error(f"Error saving settings/events", err, traceback.format_exc())
			if not transient_error:
				raise

		# TODO update sidebar
		# TODO update calendar
		# TODO parse vod and auto-update post match thread
		# TODO parse maps for post match thread

		discord_logging.flush_discord()

		if args.once:
			break
		first_loop = False

		if transient_error:
			time.sleep(180)
		else:
			time.sleep(15)
