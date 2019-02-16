import logging.handlers
import os
import sys
import time
from datetime import datetime
from datetime import timedelta

import globals
import overggparser
import string_utils
import classes
import sticky_class
import reddit_class
import file_utils

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


def main(events, reddit, sticky):
	globals.debug_time = datetime.utcnow()
	current_time = globals.debug_time

	overggparser.get_upcoming_events(events)
	for event in events:
		if current_time + timedelta(minutes=30) >= event.start and event.thread is None:
			log.info(f"Populating event: {event}")
			overggparser.populate_event(event)

			# thread_id = reddit.submit_self_post(
			# 	globals.SUBREDDIT,
			# 	string_utils.render_reddit_event_title(event),
			# 	string_utils.render_reddit_event(event)
			# )
			# sticky.sticky_second(thread_id, event.competition, event.start)
			#
			# reddit.spoiler_thread(thread_id)
			# reddit.set_suggested_sort(thread_id, "new")
			#
			# event.thread = thread_id
			event.clean()

		if event.thread is not None:
			log.info(f"Rechecking event: {event}")
			overggparser.populate_event(event)

			if event.dirty:
				log.info(f"Event dirty, updating: {event}")
				reddit.edit_thread(
					event.thread,
					string_utils.render_reddit_event(event)
				)
				event.clean()

	file_utils.save_state(events, sticky.get_save())


if __name__ == "__main__":
	log.info("Starting")

	once = False
	debug = False
	user = None
	if len(sys.argv) >= 2:
		user = sys.argv[1]
		for arg in sys.argv:
			if arg == 'once':
				once = True
			elif arg == 'debug':
				debug = True
	else:
		log.error("No user specified, aborting")
		sys.exit(0)

	reddit = reddit_class.Reddit(user)
	events, stickies = file_utils.load_state()
	sticky = sticky_class.StickyManager(reddit, globals.SUBREDDIT, stickies)

	while True:
		main(events, reddit, sticky)

		if once:
			break

		time.sleep(60*2)


# flair: Match Thread
# save previous sticky and re-sticky
# disable inbox replies
# unpin at end
# contenders post match thread if more than x comments, and lock post/sticky comment
# get stream names from overgg
# discord notifications
# only post from whitelisted tournaments
# post match threads for OWL
# order/whitelist/flag streams
# approve post

