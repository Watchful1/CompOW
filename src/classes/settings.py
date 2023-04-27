from typing import List
from dataclasses import dataclass, field
import discord_logging

log = discord_logging.get_logger()


@dataclass
class Dirtiable:
	_dirty: bool = False

	log = True

	def __setattr__(self, attr, value):
		if not attr.startswith("_") and \
				hasattr(self, attr) and \
				self.__getattribute__(attr) != value:
			super().__setattr__("_dirty", True)
			if Dirtiable.log:
				log.debug(f"dirty : {attr}:{value}")
		super().__setattr__(attr, value)


@dataclass
class Settings:
	stickies: List[str] = field(default_factory=list)

	# class var
	settings = None

	@classmethod
	def get_settings(cls, reddit):
		if cls.settings is None:
			cls.settings = reddit.get_settings()
		return cls.settings

	def save(self, reddit):
		reddit.save_settings(self)

	def __str__(self):
		return f"stickies: {(','.join(self.stickies) if self.stickies else 'None')}"
