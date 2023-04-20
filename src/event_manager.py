import discord_logging
import traceback
import requests

log = discord_logging.get_logger()

import utils
import liquipedia_parser
import string_utils
from classes.settings import Settings


def update_events(reddit, events, flairs):
	active_event = False
	for event in events.values():
		liquipedia_parser.update_event(event)

		for match_day in event.match_days:
			# post initial thread
			new_thread_posted = False
			if match_day.thread_id is None and \
					not match_day.is_complete() and \
					utils.minutes_to_start(match_day.approved_start_datetime) < event.match_thread_minutes_before:
				log.info(f"Posting match thread for {event.id}:{match_day.id} : {event.name} : starting in {utils.minutes_to_start(match_day.approved_start_datetime)} minutes")

				# TODO: remove prediction thread if posted

				thread_id = reddit.submit_self_post(
					string_utils.render_reddit_event_title(event),
					string_utils.render_reddit_event(match_day, event, flairs, reddit.subreddit),
					flair="match"
				)
				reddit.match_thread_settings(thread_id, "new")

				stickied_threads = reddit.get_stickied_threads()
				reddit.sticky_thread(thread_id)
				if len(stickied_threads) == 1:
					log.info(f"Stickying first, moving {stickied_threads[0]} down")
					reddit.unsticky_thread(stickied_threads[0])
					reddit.sticky_thread(stickied_threads[0])
				elif len(stickied_threads) == 2:
					log.info(f"Stickying first, moving {stickied_threads[0]} down, saving {stickied_threads[1]}")
					reddit.unsticky_thread(stickied_threads[0])
					reddit.sticky_thread(stickied_threads[0])
					settings = Settings.get_settings(reddit)
					settings.stickies.insert(0, stickied_threads[1])
					settings.save(reddit)
				else:
					log.warning(f"Got {len(stickied_threads)} stickied threads")

				match_day.thread_id = thread_id
				new_thread_posted = True

			# post match thread if game is done
			if event.post_match_threads and match_day.thread_id is not None:
				for i, game in enumerate(match_day.approved_games):
					if game.post_thread_id is None:
						# owl_complete = False
						# if match.owl_complete is not None and \
						# 		match.owl_complete + timedelta(minutes=2) < static.utcnow() < match.owl_complete + timedelta(minutes=5):
						# 	log.warning(f"Overwatch api says match is complete, but over.gg doesn't {match}")
						# 	owl_complete = True

						if game.complete:
							log.info(f"Match complete, posting post match thread: {event.id}:{match_day.id}:{game.id}")

							thread_id = reddit.submit_self_post(
								string_utils.render_reddit_post_match_title(
									event, match_day, game,
									spoilers=match_day.spoiler_prevention,
									match_num=i + 1
								),
								string_utils.render_reddit_post_match(event, match_day, game, flairs),
								flair="match"
							)

							reddit.match_thread_settings(thread_id, None)

							game.post_thread_id = thread_id

							comment_id = reddit.reply_thread(
								match_day.thread_id,
								string_utils.render_reddit_post_match_comment(game, reddit.subreddit))
							reddit.distinguish_comment(comment_id)

			# update thread if dirty
			if not new_thread_posted and match_day.thread_id is not None and match_day.is_thread_dirty():
				log.info(f"Match day dirty, updating thread: {event.id}:{match_day.id} : {match_day.thread_id}")

				reddit.edit_thread(
					match_day.thread_id,
					string_utils.render_reddit_event(match_day, event, flairs, reddit.subreddit)
				)

			# post discord announcement
			if event.discord_key is not None and \
					not match_day.discord_posted and \
					not match_day.is_complete() and \
					utils.minutes_to_start(match_day.approved_start_datetime) < event.discord_minutes_before:
				log.info(f"Posting announcement to discord: {event.id}:{match_day.id}")
				discord_announcement = string_utils.render_discord(event, match_day, flairs)
				if reddit.debug or discord_announcement is None:
					log.info(discord_announcement)
				else:
					try:
						requests.post(reddit.get_webhook(event.discord_key), data={"content": discord_announcement})
					except Exception as err:
						log.info(discord_announcement)
						log.warning(f"Unable to post discord announcement {err}")
						log.warning(traceback.format_exc())

				match_day.discord_posted = True

			# TODO post predictions thread day before event week starts
			# TODO remove match thread if event complete and longer than set time

			# check if match day is active or close so we can scan faster
			if not match_day.is_complete() and \
					utils.minutes_to_start(match_day.approved_start_datetime) < (event.match_thread_minutes_before + 15):
				active_event = True

	if active_event:
		return utils.utcnow(offset=60*1)  # scan every 1 minute while active
	else:
		return utils.utcnow(offset=60*5)  # scan every 5 minutes while not active



