import pytz
import math
import re
import discord_logging
import jsons
import urllib.parse

log = discord_logging.get_logger()

import utils
from classes.event import Event
from classes.settings import Settings


cow_roles = {
	'OWCSNotify': '<@&481314680665538569>',
	'OWCSAPAC': '<@&481315112993554433>',
	'OWCSNA': '<@&481315228529721344>',
	'OWCSEU': '<@&481315364345479169>',
	'OWCSCN': '<@&481315825802936320>',
	# 'Game-News': '<@&517000502924279808>',
	# 'Community-News': '<@&517000366735228929>',
	'OWWC': '<@&481316090270711820>',
	'All-Matches': '<@&517000657111220229>',
	'All-Notify': '<@&481316252661579786>',
	'here': '@here',
	'everyone': '@everyone'
}
cow_channels = {
	'match-discussion': '377127072243515393',
	'ow-esports': '420968531929071628',
}


def html_encode(message):
	return urllib.parse.quote(message, safe='')


def build_message_link(recipient, subject, content=None):
	base = "https://www.reddit.com/message/compose/?"
	bldr = []
	bldr.append(f"to={recipient}")
	bldr.append(f"subject={html_encode(subject)}")
	if content is not None:
		bldr.append(f"message={html_encode(content)}")

	return base + '&'.join(bldr)


def make_time_string(date_time):
	current_time = utils.utcnow()
	if current_time > date_time:
		return '**LIVE**'
	time_diff = (date_time - current_time).total_seconds()

	m, s = divmod(time_diff, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)

	if d > 99:
		return ">99d"
	elif d > 0:
		return str(int(d)) + 'd'
	elif h > 0:
		return str(int(h)) + 'h'
	else:
		return str(int(m)) + 'm'


def render_event_wiki(event, username):
	bldr = ["##[", event.name, "](", event.url, ") : ", event.id, "\n\n"]

	settings_fields = [
		f"post_match_threads:{event.post_match_threads}",
		f"match_thread_minutes_before:{event.match_thread_minutes_before}",
		f"leave_thread_minutes_after:{event.leave_thread_minutes_after}",
		f"use_pending_changes:{event.use_pending_changes}",
		f"discord_key:{event.discord_key}",
		f"discord_minutes_before:{event.discord_minutes_before}",
		f"discord_roles:{','.join(event.discord_roles)}",
		f"name:{(event.name.replace(':', '?') if event.name else event.name)}",
	]

	bldr.append("Setting | Value\n")
	bldr.append("---|---\n")
	bldr.append('\n'.join([field.replace(":", "|") for field in settings_fields]))
	bldr.append("\n\n")

	bldr.append("[Update settings](")
	bldr.append(build_message_link(
		username,
		f"{event.id}:update settings",
		'\n'.join([f"settings:{field}" for field in settings_fields])
	))
	bldr.append(") : [Delete event](")
	bldr.append(build_message_link(
		username,
		f"{event.id}:delete event",
		f"deleteevent"
	))
	bldr.append(") : [Approve all matches](")
	bldr.append(build_message_link(
		username,
		f"{event.id}:approve event",
		f"approveevent"
	))
	bldr.append(") : [Re-render wiki](")
	bldr.append(build_message_link(
		username,
		f"{event.id}:render wiki",
		f"renderwiki"
	))
	bldr.append(")\n\n")
	bldr.append("Streams:\n\n")
	for stream in event.streams:
		bldr.append(stream)
		bldr.append("\n\n")
	for match_day in event.match_days:
		bldr.append("###")
		bldr.append(str(match_day))
		bldr.append("\n\n")
		if len(match_day.pending_games):
			bldr.append("[Approve matchday](")
			bldr.append(build_message_link(
				username,
				f"{event.id}:approve matchday",
				f"approveday:{match_day.id}"
			))
			bldr.append(") : ")
		if len(match_day.approved_games):
			bldr.append("[Delete matches](")
			bldr.append(build_message_link(
				username,
				f"{event.id}:delete matchday",
				f"deleteday:{match_day.id}"
			))
			bldr.append(") : ")
		if not match_day.is_complete():
			bldr.append(f"[{('Disable' if match_day.spoiler_prevention else 'Enable')} spoilers](")
			bldr.append(build_message_link(
				username,
				f"{event.id}:enable spoilers",
				f"enablespoilers:{match_day.id}:{not match_day.spoiler_prevention}"
			))
			bldr.append(")\n\n")
		bldr.append("\n\n")
		bldr.append(f"Approved | Pending\n---|---\n")
		i = 0
		while True:
			if i < len(match_day.approved_games):
				bldr.append(str(match_day.approved_games[i]))
				bldr.append(" [del](")
				bldr.append(build_message_link(
					username,
					f"{event.id}:delete match",
					f"deletematch:{match_day.approved_games[i].id}"
				))
				bldr.append(")")
			bldr.append(" | ")
			if i < len(match_day.pending_games):
				bldr.append(str(match_day.pending_games[i]))

				bldr.append(" [app](")
				bldr.append(build_message_link(
					username,
					f"{event.id}:approve match",
					f"approvematch:{match_day.pending_games[i].id}:none"
				))
				bldr.append(")")
			bldr.append("\n")
			i += 1
			if i >= len(match_day.approved_games) and i >= len(match_day.pending_games):
				break

		bldr.append("\n\n")

	event_string = str(jsons.dumps(event, cls=Event, strip_nulls=True))

	bldr.append("[](#datatag")
	bldr.append(event_string)
	bldr.append(")")

	return ''.join(bldr)


def render_settings_wiki(settings, username, events):
	bldr = []
	bldr.append("[Add event](")
	bldr.append(build_message_link(
		username,
		f"add event",
		f"addevent "
	))
	bldr.append(") : **[Kill bot](")
	bldr.append(build_message_link(
		username,
		f"kill",
		f"kill"
	))
	bldr.append(")**")

	bldr.append("\n\n")
	bldr.append("|".join(cow_roles.keys()))

	bldr.append("\n\n")

	bldr.append("Event | Next approved match | Next pending match\n")
	bldr.append("---|---|---\n")
	for event in events:
		bldr.append("[")
		bldr.append(event.name)
		bldr.append("](https://www.reddit.com/r/Competitiveoverwatch/wiki/")
		bldr.append(event.wiki_name())
		bldr.append(")|")
		next_approved_game = event.get_next_game(approved=True)
		if next_approved_game is not None:
			bldr.append(str(next_approved_game.date_time))
			bldr.append(" (")
			bldr.append(make_time_string(next_approved_game.date_time))
			bldr.append(")")
		else:
			bldr.append("No approved matches")
		bldr.append("|")
		next_pending_game = event.get_next_game(approved=False, pending=True, complete=False)
		if next_pending_game is not None:
			bldr.append(str(next_pending_game.date_time))
			bldr.append(" (")
			bldr.append(make_time_string(next_pending_game.date_time))
			bldr.append(")")
		else:
			bldr.append("No pending matches")

		bldr.append("\n")

	bldr.append("\n")

	settings_string = str(jsons.dumps(settings, cls=Settings, strip_nulls=True))

	bldr.append("[](#datatag")
	bldr.append(settings_string)
	bldr.append(")")

	return ''.join(bldr)


def render_reddit_post_match(event, match_day, game, flairs):
	bldr = []

	bldr.append(">#**")
	bldr.append(event.name)
	bldr.append("**\n")
	bldr.append(">####")

	bldr.append("\n>\n")

	bldr.append(">---\n")
	bldr.append("|Team 1| |Score| |Team 2|\n")
	bldr.append("|-:|-|:-:|-|:-|\n")

	bldr.append("|")
	bldr.append(game.home.name)
	bldr.append("|")
	bldr.append(flairs.get_flair(game.home.name))
	bldr.append("|")
	bldr.append(str(game.home.score))
	bldr.append("-")
	bldr.append(str(game.away.score))
	bldr.append("|")
	bldr.append(flairs.get_flair(game.away.name))
	bldr.append("|")
	bldr.append(game.away.name)
	bldr.append("|")
	bldr.append("\n")

	# TODO parse and include maps in post game thread
	# for map_obj in match.maps:
	# 	bldr.append("|")
	# 	if map_obj.winner == Winner.HOME:
	# 		bldr.append("Winner")
	# 	elif map_obj.winner == Winner.TIED:
	# 		bldr.append("TIED")
	# 	bldr.append("||")
	# 	bldr.append(map_obj.name)
	# 	bldr.append("||")
	# 	if map_obj.winner == Winner.AWAY:
	# 		bldr.append("Winner")
	# 	elif map_obj.winner == Winner.TIED:
	# 		bldr.append("TIED")
	# 	bldr.append("|\n")

	# TODO parse and include vod in post game thread
	# if match.vod is not None:
	# 	bldr.append(">\n")
	# 	bldr.append("|VOD|")
	# 	bldr.append("\n")
	# 	bldr.append("|-|")
	# 	bldr.append("\n")
	# 	bldr.append("|")
	# 	bldr.append(flairs.get_flair("Twitch"))
	# 	bldr.append("[VOD](")
	# 	bldr.append(match.vod)
	# 	bldr.append(")|")

	bldr.append(">-")

	return ''.join(bldr)


def render_reddit_post_match_title(event, match_day, game, spoilers=False, match_num=None):
	if spoilers:
		if match_num is not None:
			return f"{event.name} | Match {match_num} | Post-Match Discussion"
		else:
			return f"{event.name} | Post-Match Discussion"
	else:
		return f"{game.home.name} vs {game.away.name} | {event.name} | Post-Match Discussion"


def render_reddit_post_match_comment(game, subreddit):
	return f"Post match thread: [{game.home.name} vs {game.away.name}]({thread_link(subreddit, game.post_thread_id)})."


def thread_link(subreddit, thread_id):
	return f"https://www.reddit.com/r/{subreddit}/comments/{thread_id}/"


def render_reddit_event(match_day, event, flairs, subreddit, username):
	bldr = []

	bldr.append("> ## **")
	bldr.append(event.name)
	bldr.append("**\n")

	bldr.append(">####")
	# TODO
	bldr.append("_")

	bldr.append("\n>\n")

	bldr.append(">> *Streams*  \n")
	streamBldr = []
	for stream in event.streams:
		streamInner = []
		# TODO
		# if "twitch.tv" in stream:
		# 	streamInner.append(flairs.get_flair("Twitch"))
		streamInner.append("[")
		streamInner.append(stream)
		streamInner.append("](")
		streamInner.append(stream)
		streamInner.append(")")
		streamBldr.append(''.join(streamInner))

	bldr.append('  \n'.join(streamBldr))
	bldr.append('  \n')
	bldr.append('[Reddit-stream](')
	if match_day.thread_id is not None:
		bldr.append('https://reddit-stream.com/comments/')
		bldr.append(match_day.thread_id)
	else:
		bldr.append('https://reddit-stream.com/comments/auto')
	bldr.append(')')

	bldr.append("\n>\n")

	# bldr.append(">> *Tournament*  \n")
	# bldr.append(flairs.get_flair("over.gg"))
	# bldr.append("[")
	# bldr.append(event.competition.name)
	# bldr.append("](")
	# bldr.append(event.competition_url)
	# bldr.append(")")

	bldr.append("\n>\n")

	bldr.append(">---\n")
	bldr.append(">---\n")
	bldr.append(">\n")
	bldr.append(">####Schedule\n")
	bldr.append(">\n")
	bldr.append(">>| |  |   |   |   |  | |   |\n")
	bldr.append(">>|-|-:|:-:|:-:|:-:|:-|-|:-:|\n")
	bldr.append(">>|Time|Team 1||||Team 2||Match Page|\n")
	for game in match_day.approved_games:
		bldr.append(">>|")

		bldr.append("[")
		bldr.append(game.date_time.strftime("%H:%M"))
		bldr.append("](")
		bldr.append("http://www.thetimezoneconverter.com/?t=")
		bldr.append(game.date_time.strftime("%H:%M"))
		bldr.append("&tz=UTC)")
		bldr.append("|")

		bldr.append(game.home.get_name())
		bldr.append("|")

		bldr.append(flairs.get_flair(game.home.name))
		bldr.append("|")

		if game.home.score or game.away.score:
			bldr.append(">!")
			bldr.append(str(game.home.score))
			bldr.append("-")
			bldr.append(str(game.away.score))
			bldr.append("!<")

		bldr.append("|")

		bldr.append(flairs.get_flair(game.away.name))
		bldr.append("|")

		bldr.append(game.away.get_name())
		bldr.append("||")
		if game.post_thread_id is not None:
			bldr.append("[Post Match](")
			bldr.append(thread_link(subreddit, game.post_thread_id))
			bldr.append(")")

		# if game.vod is not None:
		# 	bldr.append(" [VOD](")
		# 	bldr.append(match.vod)
		# 	bldr.append(")")

		bldr.append("|")
		bldr.append("\n")

	if event.post_match_threads:
		link = build_message_link(
			username,
			f"{event.id}:enable spoilers",
			f"enablespoilers:{match_day.id}:{not match_day.spoiler_prevention}"
		)
		bldr.append(")\n\n")
		if match_day.spoiler_prevention:
			bldr.append(f"Teams will be SHOWN in post match thread titles. If this is wrong, ping an active moderator and they can ")
			bldr.append(f"[click here to hide them]({link}).\n\n")
		else:
			bldr.append(f"Teams will be HIDDEN in post match thread titles. If this is wrong, ping an active moderator and they can ")
			bldr.append(f"[click here to show them]({link}).\n\n")

	bldr.append(f"\nThis thread pulls match data from [this liquipedia page]({event.url}). If the thread is out of data, you can help ")
	bldr.append(f"by updating that page. If something is wrong or missing please ping u/Watchful1 in the comments.")

	return ''.join(bldr)


def render_reddit_event_title(event):
	bldr = []
	bldr.append(event.name)
	# TODO add matchday name
	return ''.join(bldr)


def get_discord_flair(flairs, name, country):
	flair = flairs.get_static_flair(name)
	if flair is not None:
		return f"{flair} "
	else:
		if country != "TBD":
			return f":flag_{country.lower()}:"
		else:
			return ""


def render_discord(event, match_day, flairs, short=False):
	bldr = []
	bldr.append("**")
	bldr.append(event.name)
	#TODO bldr.append(event.stages_name())
	bldr.append("**")

	minutes_difference = math.ceil((match_day.approved_start_datetime - utils.utcnow()).seconds / 60)
	if 60 > minutes_difference > 0:
		bldr.append(" begins in ")
		bldr.append(str(minutes_difference))
		bldr.append(" minutes!")
	else:
		bldr.append(" begins soon!")

	bldr.append("\n")

	notifications = []
	for role in event.discord_roles:
		if role in cow_roles:
			notifications.append(cow_roles[role])
		else:
			log.warning(f"Role not in dict: {role}")
	bldr.append(' '.join(notifications))

	bldr.append("\n\n")

	for i, game in enumerate(match_day.approved_games):
		if short:
			bldr.append("*<t:")
			bldr.append(str(int(game.date_time.timestamp())))
			bldr.append(":f>* ")

			bldr.append(get_discord_flair(flairs, game.home.name, "TBD"))

			bldr.append(" **")
			bldr.append(game.home.name)
			bldr.append("**")

			bldr.append(" vs ")

			bldr.append("**")
			bldr.append(game.away.name)
			bldr.append("** ")

			bldr.append(get_discord_flair(flairs, game.away.name, "TBD"))

			bldr.append("\n")
		else:
			bldr.append("**__Match ")
			bldr.append(str(i + 1))
			bldr.append("__** - <t:")
			game_timestamp = str(int(game.date_time.timestamp()))
			bldr.append(game_timestamp)
			bldr.append(":f> - <t:")
			bldr.append(game_timestamp)
			bldr.append(":R>\n")

			bldr.append(get_discord_flair(flairs, game.home.name, "TBD"))
			bldr.append(" **")
			bldr.append(game.home.get_name())
			bldr.append("**")

			bldr.append(" vs ")

			bldr.append("**")
			bldr.append(game.away.get_name())
			bldr.append("** ")
			bldr.append(get_discord_flair(flairs, game.away.name, "TBD"))

			bldr.append("\n\n")

	bldr.append(":tv:")
	bldr.append("<")
	bldr.append(event.streams[0])
	bldr.append(">\n")

	# bldr.append(":information_source:")
	# bldr.append("<")
	# bldr.append(event.competition_url)
	# bldr.append(">\n")

	bldr.append(":keyboard:")
	bldr.append("Discuss in <#")
	bldr.append(cow_channels['match-discussion'])
	bldr.append(">")
	if match_day.thread_id is not None:
		bldr.append(" or in this thread: ")
		bldr.append("<https://redd.it/")
		bldr.append(match_day.thread_id)
		bldr.append(">")

	result_str = ''.join(bldr)
	if len(result_str) > 2000:
		if short:
			log.warning(f"Discord notification length too long {len(result_str)}")
			return None
		return render_discord(event, match_day, flairs, short=True)

	return result_str


def render_reddit_prediction_thread_title(event):
	bldr = []
	bldr.append("OWL Predictions Thread - ")
	bldr.append(event.stages_name())
	return ''.join(bldr)


def render_reddit_prediction_thread(events, flairs):
	bldr = []

	bldr.append("How do you think this weekend's games will play out? You can leave a comment below and [join our Pick'Ems leaderboard here](")
	bldr.append(utils.PREDICTION_URL)
	bldr.append(") by clicking ""Join a leaderboard"" and putting in the code `reddit-cow`. We will have prizes after each week of games.\n\n")

	for event in events:
		for match in event.matches:
			bldr.append(match.home.name)
			bldr.append(" ")
			bldr.append(flairs.get_flair(match.home.name))
			bldr.append(" vs ")
			bldr.append(flairs.get_flair(match.away.name))
			bldr.append(" ")
			bldr.append(match.away.name)

			bldr.append("  \n")

	return ''.join(bldr)


def match_list_to_string(matches):
	order_str = []
	for match in matches:
		order_str.append(f"{match.home.name} vs {match.away.name}")
	return ', '.join(order_str)
