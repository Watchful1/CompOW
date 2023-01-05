import discord_logging
import praw
import jsons

log = discord_logging.init_logging()

import liquipedia_parser
from classes import Team, Game, MatchDay, Event


if __name__ == "__main__":
	#page_url = "https://liquipedia.net/overwatch/Calling_All_Heroes/Challengers_Cup"
	page_url = "https://liquipedia.net/overwatch/Overwatch_Contenders/2022/Run_It_Back/North_America"
	#page_url = "https://liquipedia.net/dota2/Dota_Pro_Circuit/2023/1/North_America/Open_Qualifier/4"
	#page_url = "https://liquipedia.net/overwatch/Overwatch_League/Season_5/Regular_Season/Kickoff_Clash"
	#page_url = "https://liquipedia.net/overwatch/ESET_Runback_Series"

	event = Event(page_url)
	games, event_name, streams = liquipedia_parser.parse_event(event.url)

	if event.name is not None and event_name != event.name:
		log.warning(f"Event name changed from `{event.name}` to `{event_name}`")
	event.name = event_name

	changed = False
	if len(event.streams) != 0:
		if len(event.streams) != len(streams):
			changed = True
		else:
			for i in range(len(streams)):
				if event.streams[i] != streams[i]:
					changed = True
	if changed:
		log.warning(f"Event {event.name} streams changed from `{'`, `'.join(event.streams)}` to `{'`, `'.join(streams)}`")
	event.streams = streams

	for game in games:
		event.add_game(game)

	log.info(event.name)
	for stream in event.streams:
		log.info(stream)
	log.info("")

	for match_day in event.match_days:
		log.info(match_day)
		for game in match_day.pending_games:
			log.info(game)
		log.info("")

	# reddit = praw.Reddit("OWMatchThreads")
	#
	# log.info(f"Fetching wiki page {event.wiki_name()}")
	# # event_wiki = reddit.subreddit("competitiveoverwatch").wiki.create(
	# # 	name=event.wiki_name(),
	# # 	content=event.name,
	# # 	reason="Creating page for event"
	# # )
	# event_wiki = reddit.subreddit("competitiveoverwatch").wiki[event.wiki_name()]
	#
	# bldr = ["##", event.name, "\n\n"]
	# for match_day in event.match_days:
	# 	bldr.append("###")
	# 	bldr.append(str(match_day))
	# 	bldr.append("\n\n")
	# 	bldr.append(f"Approved | Pending\n---|---\n")
	# 	i = 0
	# 	while True:
	# 		if i < len(match_day.approved_games):
	# 			bldr.append(str(match_day.approved_games[i]))
	# 		bldr.append(" | ")
	# 		if i < len(match_day.pending_games):
	# 			bldr.append(str(match_day.pending_games[i]))
	# 		bldr.append("\n")
	# 		i += 1
	# 		if i >= len(match_day.approved_games) and i >= len(match_day.pending_games):
	# 			break
	#
	# 	bldr.append("\n\n")
	#
	# event_string = str(jsons.dump(event))
	#
	# bldr.append("[](#datatag")
	# bldr.append(event_string)
	# bldr.append(")")
	#
	# event_wiki.edit(content=''.join(bldr))
