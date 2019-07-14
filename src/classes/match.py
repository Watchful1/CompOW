from classes.enums import GameState


class Match:
	def __init__(self, id, start, home, away, url):
		self.id = id
		self.start = start
		self.home = home
		self.away = away

		self.state = GameState.PENDING
		self.home_score = 0
		self.away_score = 0
		self.winner = None
		self.url = url
		self.streams = []
		self.competition = None
		self.competition_url = None
		self.stage = None

		self.post_thread = None

		self.dirty = False

	def __str__(self):
		return f"{self.home.name} vs {self.away.name} : {self.start}"

	def __lt__(self, other):
		return self.start < other.start

	def __eq__(self, other):
		return self.id == other.id
