import discord_logging

log = discord_logging.init_logging()

import liquipedia_parser
from classes import Event
from reddit_class import Reddit


if __name__ == "__main__":
	event_wiki = "events/overwatch-league-2023---pro-am-north-america-qualifier"

	reddit = Reddit("OWMatchThreads")
	event = reddit.get_event_from_page("competitiveoverwatch", event_wiki)

	log.info(f"{event}")

	source_id = "5m7lq"
	target_id = ""

	for match_day in event.match_days:
		match_day.approve_game(source_id)

	reddit.update_page_from_event("competitiveoverwatch", event)

