import discord_logging

log = discord_logging.get_logger()

import utils
import liquipedia_parser
from classes import Event


def add_event(body, reddit, events):
	log.debug("Adding event from message")
	words = body.split(" ")
	if len(words) < 2:
		return "No link found in message"
	page_url = words[1]
	if "liquipedia.net" not in page_url:
		return f"Not a liquipedia url: {page_url}"

	event = Event(page_url)
	liquipedia_parser.update_event(event)
	reddit.create_page_from_event(event)
	events[event.id] = event

	return f"Event created at https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}"


def delete_event(body, reddit, events):
	log.debug("Deleting event from message")
	words = body.split(" ")
	if len(words) < 2:
		return "No id found in message"
	event_id = words[1]
	if len(event_id) != 5:
		return f"Invalid event id: {event_id}"
	if event_id not in events:
		return f"Event not found: {event_id}"
	event = events[event_id]
	reddit.hide_page_from_event(event)
	del events[event_id]
	return f"Event deleted: {event.id}"


def process_message(message, reddit, events):
	log.debug(f"Processing message {message.id} from u/{message.author.name}")
	line_results = []
	for line in message.body.splitlines():
		if line.startswith("approvematch"):
			line_result = method()
		elif line.startswith("approveday"):
			line_result = method()
		elif line.startswith("approveevent"):
			line_result = method()
		elif line.startswith("deletematch"):
			line_result = method()
		elif line.startswith("deleteevent"):
			line_result = delete_event(message.body, reddit, events)
		elif line.startswith("addevent"):
			line_result = add_event(message.body, reddit, events)
		else:
			line_result = "No command found for line"
		log.info(line_result)
		line_results.append(line_result)

			# name = "Overwatch League 2022 Season",
			# discord = [
			# 	DiscordNotification(
			# 		type=DiscordType.COW,
			# 		minutes_ahead=15,
			# 		roles=[cow_roles['OWL-Notify'], "@everyone"],
			# 		channel=cow_channels['match-discussion']
			# 	),
			# 	DiscordNotification(
			# 		type=DiscordType.THEOW,
			# 		minutes_ahead=5,
			# 		roles=["@everyone"]
			# 	)
			# ],
			# post_match_threads = True,
			# post_minutes_ahead = 150,
			# leave_thread_minutes = 4 * 60,
			# spoiler_stages = ["Play-offs: Upper bracket","Play-offs: Lower Bracket"]


def parse_messages(reddit, events):
	for message in reddit.get_unread():
		if reddit.is_message(message):
			if message.author is None:
				log.info(f"Message {message.id} is a system notification")
			elif message.author.name not in utils.AUTHORIZED_USERS:
				log.info(f"Message {message.id} is from u/{message.author.name}, skipping")
			else:
				process_message(message, reddit, events)
		reddit.mark_read(message)
