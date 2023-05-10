import discord_logging

log = discord_logging.init_logging(debug=True)

from reddit_class import Reddit
from classes.settings import Settings

if __name__ == "__main__":
	reddit = Reddit("OWMatchThreads", "CompetitiveOverwatch")

	events = []
	for event_page in reddit.list_event_pages():
		event = reddit.get_event_from_page(event_page)
		events.append(event)


