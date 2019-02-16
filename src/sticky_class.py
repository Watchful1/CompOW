import bisect
import logging.handlers

import mappings

log = logging.getLogger("bot")


class Sticky:
	def __init__(self, thread_id, competition=None, start=None):
		self.thread_id = thread_id
		self.competition = competition
		self.start = start

	def __str__(self):
		return f"{self.thread_id} : {self.competition} : {self.start}"

	def __lt__(self, other):
		self_ranking = mappings.competition_ranking(self.competition)
		other_ranking = mappings.competition_ranking(other.competition)
		if self_ranking is None:
			if other_ranking is None:
				return False
			else:
				return True
		else:
			if other_ranking is None:
				return False
			else:
				if self_ranking == other_ranking:
					return self.start >= other.start
				else:
					return self_ranking > other_ranking


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


	def sticky_second(self, thread_id, competition, start):
		self.update_current_stickies()
		second_sticky = self.current_stickies[1]
		if second_sticky is None:
			self.reddit.sticky_thread(thread_id)
		else:
			new_sticky = Sticky(thread_id, competition.name, start)
			if second_sticky < new_sticky:
				bisect.insort(self.saved_stickies, second_sticky)
				self.reddit.sticky_thread(thread_id)
			else:
				log.info("Saving for later sticky")
				bisect.insort(self.saved_stickies, new_sticky)

	def unsticky(self, thread_id):
		self.update_current_stickies()
		for current_sticky in self.current_stickies:
			if current_sticky is not None and current_sticky.thread_id == thread_id:
				self.reddit.unsticky_thread(thread_id)
				if len(self.saved_stickies) > 0:
					re_sticky = self.saved_stickies.pop()
					self.reddit.sticky_thread(re_sticky.thread_id)
					break
