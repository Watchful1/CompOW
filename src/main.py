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
	events_to_delete = []
	for event in events:
		if event.thread is not None:
			log.info(f"Rechecking event: {event}")
			overggparser.populate_event(event)

			if event.competition.post_match_threads:
				for match in event.matches:
					if match.state == classes.GameState.COMPLETE and match.post_thread is None:
						log.info(f"Match complete, posting post match thread: {match}")

						thread_id = reddit.submit_self_post(
							globals.SUBREDDIT,
							string_utils.render_reddit_post_match_title(match),
							string_utils.render_reddit_post_match(match)
						)

						reddit.match_thread_settings(thread_id, None)

						match.post_thread = thread_id

			if event.dirty:
				log.info(f"Event dirty, updating: {event}")
				reddit.edit_thread(
					event.thread,
					string_utils.render_reddit_event(event)
				)
				event.clean()

			if event.game_state() == classes.GameState.COMPLETE:
				log.info(f"Event complete, removing: {event}")
				events_to_delete.append(event)

		if current_time + timedelta(minutes=event.competition.post_minutes_ahead) >= event.start and event.thread is None:
			log.info(f"Populating event: {event}")
			overggparser.populate_event(event)

			thread_id = reddit.submit_self_post(
				globals.SUBREDDIT,
				string_utils.render_reddit_event_title(event),
				string_utils.render_reddit_event(event)
			)
			sticky.sticky(thread_id, event.competition, event.start)

			reddit.match_thread_settings(thread_id)

			event.thread = thread_id
			event.clean()

	for event in events_to_delete:
		events.remove(event)

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


# sticky in correct order
# save previous sticky and re-sticky
# unpin at end
# contenders post match thread if more than x comments, and lock post/sticky comment
# discord notifications
# post match threads in OP, comments in thread
# team symbols in match thread, post match thread
# stream symbols on streams
# map details in post match thread
# loop faster when a match is in progress and slower if there is none

