from typing import List
from dataclasses import dataclass, field
import discord_logging

log = discord_logging.get_logger()

from classes.settings import DirtyMixin


@dataclass
class Team(DirtyMixin):
	name: str = None
	score: int = None

	def set_score(self, score):
		if score is not None:
			if score.lower() == "w":
				self.score = 3
			elif score.lower() == "l":
				self.score = 0
			else:
				self.score = int(score)

	def get_name(self):
		if self.name is None:
			return "TBD"
		return self.name

	def __eq__(self, other):
		if not isinstance(other, Team):
			return False
		return self.name == other.name and self.score == other.score

	def __str__(self):
		return f"{self.name}: {self.score}"
