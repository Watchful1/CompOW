class Map:
	def __init__(self, name, winner):
		self.name = name
		self.winner = winner

	def __eq__(self, other):
		return self.name == other.name and self.winner == other.winner
