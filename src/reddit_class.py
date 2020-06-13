import praw
import configparser
import traceback
import sys
import time
import discord_logging

import static

log = discord_logging.get_logger()


class Reddit:
	def __init__(self, user, debug=False):
		self.debug = debug
		try:
			self.reddit = praw.Reddit(
				user,
				user_agent=static.USER_AGENT)
		except configparser.NoSectionError:
			log.error("User "+user+" not in praw.ini, aborting")
			sys.exit(0)

		static.ACCOUNT_NAME = str(self.reddit.user.me()).lower()

		log.info("Logged into reddit as /u/" + static.ACCOUNT_NAME)

		config_keys = [
			{'var': "WEBHOOK_COW", 'name': "webhook_cow"},
			{'var': "WEBHOOK_THEOW", 'name': "webhook_theow"},
		]
		for key in config_keys:
			if self.reddit.config.CONFIG.has_option(user, key['name']):
				setattr(static, key['var'], self.reddit.config.CONFIG[user][key['name']])
			else:
				log.error(f"{key['name']} key not in config")

	def submit_self_post(self, subreddit, title, text, chat_post=False):
		try:
			if self.debug:
				log.info(f"Title: {title}")
				log.info(f"Body: {text}")
				thread_id = "test"
			else:
				if chat_post:
					thread = self.reddit.subreddit(subreddit).submit(title=title, selftext=text, discussion_type="CHAT")
				else:
					thread = self.reddit.subreddit(subreddit).submit(title=title, selftext=text)
				thread_id = thread.id
			log.debug(f"Posted thread to r/{subreddit} - {thread_id}")
			return thread_id
		except Exception as err:
			log.warning(f"Unable to post thread to r/{subreddit}")
			log.warning(traceback.format_exc())
			return None

	def edit_thread(self, thread_id, text):
		try:
			if self.debug:
				log.info(f"Body: {text}")
			else:
				submission = self.reddit.submission(id=thread_id)
				submission.edit(text)
			log.debug(f"Edited thread {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to edit thread {thread_id}")
			log.warning(traceback.format_exc())
			return False

	def reply_thread(self, thread_id, text):
		try:
			if self.debug:
				log.info(f"Text: {text}")
				comment_id = "test"
			else:
				submission = self.reddit.submission(id=thread_id)
				comment_id = submission.reply(text)
			log.debug(f"Replied to thread {thread_id}")
			return comment_id
		except Exception as err:
			log.warning(f"Unable to reply to thread {thread_id}")
			log.warning(traceback.format_exc())
			return None

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
			if not self.debug:
				self.reddit.submission(thread_id).mod.sticky(state=True)
				time.sleep(3)  # stickying is weird, let's sleep a bit to let things settle down
			log.debug(f"Stickied {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to sticky {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def unsticky_thread(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.sticky(state=False)
				time.sleep(3)  # stickying is weird, let's sleep a bit to let things settle down
			log.debug(f"Unstickied {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to unsticky {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def spoiler_thread(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.spoiler()
			log.debug(f"Spoilered {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to spoiler {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def set_suggested_sort(self, thread_id, sort):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.suggested_sort(sort=sort)
			log.debug(f"Setting suggested sort to {sort} for {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to set suggested for {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def disable_inbox_replies(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).disable_inbox_replies()
			log.debug(f"Disabling inbox replies for {thread_id}")
			return True
		except Exception as err:
			log.warning(f"Unable to disable inbox replies for {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def get_flair_id(self, thread_id, flair_name):
		try:
			if self.debug:
				return "test"
			else:
				flairs = self.reddit.submission(thread_id).flair.choices()
				for flair in flairs:
					if flair['flair_text'] == flair_name:
						log.debug(f"Returning flair id for flair name: {flair_name} : {flair['flair_template_id']}")
						return flair['flair_template_id']
				log.debug(f"Couldn't find template for flair: {flair_name}")
				return None
		except Exception as err:
			log.warning(f"Unable to find template for flair: {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def set_flair(self, thread_id, flair_template_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).flair.select(flair_template_id)
			log.debug(f"Setting flair for: {thread_id} : {flair_template_id}")
			return None
		except Exception as err:
			log.warning(f"Unable to set flair for: {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def approve(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.approve()
			log.debug(f"Approving thread: {thread_id}")
			return None
		except Exception as err:
			log.warning(f"Unable to approve thread: {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def distinguish_comment(self, comment_id):
		try:
			if not self.debug:
				self.reddit.comment(comment_id).mod.distinguish(how='yes')
			log.debug(f"Distinguishing comment: {comment_id}")
			return None
		except Exception as err:
			log.warning(f"Unable to distinguish comment: {comment_id}")
			log.warning(traceback.format_exc())
			return None

	def lock(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.lock()
			log.debug(f"Locking thread: {thread_id}")
			return None
		except Exception as err:
			log.warning(f"Unable to lock thread: {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def match_thread_settings(self, thread_id, sort):
		self.spoiler_thread(thread_id)
		if sort is not None:
			self.set_suggested_sort(thread_id, sort)
		self.disable_inbox_replies(thread_id)
		flair_template_id = self.get_flair_id(thread_id, "Matchthread")
		if flair_template_id is not None:
			self.set_flair(thread_id, flair_template_id)
		self.approve(thread_id)

	def prediction_thread_settings(self, thread_id):
		self.disable_inbox_replies(thread_id)
		flair_template_id = self.get_flair_id(thread_id, "Matchthread")
		if flair_template_id is not None:
			self.set_flair(thread_id, flair_template_id)
		self.approve(thread_id)

	def get_unread(self):
		try:
			return self.reddit.inbox.unread()
		except Exception as err:
			log.warning(f"Unable to fetch messages")
			log.warning(traceback.format_exc())
			return []

	def reply_message(self, message, content):
		try:
			if self.debug:
				log.info(f"Reply: {content}")
			else:
				message.reply(content)
			log.debug(f"Replied to message {message.id}")
		except Exception as err:
			log.warning(f"Unable to reply to message {message.id}")
			log.warning(traceback.format_exc())

	def mark_read(self, message):
		if not self.debug:
			message.mark_read()

	def is_message(self, item):
		return isinstance(item, praw.models.Message)

	def get_thread_body(self, thread_id):
		try:
			submission = self.reddit.submission(id=thread_id)
			return submission.selftext
		except Exception as err:
			log.warning(f"Unable to fetch thread {thread_id}")
			log.warning(traceback.format_exc())
			return None
