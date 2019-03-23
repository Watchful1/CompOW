class Team:
	def __init__(self, name, country):
		self.name = "TBD" if name is None else name
		self.country = "TBD" if country is None else country

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.__dict__ == other.__dict__
