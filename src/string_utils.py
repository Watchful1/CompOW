import classes
import mappings
from urllib.parse import urlparse


def extract_url_name(url):
	try:
		parsed_url = urlparse(url)
	except Exception as err:
		return url

	if "twitch.tv" in parsed_url.netloc.lower():
		last_slash = url.rfind("/", 0, len(url) - 1)
		if url[-1] == '/':
			return url[last_slash + 1:-1]
		else:
			return url[last_slash + 1:]
	else:
		return parsed_url.netloc


def render_reddit(event):
	bldr = []

	bldr.append("> ## **")
	bldr.append(event.competition)
	bldr.append("**\n")

	bldr.append(">####")
	bldr.append(event.stage)

	bldr.append("\n>\n")

	bldr.append(">> *Streams:* ")
	for stream in event.streams:
		bldr.append("[")
		bldr.append(mappings.get_or_default("stream", extract_url_name(stream)))
		bldr.append("](")
		bldr.append(stream)
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


def render_reddit_title(event):
	return f"{event.competition} - {event.stage}"

