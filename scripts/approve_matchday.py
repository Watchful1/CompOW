import discord_logging

log = discord_logging.init_logging()

import liquipedia_parser
from classes import Event
from reddit_class import Reddit


if __name__ == "__main__":
	event_wiki = "events/overwatch-league-2023---pro-am-group-stage"

	reddit = Reddit("OWMatchThreads", "competitiveoverwatch")
	event = reddit.get_event_from_page(event_wiki)

	log.info(f"{event}")

	source_id = "h9wgg"

	for match_day in event.match_days:
		if match_day.id == source_id:
			match_day.approve_all_games()

	reddit.update_page_from_event(event)

