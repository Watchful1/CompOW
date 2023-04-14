import discord_logging

log = discord_logging.init_logging()

import liquipedia_parser
from classes import Event
from reddit_class import Reddit


if __name__ == "__main__":
	event_wiki = "events/overwatch-league-2023---pro-am"

	reddit = Reddit("OWMatchThreads", "competitiveoverwatch")
	event = reddit.get_event_from_page(event_wiki)

	log.info(f"{event}")

	source_id = None#"c9rq0"
	target_id = None#"ov34a"
	delete_id = "pa69f"

	# if source_id is not None:
	# 	for match_day in event.match_days:
	# 		match_day.approve_game(source_id, target_id)

	if delete_id is not None:
		for match_day in event.match_days:
			match_day.delete_game(delete_id)

	reddit.update_page_from_event(event)
