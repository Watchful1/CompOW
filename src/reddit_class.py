import logging.handlers
import praw
import configparser
import traceback
import sys

import globals

log = logging.getLogger("bot")


class Reddit:
	def __init__(self, user):
		try:
			self.reddit = praw.Reddit(
				user,
				user_agent=globals.USER_AGENT)
		except configparser.NoSectionError:
			log.error("User "+user+" not in praw.ini, aborting")
			sys.exit(0)

		globals.ACCOUNT_NAME = str(self.reddit.user.me()).lower()

		log.info("Logged into reddit as /u/" + globals.ACCOUNT_NAME)

		config_keys = [
			{'var': "DISCORD_TOKEN", 'name': "discord_token"},
		]
		for key in config_keys:
			if self.reddit.config.CONFIG.has_option(user, key['name']):
				setattr(globals, key['var'], self.reddit.config.CONFIG[user][key['name']])
			else:
				log.error(f"{key['name']} key not in config, aborting")

	def submit_self_post(self, subreddit, title, text):
		try:
			thread = self.reddit.subreddit(subreddit).submit(title=title, selftext=text)
			log.debug(f"Posted thread to r/{subreddit} - {thread.id}")
			return thread.id
		except Exception as err:
			log.warning(f"Unable to post thread to r/{subreddit}")
			log.warning(traceback.format_exc())
			return None

	def edit_thread(self, thread_id, text):
		try:
			submission = self.reddit.submission(id=thread_id)
			submission.edit(text)
			log.debug(f"Edited thread {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to edit thread {thread_id}")
			log.warning(traceback.format_exc())
			return False

	def get_stickied_threads(self, subreddit):
		try:
			stickied = []
			for submission in self.reddit.subreddit(subreddit).hot(limit=2):
				if submission.stickied:
					stickied.append(submission.id)
				else:
					stickied.append(None)
			log.debug(f"Found stickies in r/{subreddit} - {str(stickied)}")
			return stickied
		except Exception as err:
			log.warning(f"Unable to find bottom sticky in r/{subreddit}")
			log.warning(traceback.format_exc())
			return None

	def sticky_thread(self, thread_id):
		try:
			self.reddit.submission(thread_id).mod.sticky(state=True)
			log.debug(f"Stickied {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to sticky {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def unsticky_thread(self, thread_id):
		try:
			self.reddit.submission(thread_id).mod.sticky(state=False)
			log.debug(f"Unstickied {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to unsticky {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def spoiler_thread(self, thread_id):
		try:
			self.reddit.submission(thread_id).mod.spoiler()
			log.debug(f"Spoilered {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to spoiler {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def set_suggested_sort(self, thread_id, sort):
		try:
			self.reddit.submission(thread_id).mod.suggested_sort(sort=sort)
			log.debug(f"Setting suggested sort to new for {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to set suggested for for {thread_id}")
			log.warning(traceback.format_exc())
			return None
