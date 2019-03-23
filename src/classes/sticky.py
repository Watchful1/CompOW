import mappings


class Sticky:
	def __init__(self, thread_id, competition=None, start=None):
		self.thread_id = thread_id
		self.competition = competition
		self.start = start

	def __str__(self):
		return f"{self.thread_id} : {self.competition} : {self.start}"

	def __lt__(self, other):
		if other is None:
			return False
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
