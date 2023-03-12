import discord_logging

log = discord_logging.init_logging()

import liquipedia_parser
from classes import Event
from reddit_class import Reddit


if __name__ == "__main__":
	event_wiki = "events/overwatch-league-2023---pro-am-north-america-qualifier"

	reddit = Reddit("OWMatchThreads")
	event = reddit.get_event_from_page("competitiveoverwatch", event_wiki)
	liquipedia_parser.update_event(event)
	log.info(f"{event}")

	reddit.update_page_from_event("competitiveoverwatch", event)

	log.info(f"Page updated at https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}")
