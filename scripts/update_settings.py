import discord_logging

log = discord_logging.init_logging()

import liquipedia_parser
from classes import Event
from reddit_class import Reddit


if __name__ == "__main__":
	event_wiki = "events/overwatch-league-2023---pro-am-group-stage"
	event_wiki2 = "events/overwatch-league-2023---pro-am"

	reddit = Reddit("OWMatchThreads", "competitiveoverwatch")
	event = reddit.get_event_from_page(event_wiki)
	event2 = reddit.get_event_from_page(event_wiki2)

	#liquipedia_parser.update_event(event)

	event2.match_thread_minutes_before = 60 * 2
	#event.details_url = "https://liquipedia.net/overwatch/Overwatch_League/Season_6/Pro-Am"
	event2.discord_key = "cow"
	event2.post_match_threads = True
	event2.use_pending_changes = True

	reddit.update_page_from_event(event2)
	log.info(f"Page updated at https://www.reddit.com/r/Competitiveoverwatch/wiki/{event2.wiki_name()}")
