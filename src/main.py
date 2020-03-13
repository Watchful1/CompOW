#!/usr/bin/python3

import sys
import time
import requests
import traceback
import re
import discord_logging
import prawcore
import logging.handlers

log = discord_logging.init_logging()

import static
import overggparser
import string_utils
import sticky_manager
import reddit_class
import file_utils
import flair_manager
import mappings
from classes.enums import GameState


def minutes_to_start(start):
	if start > static.utcnow():
		return (start - static.utcnow()).total_seconds() / 60
	elif start < static.utcnow():
		return ((static.utcnow() - start).total_seconds() / 60) * -1
	else:
		return 0


def main(events, reddit, sticky, flairs, debug, no_discord, keys):
	try:
		overggparser.get_upcoming_events(events)
	except Exception as err:
		log.warning("Something went wrong parsing the api results")
		log.warning(traceback.format_exc())

	upcoming_owl_events = []
	events_to_delete = []
	for event in events:
		if event.thread is not None:
			# log.info(f"Rechecking event: {event}")
			overggparser.populate_event(event)

			if event.competition.post_match_threads:
				for match in event.matches:
					if match.state == GameState.COMPLETE and match.post_thread is None:
						log.info(f"Match complete, posting post match thread: {match}")

						thread_id = reddit.submit_self_post(
							static.SUBREDDIT,
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

			if event.game_state() == GameState.COMPLETE:
				if event.competition.leave_thread_minutes is not None:
					if event.completion_time is None:
						event.completion_time = static.utcnow()
					elif ((static.utcnow() - event.completion_time).seconds / 60) > event.competition.leave_thread_minutes:
						log.info(f"Event complete after cooldown, un-stickying and removing: {event}")
						sticky.unsticky(event.thread)
						events_to_delete.append(event)
				else:
					log.info(f"Event complete, un-stickying and removing: {event}")
					sticky.unsticky(event.thread)
					events_to_delete.append(event)

		if (minutes_to_start(event.start) < event.competition.post_minutes_ahead) and event.thread is None:
			log.info(f"Populating event: {event}")
			overggparser.populate_event(event)

			if len(event.streams):
				if event.is_owl() and keys['prediction_thread'] is not None:
					log.info("Unstickying prediction thread")
					sticky.unsticky(keys['prediction_thread'])
					reddit.lock(keys['prediction_thread'])
					keys['prediction_thread'] = None

				thread_id = reddit.submit_self_post(
					static.SUBREDDIT,
					string_utils.render_reddit_event_title(event),
					string_utils.render_reddit_event(event, flairs)
				)
				reddit.match_thread_settings(thread_id, "new")

				sticky.sticky(thread_id, event.competition, event.start)

				event.thread = thread_id
				event.clean()

		if event.competition.discord is not None:
			for discord_notification in event.competition.discord:
				if discord_notification.type not in event.posted_discord and \
						(minutes_to_start(event.start) < discord_notification.minutes_ahead) and \
						len(event.streams):
					log.info(f"Posting announcement to discord: {event} : {discord_notification.type}")
					discord_announcement = string_utils.render_discord(event, flairs, discord_notification)
					if debug or no_discord:
						log.info(discord_announcement)
					else:
						try:
							requests.post(static.get_webhook(discord_notification.type), data={"content": discord_announcement})
						except Exception:
							log.info(discord_announcement)
							log.warning(f"Unable to post discord announcement")
							log.warning(traceback.format_exc())

					event.posted_discord.append(discord_notification.type)

					if not debug:
						file_utils.save_state(events, sticky.get_save(), flairs.flairs, keys)

		if event.is_owl() and minutes_to_start(event.start) < 72 * 60:
			upcoming_owl_events.append(event)

	for event in events_to_delete:
		log.info(f"Event complete, removing: {event}")
		events.remove(event)

	if len(upcoming_owl_events) and keys['prediction_thread'] is None and static.utcnow().weekday() == 4 and static.utcnow().hour > 18:
		log.info("Posting prediction thread")
		thread_id = reddit.submit_self_post(
			static.SUBREDDIT,
			string_utils.render_reddit_prediction_thread_title(upcoming_owl_events[0]),
			string_utils.render_reddit_prediction_thread(upcoming_owl_events, flairs)
		)
		keys['prediction_thread'] = thread_id
		sticky.sticky(thread_id, upcoming_owl_events[0].competition, upcoming_owl_events[0].start)

		reddit.prediction_thread_settings(thread_id)

	if not debug:
		file_utils.save_state(events, sticky.get_save(), flairs.flairs, keys)

	for event in events:
		if event.thread is not None or \
				minutes_to_start(event.start) < event.competition.post_minutes_ahead + 15:
			return 1

	return 5


def check_messages(reddit, flairs):
	for message in reddit.get_unread():
		if reddit.is_message(message):
			if message.author is not None and message.author.name in static.AUTHORIZED_USERS:
				log.info(f"Processing an authorized message from u/{message.author.name}")

				line_results = []
				for line in message.body.splitlines():
					post_id = re.findall(r'(?:reddit.com/r/\w*/comments/)(\w*)', line)
					if not len(post_id):
						log.info("Could not find reddit post")
						line_results.append("Could not find a reddit post")
						continue
					post_id = post_id[0]

					video = re.findall(r'(http\S*youtube\S*)', line)
					if not len(video):
						log.info("Could not find a video link")
						line_results.append("Could not find a video link")
						continue
					video = video[0]

					current_body = reddit.get_thread_body(post_id)
					if current_body is None:
						log.info(f"Could not find thread: {post_id}")
						line_results.append(f"Could not find thread: {post_id}")
						continue

					new_body = string_utils.render_append_highlights(current_body, video, flairs)
					if new_body is None:
						log.info(f"Could not find end of post: {post_id}")
						line_results.append(
							"Could not find end of body. This could mean a highlight video is "
							"already appended, or it's not a post match thread")
						continue

					if not reddit.edit_thread(post_id, new_body):
						log.info("Could not edit thread")
						line_results.append(
							"Could not edit thread. This could mean it's not a thread from the bot or "
							"something could be wrong with reddit")
						continue

					line_results.append(f"Added link {video} to thread {post_id}")

				reddit.reply_message(message, "\n\n".join(line_results))

			elif message.author is None:
				log.info(f"Received a message from reddit, skipping")
			else:
				log.info(f"Received a message from u/{message.author.name}, skipping")

		reddit.mark_read(message)

	return


if __name__ == "__main__":
	log.info("Starting")

	once = False
	debug = False
	force = False
	no_discord = False
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
			elif arg == 'no_discord':
				no_discord = True
	else:
		log.error("No user specified, aborting")
		sys.exit(0)

	if not debug:
		static.debug_now = None
		discord_logging.init_discord_logging(user, logging.WARNING, 1)
	reddit = reddit_class.Reddit(user, debug)

	state = file_utils.load_state(debug)
	if force:
		for event in state['events']:
			event.dirty = True

	log.info(f"Loaded {len(state['events'])} events")

	sticky = sticky_manager.StickyManager(reddit, static.SUBREDDIT, state['stickies'])
	flairs = flair_manager.FlairManager(state['flairs'])
	events = state['events']
	for event in events:
		rank, competition = mappings.get_competition(event.competition.name)
		event.competition = competition

	loop = 0
	loop_sleep = 0
	while True:
		try:
			if loop == 0:
				loop_sleep = main(state['events'], reddit, sticky, flairs, debug, no_discord, state['keys'])
			check_messages(reddit, flairs)
		except prawcore.exceptions.ServerError as err:
			log.warning("Caught praw ServerError")
			log.warning(traceback.format_exc())
		except prawcore.exceptions.Conflict as err:
			log.warning("Caught praw Conflict")
			log.warning(traceback.format_exc())
		except prawcore.exceptions.RequestException as err:
			log.warning("Caught praw RequestException")
			log.warning(traceback.format_exc())

		discord_logging.flush_discord()
		loop += 1
		if loop >= loop_sleep:
			loop = 0

		if debug:
			for event in state['events']:
				log.info(str(event))

		if once:
			break

		time.sleep(60)
