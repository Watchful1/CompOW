import discord_logging

log = discord_logging.init_logging(debug=True)

from reddit_class import Reddit
from classes.settings import Settings

if __name__ == "__main__":
	reddit = Reddit("OWMatchThreads", "CompetitiveOverwatch")
	settings = reddit.get_settings()
	settings.stickies.append("test")
	reddit.save_settings(settings)
