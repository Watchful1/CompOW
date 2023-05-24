import discord_logging
import logging.handlers

log = discord_logging.init_logging(add_trace=True)

import liquipedia_parser
from reddit_class import Reddit


if __name__ == "__main__":
	discord_logging.set_level(logging.TRACE)
	event_wiki = "events/overwatch-contenders-2023-summer-series-asia-pacific"

	reddit = Reddit("OWMatchThreads", "competitiveoverwatch")
	event = reddit.get_event_from_page(event_wiki)
	liquipedia_parser.update_event(event)
	log.info(f"{event}")

	reddit.update_page_from_event(event)

	log.info(f"Page updated at https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}")
