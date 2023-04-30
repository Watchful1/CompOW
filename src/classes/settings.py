from typing import List, ClassVar
from dataclasses import dataclass, field
import discord_logging

log = discord_logging.get_logger()


@dataclass
class DirtyMixin:
	_dirty: bool = False

	log = True

	def __setattr__(self, attr, value):
		if not attr.startswith("_") and \
				hasattr(self, attr) and \
				self.__getattribute__(attr) != value:
			super().__setattr__("_dirty", True)
			if DirtyMixin.log:
				log.trace(f"dirty : {attr}:{value}")
		super().__setattr__(attr, value)


@dataclass
class Settings:
	stickies: List[str] = field(default_factory=list)

	def __str__(self):
		return f"stickies: {(','.join(self.stickies) if self.stickies else 'None')}"
