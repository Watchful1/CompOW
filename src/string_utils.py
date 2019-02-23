import pytz

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

	bldr.append(">> *Streams:*  \n")
	streamBldr = []
	for stream in event.streams:
		streamInner = []
		if "twitch.tv" in stream.url:
			streamInner.append(flairs.get_flair("Twitch"))
		streamInner.append("[")
		streamInner.append(stream.name)
		streamInner.append("](")
		streamInner.append(stream.url)
		streamInner.append(")  \n")
		streamBldr.append(''.join(streamInner))

	bldr.append(' | '.join(streamBldr))

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
	return f"{event.competition.name} - {event.stages_name()}"


def render_discord(event):
	bldr = []

	bldr.append("**")
	bldr.append(event.competition.name)
	bldr.append(" - ")
	bldr.append(event.stages_name())
	bldr.append("**")

	minutes_difference = int((event.start - globals.debug_time).seconds / 60)
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
	if event.competition.discord_role is not None:
		notifications.append(f"[{event.competition.discord_role}]")

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

		bldr.append("**")
		bldr.append(match.home.name)
		bldr.append("**")

		bldr.append(" vs ")

		bldr.append("**")
		bldr.append(match.away.name)
		bldr.append("**")

		bldr.append("\n\n")


	return ''.join(bldr)
