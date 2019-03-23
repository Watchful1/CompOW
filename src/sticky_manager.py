import bisect
import logging.handlers

from classes.sticky import Sticky

log = logging.getLogger("bot")


class StickyManager:
	def __init__(self, reddit, subreddit, stickies):
		self.reddit = reddit
		self.subreddit = subreddit
		self.current_stickies = stickies['current']
		self.saved_stickies = stickies['saved']

	def get_save(self):
		return {'current': self.current_stickies, 'saved': self.saved_stickies}

	def update_current_stickies(self):
		stickies = self.reddit.get_stickied_threads(self.subreddit)
		result_stickies = []
		for sticky in stickies:
			if sticky is None:
				result_stickies.append(None)
				continue

			found = False
			for current_sticky in self.current_stickies:
				if current_sticky is not None and current_sticky.thread_id == sticky:
					result_stickies.append(current_sticky)
					found = True

			if not found:
				result_stickies.append(Sticky(sticky))
		self.current_stickies = result_stickies
		log.debug(f"Updated current stickies to: {result_stickies[0]}, {result_stickies[1]}")

	def sticky(self, thread_id, competition, start):
		self.update_current_stickies()
		new_sticky = Sticky(thread_id, competition.name, start)

		if self.current_stickies[0] is None or self.current_stickies[0] < new_sticky:
			log.info(f"Stickying first: {new_sticky.thread_id}")
			for current_sticky in self.current_stickies:
				if current_sticky is not None:
					self.reddit.unsticky_thread(current_sticky.thread_id)
			self.reddit.sticky_thread(new_sticky.thread_id)
			if self.current_stickies[0] is not None:
				self.reddit.sticky_thread(self.current_stickies[0].thread_id)

			if self.current_stickies[1] is not None:
				bisect.insort(self.saved_stickies, self.current_stickies[1])

		elif self.current_stickies[1] is None or self.current_stickies[1] < new_sticky:
			log.info(f"Stickying second: {new_sticky.thread_id}")
			self.reddit.sticky_thread(new_sticky)

			if self.current_stickies[1] is not None:
				bisect.insort(self.saved_stickies, self.current_stickies[1])

		else:
			log.info(f"Saving for later: {new_sticky.thread_id}")
			bisect.insort(self.saved_stickies, new_sticky)

		self.update_current_stickies()

	def unsticky(self, thread_id):
		self.update_current_stickies()
		for current_sticky in self.current_stickies:
			if current_sticky is not None and current_sticky.thread_id == thread_id:
				self.reddit.unsticky_thread(thread_id)
				if len(self.saved_stickies) > 0:
					re_sticky = self.saved_stickies.pop()
					self.reddit.sticky_thread(re_sticky.thread_id)
					break

		self.update_current_stickies()
