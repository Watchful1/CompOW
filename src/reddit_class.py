import praw
import prawcore
import configparser
import traceback
import sys
import time
import discord_logging
import jsons
import re

log = discord_logging.get_logger()

import utils
import counters
import string_utils
from classes.event import Event
from classes.settings import Settings, DirtyMixin


class Reddit:
	def __init__(self, user, subreddit, debug=False):
		self.subreddit = subreddit
		self.user = user
		self.debug = debug
		self.flair_cache = {}
		self.webhook_cache = {}
		self.settings = None
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
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Posted thread to r/{self.subreddit} - {thread_id}")
			return thread_id
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
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
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Edited thread {thread_id}")
			return True
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
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
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Replied to thread {thread_id}")
			return comment_id
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to reply to thread {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def get_stickied_threads(self):
		try:
			stickied = []
			for submission in self.reddit.subreddit(self.subreddit).hot(limit=2):
				if submission.stickied:
					stickied.append(submission.id)
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Found stickies in r/{self.subreddit} - {str(stickied)}")
			return stickied
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to find bottom sticky in r/{self.subreddit}")
			log.warning(traceback.format_exc())
			return []

	def sticky_thread(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.sticky(state=True)
				time.sleep(3)  # stickying is weird, let's sleep a bit to let things settle down
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Stickied {thread_id}")
			return True
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to sticky {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def unsticky_thread(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.sticky(state=False)
				time.sleep(3)  # stickying is weird, let's sleep a bit to let things settle down
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Unstickied {thread_id}")
			return True
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to unsticky {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def spoiler_thread(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.spoiler()
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Spoilered {thread_id}")
			return True
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to spoiler {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def set_suggested_sort(self, thread_id, sort):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.suggested_sort(sort=sort)
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Setting suggested sort to {sort} for {thread_id}")
			return True
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to set suggested for {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def disable_inbox_replies(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).disable_inbox_replies()
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Disabling inbox replies for {thread_id}")
			return True
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
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
				counters.queries.labels(site="reddit", response="success").inc()
				log.debug(f"Couldn't find template for flair: {flair_name}")
				return None
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to find template for flair in r/{self.subreddit}")
			log.warning(traceback.format_exc())
			return None

	def set_flair(self, thread_id, flair_template_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).flair.select(flair_template_id)
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Setting flair for: {thread_id} : {flair_template_id}")
			return None
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to set flair for: {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def approve(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.approve()
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Approving thread: {thread_id}")
			return None
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to approve thread: {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def distinguish_comment(self, comment_id):
		try:
			log.debug(f"Distinguishing comment: {comment_id}")
			if not self.debug:
				self.reddit.comment(comment_id).mod.distinguish(how='yes')
			counters.queries.labels(site="reddit", response="success").inc()
			return None
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to distinguish comment: {comment_id}")
			log.warning(traceback.format_exc())
			return None

	def lock(self, thread_id):
		try:
			if not self.debug:
				self.reddit.submission(thread_id).mod.lock()
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Locking thread: {thread_id}")
			return None
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
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
			unread = self.reddit.inbox.unread()
			counters.queries.labels(site="reddit", response="success").inc()
			return unread
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to fetch messages")
			log.warning(traceback.format_exc())
			return []

	def reply_message(self, message, content):
		try:
			if self.debug:
				log.info(f"Reply: {content}")
			else:
				message.reply(content)
			counters.queries.labels(site="reddit", response="success").inc()
			log.debug(f"Replied to message {message.id}")
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to reply to message {message.id}")
			log.warning(traceback.format_exc())

	def mark_read(self, message):
		if not self.debug:
			message.mark_read()
		counters.queries.labels(site="reddit", response="success").inc()

	def is_message(self, item):
		return isinstance(item, praw.models.Message)

	def get_thread_body(self, thread_id):
		try:
			submission = self.reddit.submission(id=thread_id)
			counters.queries.labels(site="reddit", response="success").inc()
			return submission.selftext
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.warning(f"Unable to fetch thread {thread_id}")
			log.warning(traceback.format_exc())
			return None

	def list_event_pages(self):
		event_pages = []
		for page in self.reddit.subreddit(self.subreddit).wiki:
			if page.name.startswith("events/") and page.name != "events/settings":
				event_pages.append(page.name)
		counters.queries.labels(site="reddit", response="success").inc()
		return event_pages

	def get_data_string_from_wiki(self, page):
		datatag = "[](#datatag"
		wiki_content = self.reddit.subreddit(self.subreddit).wiki[page].content_md
		counters.queries.labels(site="reddit", response="success").inc()
		datatag_location = wiki_content.find(datatag)
		if datatag_location == -1:
			return None
		return wiki_content[datatag_location + len(datatag):-1].replace("%20", " ")

	def get_event_from_page(self, page):
		log.debug(f"Loading event page: {page}")
		data = self.get_data_string_from_wiki(page)
		if data is None:
			return None
		try:
			DirtyMixin.log = False
			event = jsons.loads(data, cls=Event)
			if event.wiki_name() != page:
				log.warning(f"Loaded event from page that doesn't match name: {page} : {event.wiki_name()}")
			event.clean()
			DirtyMixin.log = True
			return event
		except Exception as err:
			counters.queries.labels(site="reddit", response="error").inc()
			log.info(err)
			log.info(traceback.format_exc())
			return None

	def create_page_from_event(self, event):
		wiki_page = self.reddit.subreddit(self.subreddit).wiki[event.wiki_name()]
		try:
			wiki_page._fetch()
			counters.queries.labels(site="reddit", response="success").inc()
			if wiki_page.mod.settings()['listed']:
				log.info(f"Wiki page already exists when creating, calling update instead")
				self.update_page_from_event(event)
			else:
				log.info(f"Wiki page exists, but is not listed")
				self.toggle_page_from_event(event, True)
		except prawcore.exceptions.NotFound:
			counters.queries.labels(site="reddit", response="error").inc()
			pass

		if self.debug:
			log.info(f"Creating page: {event.wiki_name()}")
		else:
			log.debug(f"Creating page: {event.wiki_name()}")
			self.reddit.subreddit(self.subreddit).wiki.create(
				name=event.wiki_name(),
				content=string_utils.render_event_wiki(event, self.user),
				reason="Creating new event"
			)
			counters.queries.labels(site="reddit", response="success").inc()

	def update_page_from_event(self, event, clean=True):
		if clean:
			event.clean()
		if self.debug:
			log.info(f"Updating page: {event.wiki_name()}")
		else:
			log.debug(f"Updating page: {event.wiki_name()}")
			event_wiki = self.reddit.subreddit(self.subreddit).wiki[event.wiki_name()]
			old_wiki_content = event_wiki.content_md
			counters.queries.labels(site="reddit", response="success").inc()
			new_wiki_content = string_utils.render_event_wiki(event, self.user)
			if old_wiki_content == new_wiki_content:
				log.warning(f"Tried to update event page, but content was the same: {event.id}")
			else:
				event_wiki.edit(content=new_wiki_content)
				counters.queries.labels(site="reddit", response="success").inc()

	def toggle_page_from_event(self, event, show):
		if self.debug:
			log.info(f"{('Showing' if show else 'Hiding')} page: {event.wiki_name()}")
		else:
			log.debug(f"{('Showing' if show else 'Hiding')} page: {event.wiki_name()}")
			event_wiki = self.reddit.subreddit(self.subreddit).wiki[event.wiki_name()]
			event_wiki.mod.update(listed=show, permlevel=0)
			counters.queries.labels(site="reddit", response="success").inc()

	def save_settings(self, settings, events):
		if self.debug:
			log.info(f"Saving settings: {settings}")
		else:
			log.debug(f"Saving settings: {settings}")
			settings_wiki = self.reddit.subreddit(self.subreddit).wiki["events/settings"]
			old_wiki_content = settings_wiki.content_md
			counters.queries.labels(site="reddit", response="success").inc()
			new_wiki_content = string_utils.render_settings_wiki(settings, self.user, events)
			if old_wiki_content == new_wiki_content:
				log.debug(f"No changes in wiki page, not updating")
			else:
				settings_wiki.edit(content=new_wiki_content)
				counters.queries.labels(site="reddit", response="success").inc()

	def get_settings(self):
		if self.settings is None:
			try:
				data = self.get_data_string_from_wiki("events/settings")
				self.settings = jsons.loads(data, cls=Settings)
			except prawcore.exceptions.NotFound as err:
				log.info(f"No settings wiki found, returning blank")
			except Exception as err:
				log.warning(f"Couldn't load settings, unknown error: {err}")
				log.warning(traceback.format_exc())

		if self.settings is None:
			return Settings()
		else:
			return self.settings

	def update_sidebar(self, event_string):
		if self.debug:
			log.info(f"Updating sidebar")
		else:
			log.debug(f"Updating sidebar")
			sidebar_wiki = self.reddit.subreddit(self.subreddit).wiki['config/sidebar']
			old_wiki_content = sidebar_wiki.content_md
			counters.queries.labels(site="reddit", response="success").inc()
			new_wiki_content = re.sub(r"(\[\]\(#mtstart\)\r?\n)(.*)(\[\]\(#mtend\))", r"\1" + event_string + r"\3", old_wiki_content, flags=re.M | re.DOTALL)

			if old_wiki_content == new_wiki_content:
				log.debug(f"Tried to update sidebar, but content was the same")
			else:
				sidebar_wiki.edit(content=new_wiki_content)
				counters.queries.labels(site="reddit", response="success").inc()

	def fill_empty_stickies(self):
		settings = self.get_settings()
		if len(settings.stickies):
			stickied_threads = self.get_stickied_threads()
			if len(stickied_threads) < 2:
				first_saved = settings.stickies.pop(0)
				self.sticky_thread(first_saved)
			if len(stickied_threads) < 1 and len(settings.stickies):
				first_saved = settings.stickies.pop(0)
				self.sticky_thread(first_saved)
