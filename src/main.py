#!/usr/bin/python3

import logging.handlers
import os
import sys
import time
import requests
import traceback
from datetime import datetime
from datetime import timedelta

import globals
import overggparser
import string_utils
import classes
import sticky_class
import reddit_class
import file_utils
import flair_class

LOG_LEVEL = logging.DEBUG

LOG_FOLDER_NAME = "logs"
if not os.path.exists(LOG_FOLDER_NAME):
	os.makedirs(LOG_FOLDER_NAME)
LOG_FILENAME = LOG_FOLDER_NAME + "/" + "bot.log"
LOG_FILE_BACKUPCOUNT = 5
LOG_FILE_MAXSIZE = 1024 * 1024 * 16

log = logging.getLogger("bot")
log.setLevel(LOG_LEVEL)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
log_stderrHandler = logging.StreamHandler()
log_stderrHandler.setFormatter(log_formatter)
log.addHandler(log_stderrHandler)
if LOG_FILENAME is not None:
	log_fileHandler = logging.handlers.RotatingFileHandler(
		LOG_FILENAME,
		maxBytes=LOG_FILE_MAXSIZE,
		backupCount=LOG_FILE_BACKUPCOUNT
	)
	log_fileHandler.setFormatter(log_formatter)
	log.addHandler(log_fileHandler)


def minutes_to_start(start):
	return (start - datetime.utcnow()).seconds / 60


def main(events, reddit, sticky, flairs, debug):
	overggparser.get_upcoming_events(events)
	events_to_delete = []
	for event in events:
		if event.thread is not None:
			# log.info(f"Rechecking event: {event}")
			overggparser.populate_event(event)

			if event.competition.post_match_threads:
				for match in event.matches:
					if match.state == classes.GameState.COMPLETE and match.post_thread is None:
						log.info(f"Match complete, posting post match thread: {match}")

						thread_id = reddit.submit_self_post(
							globals.SUBREDDIT,
							string_utils.render_reddit_post_match_title(match),
							string_utils.render_reddit_post_match(match, flairs)
						)

						reddit.match_thread_settings(thread_id, None)

						match.post_thread = thread_id

						comment_id = reddit.reply_thread(event.thread,
														 string_utils.render_reddit_post_match_comment(match))
						reddit.distinguish_comment(comment_id)

			if event.dirty:
				log.info(f"Event dirty, updating: {event}")
				reddit.edit_thread(
					event.thread,
					string_utils.render_reddit_event(event, flairs)
				)
				event.clean()

			if event.game_state() == classes.GameState.COMPLETE:
				log.info(f"Event complete, un-stickying and removing: {event}")
				sticky.unsticky(event.thread)
				events_to_delete.append(event)

		if (minutes_to_start(event.start) < event.competition.post_minutes_ahead or debug) and event.thread is None:
			log.info(f"Populating event: {event}")
			overggparser.populate_event(event)

			if event.prediction_thread is not None:
				log.info("Unstickying prediction thread")
				sticky.unsticky(event.prediction_thread)
				reddit.lock(event.prediction_thread)

			thread_id = reddit.submit_self_post(
				globals.SUBREDDIT,
				string_utils.render_reddit_event_title(event),
				string_utils.render_reddit_event(event, flairs)
			)
			reddit.match_thread_settings(thread_id, "new")

			sticky.sticky(thread_id, event.competition, event.start)

			event.thread = thread_id
			event.clean()

		if event.competition.discord_minutes_ahead is not None and \
				(minutes_to_start(event.start) < event.competition.discord_minutes_ahead or debug) and \
				len(event.streams) and \
				not event.posted_discord:
			if globals.WEBHOOK is not None:
				log.info(f"Posting announcement to discord: {event}")
				discord_announcement = string_utils.render_discord(event, flairs)
				if debug:
					log.info(discord_announcement)
				else:
					try:
						requests.post(globals.WEBHOOK, data={"content": discord_announcement})
					except Exception:
						log.info(discord_announcement)
						log.warning(f"Unable to post discord announcement")
						log.warning(traceback.format_exc())

				event.posted_discord = True

		if event.competition.prediction_thread_minutes_ahead is not None and \
				minutes_to_start(event.start) < event.competition.prediction_thread_minutes_ahead and \
				event.prediction_thread is None:
			log.info("Posting prediction thread")
			overggparser.populate_event(event)

			thread_id = reddit.submit_self_post(
				globals.SUBREDDIT,
				string_utils.render_reddit_prediction_thread_title(event),
				string_utils.render_reddit_prediction_thread(event, flairs)
			)
			sticky.sticky(thread_id, event.competition, event.start)

			reddit.prediction_thread_settings(thread_id)

			event.prediction_thread = thread_id
			event.clean()

	for event in events_to_delete:
		log.info(f"Event complete, removing: {event}")
		events.remove(event)

	if not debug:
		file_utils.save_state(events, sticky.get_save(), flairs.flairs)

	for event in events:
		if event.thread is not None or \
				minutes_to_start(event.start) < event.competition.post_minutes_ahead + 15:
			return 1 * 60

	return 5 * 60


if __name__ == "__main__":
	log.info("Starting")

	once = False
	debug = False
	force = False
	user = None
	if len(sys.argv) >= 2:
		user = sys.argv[1]
		for arg in sys.argv:
			if arg == 'once':
				once = True
			elif arg == 'debug':
				debug = True
			elif arg == 'force':
				force = True
	else:
		log.error("No user specified, aborting")
		sys.exit(0)

	reddit = reddit_class.Reddit(user, debug)

	state = file_utils.load_state(debug)
	if force:
		for event in state['events']:
			event.dirty = True

	log.info(f"Loaded {len(state['events'])} events")

	sticky = sticky_class.StickyManager(reddit, globals.SUBREDDIT, state['stickies'])
	flairs = flair_class.FlairManager(state['flairs'])

	while True:
		sleep_time = main(state['events'], reddit, sticky, flairs, debug)

		if once:
			break

		#log.info(f"Sleeping: {sleep_time}")
		time.sleep(sleep_time)
