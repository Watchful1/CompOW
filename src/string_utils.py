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
	return f"Post match thread [here]({thread_link(globals.SUBREDDIT, match.post_thread)})."


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

	bldr.append(">> *Streams:* ")
	streamBldr = []
	for stream in event.streams:
		streamInner = []
		if "twitch.tv" in stream.url:
			streamInner.append(flairs.get_flair("twitch"))
		streamInner.append("[")
		streamInner.append(stream.name)
		streamInner.append("](")
		streamInner.append(stream.url)
		streamInner.append(") ")
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

		bldr.append(flairs.get_flair("overgg"))
		bldr.append("[over.gg](")
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
