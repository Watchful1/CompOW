import pytz
import math
import re

import static
from classes.enums import GameState
from classes.enums import Winner
from classes.enums import DiscordType


def render_append_highlights(current_body, link, flairs):
	if not re.findall(r'(>-$)', current_body):
		return None

	bldr = [current_body]

	bldr.append("\n")
	bldr.append("|Highlights|")
	bldr.append("\n")
	bldr.append("|-|")
	bldr.append("\n")
	bldr.append("|")
	bldr.append(flairs.get_flair("YouTube"))
	bldr.append("[Akshon Esports Highlights](")
	bldr.append(link)
	bldr.append(")|")

	return ''.join(bldr)


def render_reddit_post_match(match, flairs):
	bldr = []

	bldr.append(">#**")
	bldr.append(match.competition)
	bldr.append("**\n")
	bldr.append(">####")

	bldr.append("\n>\n")

	bldr.append(">---\n")
	bldr.append("|Team 1| |Score| |Team 2|\n")
	bldr.append("|-:|-|:-:|-|:-|\n")

	bldr.append("|")
	bldr.append(match.home.name)
	bldr.append("|")
	bldr.append(flairs.get_flair(match.home.name))
	bldr.append("|")
	bldr.append(str(match.home_score))
	bldr.append("-")
	bldr.append(str(match.away_score))
	bldr.append("|")
	bldr.append(flairs.get_flair(match.away.name))
	bldr.append("|")
	bldr.append(match.away.name)
	bldr.append("|")
	bldr.append("\n")

	for map_obj in match.maps:
		bldr.append("|")
		if map_obj.winner == Winner.HOME:
			bldr.append("Winner")
		elif map_obj.winner == Winner.TIED:
			bldr.append("TIED")
		bldr.append("||")
		bldr.append(map_obj.name)
		bldr.append("||")
		if map_obj.winner == Winner.AWAY:
			bldr.append("Winner")
		elif map_obj.winner == Winner.TIED:
			bldr.append("TIED")
		bldr.append("|\n")

	if match.vod is not None:
		bldr.append(">\n")
		bldr.append("|VOD|")
		bldr.append("\n")
		bldr.append("|-|")
		bldr.append("\n")
		bldr.append("|")
		bldr.append(flairs.get_flair("Twitch"))
		bldr.append("[VOD](")
		bldr.append(match.vod)
		bldr.append(")|")

	bldr.append(">-")

	return ''.join(bldr)


def render_reddit_post_match_title(match):
	return f"{match.home.name} vs {match.away.name} | {match.competition} | {match.stage} | Post-Match Discussion"


def render_reddit_post_match_comment(match):
	return f"Post match thread: [{match.home} vs {match.away}]({thread_link(static.SUBREDDIT, match.post_thread)})."


def thread_link(subreddit, thread_id):
	return f"https://www.reddit.com/r/{subreddit}/comments/{thread_id}/"


def render_reddit_event(event, flairs):
	bldr = []

	bldr.append("> ## **")
	bldr.append(event.competition.name)
	bldr.append("**\n")

	bldr.append(">####")
	bldr.append(event.stages_name())

	bldr.append("\n>\n")

	bldr.append(">> *Streams*  \n")
	streamBldr = []
	for stream in event.streams:
		streamInner = []
		if "twitch.tv" in stream.url:
			streamInner.append(flairs.get_flair("Twitch"))
		streamInner.append("[")
		streamInner.append(stream.name)
		streamInner.append("](")
		streamInner.append(stream.url)
		streamInner.append(")")
		streamBldr.append(''.join(streamInner))

	bldr.append('  \n'.join(streamBldr))
	bldr.append('  \n')
	bldr.append('[Reddit-stream](')
	if event.thread is not None:
		bldr.append('https://reddit-stream.com/comments/')
		bldr.append(event.thread)
	else:
		bldr.append('https://reddit-stream.com/comments/auto')
	bldr.append(')')

	bldr.append("\n>\n")

	bldr.append(">> *Tournament*  \n")
	bldr.append(flairs.get_flair("over.gg"))
	bldr.append("[")
	bldr.append(event.competition.name)
	bldr.append("](")
	bldr.append(event.competition_url)
	bldr.append(")")

	bldr.append("\n>\n")

	if event.is_owl():
		bldr.append(">> *Predictions*  \n")
		bldr.append("[Predictions Website](")
		bldr.append(static.PREDICTION_URL)
		bldr.append(")")
		bldr.append("\n>\n")

	bldr.append(">---\n")
	bldr.append(">---\n")
	bldr.append(">\n")
	bldr.append(">####Schedule\n")
	bldr.append(">\n")
	bldr.append(">>| |  |   |   |   |  | |   |\n")
	bldr.append(">>|-|-:|:-:|:-:|:-:|:-|-|:-:|\n")
	bldr.append(">>|Time|Team 1||||Team 2||Match Page|\n")
	for match in event.matches:
		bldr.append(">>|")

		bldr.append("[")
		bldr.append(match.start.strftime("%H:%M"))
		bldr.append("](")
		bldr.append("http://www.thetimezoneconverter.com/?t=")
		bldr.append(match.start.strftime("%H:%M"))
		bldr.append("&tz=UTC)")
		bldr.append("|")

		bldr.append(match.home.name)
		bldr.append("|")

		bldr.append(flairs.get_flair(match.home.name))
		bldr.append("|")

		if match.state != GameState.PENDING:
			bldr.append(">!")
			bldr.append(str(match.home_score))
			bldr.append("-")
			bldr.append(str(match.away_score))
			bldr.append("!<")

		bldr.append("|")

		bldr.append(flairs.get_flair(match.away.name))
		bldr.append("|")

		bldr.append(match.away.name)
		bldr.append("|")
		bldr.append("|")

		bldr.append(flairs.get_flair("over.gg"))
		bldr.append(" - [Match](")
		bldr.append(match.url)
		bldr.append(")")

		if event.competition.post_match_threads and match.post_thread is not None:
			bldr.append(" [Post Match](")
			bldr.append(thread_link(static.SUBREDDIT, match.post_thread))
			bldr.append(")")

		if match.vod is not None:
			bldr.append(" [VOD](")
			bldr.append(match.vod)
			bldr.append(")")

		bldr.append("|")
		bldr.append("\n")

	return ''.join(bldr)


def render_reddit_event_title(event):
	bldr = []
	bldr.append(event.competition.name)
	bldr.append(" - ")
	bldr.append(event.stages_name())
	return ''.join(bldr)


def get_discord_flair(flairs, name, country, discord_type):
	flair = flairs.get_static_flair(name, discord_type)
	if flair is not None:
		return f"{flair} "
	else:
		if country != "TBD":
			return f":flag_{country.lower()}:"
		else:
			return ""


def render_discord(event, flairs, discord_notification):
	bldr = []

	if discord_notification.type == DiscordType.COW:
		bldr.append("~ping ")

		bldr.append("**")
		bldr.append(event.competition.name)
		bldr.append(" - ")
		bldr.append(event.stages_name())
		bldr.append("**")

		minutes_difference = math.ceil((event.start - static.utcnow()).seconds / 60)
		if 60 > minutes_difference > 0:
			bldr.append(" begins in ")
			bldr.append(str(minutes_difference))
			bldr.append(" minutes!")
		else:
			bldr.append(" begins soon!")

		bldr.append("\n")

		notifications = []
		notifications.append("[All-Notify]")
		notifications.append("[All-Matches]")
		for role in discord_notification.roles:
			notifications.append(f"[{role}]")

		bldr.append(' '.join(notifications))

		bldr.append("\n\n")

		for i, match in enumerate(event.matches):
			bldr.append("**__Match ")
			bldr.append(str(i + 1))
			bldr.append("__** - *")

			timezones = [
				pytz.timezone("US/Pacific"),
				pytz.timezone("US/Eastern"),
				pytz.timezone("Europe/Paris"),
				pytz.timezone("Australia/Sydney"),
			]
			match_time = pytz.utc.localize(match.start)

			time_names = []
			for timezone in timezones:
				time_names.append(match_time.astimezone(timezone).strftime("%I:%M %p %Z"))

			bldr.append(' / '.join(time_names))

			bldr.append("*\n")

			bldr.append(get_discord_flair(flairs, match.home.name, match.home.country, discord_notification.type))

			bldr.append(" **")
			bldr.append(match.home.name)
			bldr.append("**")

			bldr.append(" vs ")

			bldr.append("**")
			bldr.append(match.away.name)
			bldr.append("** ")

			bldr.append(get_discord_flair(flairs, match.away.name, match.away.country, discord_notification.type))

			bldr.append("\n\n")

		bldr.append(":tv:")
		bldr.append("<")
		bldr.append(event.streams[0].url)
		bldr.append(">\n")

		bldr.append(":information_source:")
		bldr.append("<")
		bldr.append(event.competition_url)
		bldr.append(">\n")

		bldr.append(":keyboard:")
		bldr.append("Discuss in <#")
		bldr.append(discord_notification.channel)
		bldr.append(">")
		if event.thread is not None:
			bldr.append(" or in this thread: ")
			bldr.append("<https://redd.it/")
			bldr.append(event.thread)
			bldr.append(">")

	elif discord_notification.type == DiscordType.THEOW:
		bldr.append("**")
		bldr.append(event.competition.name)
		bldr.append("**")

		minutes_difference = math.ceil((event.start - static.utcnow()).seconds / 60)
		if 60 > minutes_difference > 0:
			bldr.append(" is going live in ")
			bldr.append(str(minutes_difference))
			bldr.append(" minutes! ")
		else:
			bldr.append(" begins soon! ")

		notifications = []
		for role in discord_notification.roles:
			notifications.append(f"@{role}")

		bldr.append(' '.join(notifications))

		bldr.append("\n\n")

		bldr.append("__")
		bldr.append(event.stages_name())
		bldr.append("__")

		bldr.append("\n")

		for i, match in enumerate(event.matches):
			bldr.append(get_discord_flair(flairs, match.home.name, match.home.country, discord_notification.type))

			bldr.append(" **")
			bldr.append(match.home.name)
			bldr.append("**")

			bldr.append(" vs ")

			bldr.append("**")
			bldr.append(match.away.name)
			bldr.append("** ")

			bldr.append(get_discord_flair(flairs, match.away.name, match.away.country, discord_notification.type))

			bldr.append("\n")

		bldr.append("\n")

		bldr.append(":tv:")
		bldr.append("<")
		bldr.append(event.streams[0].url)
		bldr.append(">\n")

	return ''.join(bldr)


def render_reddit_prediction_thread_title(event):
	bldr = []
	bldr.append("OWL Predictions Thread - ")
	bldr.append(event.stages_name())
	return ''.join(bldr)


def render_reddit_prediction_thread(events, flairs):
	bldr = []

	bldr.append("How do you think this weekend's games will play out? You can leave a comment below and also visit our ")
	bldr.append("[Predictions Website](")
	bldr.append(static.PREDICTION_URL)
	bldr.append(") to make your predictions.\n\n")

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

	bldr.append("\n\n")

	bldr.append("#Predictions\n")
	bldr.append("* Head to [our predictions website](")
	bldr.append(static.PREDICTION_URL)
	bldr.append(")\n")
	bldr.append("* Authenticate your Reddit account\n")
	bldr.append("* Submit your predictions\n\n")

	return ''.join(bldr)
