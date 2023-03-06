import discord_logging

log = discord_logging.init_logging()

import liquipedia_parser
from classes import Event
from reddit_class import Reddit


if __name__ == "__main__":
	page_url = "https://liquipedia.net/overwatch/Overwatch_League/Season_6/Pro-Am/Qualifier/North_America"

	event = Event(page_url)
	liquipedia_parser.update_event(event)
	event.log()

	reddit = Reddit("OWMatchThreads")
	reddit.create_page_from_event("competitiveoverwatch", event)

	log.info(f"Page created at https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}")
