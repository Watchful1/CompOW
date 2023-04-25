import praw
import prawcore
import configparser
import traceback
import sys
import time
import discord_logging
import jsons

log = discord_logging.get_logger()

import utils
import string_utils
from classes.event import Event
from classes.settings import Settings


class Reddit:
	def __init__(self, user, subreddit, debug=False):
		self.subreddit = subreddit
		self.user = user
		self.debug = debug
		self.flair_cache = {}
		self.webhook_cache = {}
		try:
			self.reddit = praw.Reddit(user, user_agent=utils.USER_AGENT)
		except configparser.NoSectionError:
			log.error(f"User {user} not in praw.ini, aborting")
			sys.exit(0)

		log.info(f"Logged into reddit as u/{self.reddit.user.me().name}")

	def get_webhook(self, key):
		if key not in self.webhook_cache:
			if self.reddit.config.CONFIG.has_option(self.user, f"webhook_{key}"):
				self.webhook_cache[key] = self.reddit.config.CONFIG[self.user][f"webhook_{key}"]
			else:
				return None
		return self.webhook_cache[key]

	def submit_self_post(self, title, text, chat_post=False, flair=None):
		try:
			if self.debug:
				log.info(f"Title: {title}")
				log.info(f"Body: {text}")
				thread_id = "test"
			else:
				flair_id = None
				if flair is not None:
					flair_id = self.get_flair_id(flair)
				if chat_post:
					thread = self.reddit.subreddit(self.subreddit).submit(title=title, selftext=text, discussion_type="CHAT", flair_id=flair_id)
				else:
					thread = self.reddit.subreddit(self.subreddit).submit(title=title, selftext=text, flair_id=flair_id)
				thread_id = thread.id
			log.debug(f"Posted thread to r/{self.subreddit} - {thread_id}")
			return thread_id
		except Exception as err:
			log.warning(f"Unable to post thread to r/{self.subreddit}")
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
				comment_id = submission.reply(text).id
			log.debug(f"Replied to thread {thread_id}")
			return comment_id
		except Exception as err:
			log.warning(f"Unable to reply to thread {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def get_stickied_threads(self):
		try:
			stickied = []
			for submission in self.reddit.subreddit(self.subreddit).hot(limit=2):
				if submission.stickied:
					stickied.append(submission.id)
			log.debug(f"Found stickies in r/{self.subreddit} - {str(stickied)}")
			return stickied
		except Exception as err:
			log.warning(f"Unable to find bottom sticky in r/{self.subreddit}")
			log.warning(traceback.format_exc())
			return []

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

	def get_flair_id(self, flair_name):
		try:
			if self.debug:
				return "test"
			else:
				if flair_name in self.flair_cache:
					return self.flair_cache[flair_name]
				for flair in self.reddit.subreddit(self.subreddit).flair.link_templates.user_selectable():
					if flair_name in flair['flair_text'].lower():
						log.debug(f"Returning flair id for flair name: {flair_name} : {flair['flair_template_id']}")
						self.flair_cache[flair_name] = flair['flair_template_id']
						return flair['flair_template_id']
				log.debug(f"Couldn't find template for flair: {flair_name}")
				return None
		except Exception as err:
			log.warning(f"Unable to find template for flair in r/{self.subreddit}")
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
			log.debug(f"Distinguishing comment: {comment_id}")
			if not self.debug:
				self.reddit.comment(comment_id).mod.distinguish(how='yes')
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
		self.approve(thread_id)

	def prediction_thread_settings(self, thread_id):
		self.disable_inbox_replies(thread_id)
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

	def list_event_pages(self):
		event_pages = []
		for page in self.reddit.subreddit(self.subreddit).wiki:
			if page.name.startswith("events/") and page.name != "events/settings":
				event_pages.append(page.name)
		return event_pages

	def get_event_from_page(self, page):
		#log.debug(f"Loading event page: {page}")
		datatag = "[](#datatag"
		wiki_content = self.reddit.subreddit(self.subreddit).wiki[page].content_md
		datatag_location = wiki_content.find(datatag)
		if datatag_location == -1:
			return None
		data = wiki_content[datatag_location + len(datatag):-1].replace("%20", " ")
		try:
			return jsons.loads(data, cls=Event)
		except Exception as err:
			log.info(err)
			log.info(traceback.format_exc())
			return None

	def create_page_from_event(self, event):
		if self.debug:
			log.info(f"Creating page: {event.wiki_name()}")
		else:
			log.debug(f"Creating page: {event.wiki_name()}")
			self.reddit.subreddit(self.subreddit).wiki.create(
				name=event.wiki_name(),
				content=string_utils.render_event_wiki(event, self.user),
				reason="Creating new event"
			)

	def update_page_from_event(self, event):
		if self.debug:
			log.info(f"Updating page: {event.wiki_name()}")
		else:
			#log.debug(f"Updating page: {event.wiki_name()}")
			event_wiki = self.reddit.subreddit(self.subreddit).wiki[event.wiki_name()]
			event_wiki.edit(content=string_utils.render_event_wiki(event, self.user))

	def hide_page_from_event(self, event):
		if self.debug:
			log.info(f"Hiding page: {event.wiki_name()}")
		else:
			log.debug(f"Hiding page: {event.wiki_name()}")
			event_wiki = self.reddit.subreddit(self.subreddit).wiki[event.wiki_name()]
			event_wiki.mod.update(listed=False, permlevel=0)

	def save_settings(self, settings):
		if self.debug:
			log.info(f"Updating settings: {settings}")
		else:
			#log.debug(f"Updating page: {event.wiki_name()}")
			settings_wiki = self.reddit.subreddit(self.subreddit).wiki["events/settings"]
			settings_wiki.edit(content=str(jsons.dumps(settings, cls=Settings, strip_nulls=True)))

	def get_settings(self):
		try:
			wiki_content = self.reddit.subreddit(self.subreddit).wiki["events/settings"].content_md
			return jsons.loads(wiki_content, cls=Event)
		except prawcore.exceptions.NotFound as err:
			log.info(f"No settings wiki found, returning blank")
			return Settings()
		except Exception as err:
			log.warning(f"Couldn't load settings, unknown error: {err}")
			log.warning(traceback.format_exc())
			return Settings()

