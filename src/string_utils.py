import classes
import mappings


def render_reddit_stage(stage):
	bldr = []


def render_reddit_post_match(match):
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
	bldr.append("||")
	bldr.append(str(match.home_score))
	bldr.append("-")
	bldr.append(str(match.away_score))
	bldr.append("||")
	bldr.append(match.away.name)
	bldr.append("|")



	return ''.join(bldr)


def render_reddit_post_match_title(match):
	return f"{match.home.name} vs {match.away.name} | {match.competition} | {match.stage} | Post-Match Discussion"


def render_reddit_event(event):
	bldr = []

	bldr.append("> ## **")
	bldr.append(event.competition.name)
	bldr.append("**\n")

	bldr.append(">####")
	bldr.append(event.stage_names())

	bldr.append("\n>\n")

	bldr.append(">> *Streams:* ")
	for stream in event.streams():
		bldr.append("[")
		bldr.append(stream.name)
		bldr.append("](")
		bldr.append(stream.url)
		bldr.append(") ")

	bldr.append("\n>\n")

	bldr.append(">---\n")
	bldr.append(">---\n")
	bldr.append(">\n")
	bldr.append(">####Schedule\n")
	bldr.append(">\n")
	bldr.append(">>| |  |   |   |   |  | |   |\n")
	bldr.append(">>|-|-:|:-:|:-:|:-:|:-|-|:-:|\n")
	bldr.append(">>|Time|Team 1||||Team 2||Match Page|\n")
	for stage in event.stages:
		for match in stage.matches:
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

			bldr.append(mappings.get_flair(match.home.name))
			bldr.append("|")

			bldr.append(str(match.home_score))
			bldr.append("-")
			bldr.append(str(match.away_score))
			bldr.append("|")

			bldr.append(mappings.get_flair(match.away.name))
			bldr.append("|")

			bldr.append(match.away.name)
			bldr.append("|")
			bldr.append("|")

			bldr.append("[Page](")
			bldr.append(match.url)
			bldr.append(")")
			bldr.append("|")
			bldr.append("\n")

	return ''.join(bldr)


def render_reddit_event_title(event):
	return f"{event.competition.name} - {event.stage_names()}"

