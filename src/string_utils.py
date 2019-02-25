import pytz
from datetime import datetime

import classes
import globals


def render_reddit_post_match(match, flairs):
	bldr = []

	bldr.append(">#**")
	bldr.append(match.competition)
	bldr.append("**\n")
	bldr.append(">####")

	bldr.append("\n>\n")

	bldr.append(">---\n")
	bldr.append(">|Team 1| |Score| |Team 2|\n")
	bldr.append(">|-:|-|:-:|-|:-|\n")

	bldr.append(">|")
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

	return ''.join(bldr)


def render_reddit_post_match_title(match):
	return f"{match.home.name} vs {match.away.name} | {match.competition} | {match.stage} | Post-Match Discussion"


def render_reddit_post_match_comment(match):
	return f"Post match thread: [{match.home} vs {match.away}]({thread_link(globals.SUBREDDIT, match.post_thread)})."


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

	bldr.append("\n>\n")

	bldr.append(">> *Tournament*  \n")
	bldr.append(flairs.get_flair("over.gg"))
	bldr.append("[")
	bldr.append(event.competition.name)
	bldr.append("](")
	bldr.append(event.competition_url)
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

		if match.state != classes.GameState.PENDING:
			bldr.append(str(match.home_score))
			bldr.append("-")
			bldr.append(str(match.away_score))

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
			bldr.append(thread_link(globals.SUBREDDIT, match.post_thread))
			bldr.append(")")

		bldr.append("|")
		bldr.append("\n")

	return ''.join(bldr)


def render_reddit_event_title(event):
	bldr = []
	bldr.append(event.competition.name)
	bldr.append(" - ")
	bldr.append(event.stages_name())
	if event.competition.day_in_title:
		bldr.append(" - ")
		bldr.append(event.start.astimezone(pytz.timezone('US/Pacific')).strftime('%A'))
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


def render_discord(event, flairs):
	bldr = []

	bldr.append("~ping ")

	bldr.append("**")
	bldr.append(event.competition.name)
	bldr.append(" - ")
	bldr.append(event.stages_name())
	bldr.append("**")

	minutes_difference = int((event.start - datetime.utcnow()).seconds / 60)
	if minutes_difference < 60:
		bldr.append(" begins in ")
		bldr.append(str(minutes_difference))
		bldr.append(" minutes!")
	else:
		bldr.append(" begins soon!")

	bldr.append("\n")

	notifications = []
	notifications.append("[All-Notify]")
	notifications.append("[All-Matches]")
	if len(event.competition.discord_roles):
		for role in event.competition.discord_roles:
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
		]
		match_time = pytz.utc.localize(match.start)

		time_names = []
		for timezone in timezones:
			time_names.append(match_time.astimezone(timezone).strftime("%I:%M %p %Z"))

		bldr.append(' / '.join(time_names))

		bldr.append("*\n")

		bldr.append(get_discord_flair(flairs, match.home.name, match.home.country))

		bldr.append("**")
		bldr.append(match.home.name)
		bldr.append("**")

		bldr.append(" vs ")

		bldr.append("**")
		bldr.append(match.away.name)
		bldr.append("**")

		bldr.append(get_discord_flair(flairs, match.away.name, match.away.country))

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
	bldr.append(event.competition.discord_channel)
	bldr.append(">")
	if event.thread is not None:
		bldr.append(" or in this thread: ")
		bldr.append("<https://redd.it/")
		bldr.append(event.thread)
		bldr.append(">")

	return ''.join(bldr)
