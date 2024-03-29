import sys

import discord_logging
import re

log = discord_logging.get_logger()

import utils
import liquipedia_parser
from classes.event import Event
from classes.settings import DirtyMixin


def add_event(line, reddit, events):
	log.debug("Adding event from message")
	words = line.split(" ")
	if len(words) < 2:
		return "No link found in message"
	page_url = words[1]
	if "liquipedia.net" not in page_url:
		return f"Not a liquipedia url: {page_url}"

	event = Event(url=page_url)
	DirtyMixin.log = False
	liquipedia_parser.update_event(event, approve_complete=True)
	DirtyMixin.log = True
	reddit.create_page_from_event(event)
	events[event.id] = event

	return f"Event created at https://www.reddit.com/r/Competitiveoverwatch/wiki/{event.wiki_name()}"


def delete_event(line, event, reddit, events):
	log.debug(f"Deleting event from message: {event}")
	if event is None:
		return "Event not found"

	reddit.toggle_page_from_event(event, False)
	del events[event.id]
	return f"Event deleted: {event.id}"


def approve_event(line, event):
	log.debug(f"Approving event from message: {event}")
	if event is None:
		return "Event not found"

	event.approve_all_games()

	return f"Event approved: {event.id}"


def approve_match_day(line, event):
	log.debug(f"Approving match day from message: {event}")
	if event is None:
		return "Event not found"

	parts = line.split(":")
	if not len(parts) >= 2:
		return f"match day id not found: {line}"
	match_day_id = parts[1]

	match_day = event.get_match_day(match_day_id)
	if match_day is None:
		return f"Match day not found: {match_day_id}"

	games_approved = match_day.approve_all_games()

	return f"{games_approved} games approved in match day: {event.id}:{match_day_id}"


def enable_spoilers_match_day(line, event):
	log.debug(f"Enabling spoilers for match day from message: {event}")
	if event is None:
		return "Event not found"

	parts = line.split(":")
	if not len(parts) >= 2:
		return f"match day id not found: {line}"
	match_day_id = parts[1]
	if not len(parts) >= 3:
		return f"true/false not found: {line}"
	if parts[2] == "True":
		enabled = True
	elif parts[2] == "False":
		enabled = False
	else:
		return f"value not True/False: {parts[2]}"

	match_day = event.get_match_day(match_day_id)
	if match_day is None:
		return f"Match day not found: {match_day_id}"

	match_day.spoiler_prevention = enabled

	return f"match day spoilers set to {enabled}: {event.id}:{match_day_id}"


def approve_match(line, event):
	log.debug(f"Approving match from message: {event}")
	if event is None:
		return "Event not found"

	parts = line.split(":")
	if not len(parts) >= 2:
		return f"match id not found: {line}"
	pending_match_id = parts[1]
	if len(parts) >= 3 and parts[2] != "none":
		approved_match_id = parts[2]
	else:
		approved_match_id = None

	match_day = event.get_match_day_from_match_id(pending_match_id)
	if match_day is None:
		return f"Match day not found from match id: {pending_match_id}"

	if match_day.approve_game(pending_match_id, approved_match_id):
		return f"game approved in match day: {event.id}:{match_day.id} : {pending_match_id}:{approved_match_id}"
	else:
		return f"approval failed in match day: {event.id}:{match_day.id} : {pending_match_id}:{approved_match_id}"


def delete_match(line, event):
	log.debug(f"Deleting match from message: {event}")
	if event is None:
		return "Event not found"

	parts = line.split(":")
	if not len(parts) >= 2:
		return f"match id not found: {line}"
	match_id = parts[1]

	match_day = event.get_match_day_from_match_id(match_id)
	if match_day is None:
		return f"Match day not found from match id: {match_id}"

	if match_day.delete_game(match_id):
		return f"game deleted in match day: {event.id}:{match_day.id} : {match_id}"
	else:
		return f"deletion failed in match day: {event.id}:{match_day.id} : {match_id}"


def delete_match_day(line, event):
	log.debug(f"Deleting match day from message: {event}")
	if event is None:
		return "Event not found"

	parts = line.split(":")
	if not len(parts) >= 2:
		return f"match day id not found: {line}"
	match_day_id = parts[1]

	match_day = event.get_match_day(match_day_id)
	if match_day is None:
		return f"Match day not found: {match_day_id}"

	games_deleted = match_day.delete_all_games()

	return f"{games_deleted} games deleted in match day: {event.id}:{match_day_id}"


def update_settings(line, event, reddit):
	log.debug(f"Updating settings from message: {event}")
	if event is None:
		return "No event found"
	parts = line.split(":")
	key = parts[1]
	value = parts[2]
	bool_val = None
	int_val = None
	result = None
	if value == "True":
		bool_val = True
	elif value == "False":
		bool_val = False
	else:
		try:
			int_val = int(value)
		except ValueError:
			pass

	if key == "post_match_threads" and bool_val is not None and event.post_match_threads is not bool_val:
		result = f"post_match_threads from {event.post_match_threads} to {bool_val}"
		event.post_match_threads = bool_val
	elif key == "match_thread_minutes_before" and int_val is not None and event.match_thread_minutes_before != int_val:
		result = f"match_thread_minutes_before from {event.match_thread_minutes_before} to {int_val}"
		event.match_thread_minutes_before = int_val
	elif key == "leave_thread_minutes_after" and int_val is not None and event.leave_thread_minutes_after != int_val:
		result = f"leave_thread_minutes_after from {event.leave_thread_minutes_after} to {int_val}"
		event.leave_thread_minutes_after = int_val
	elif key == "use_pending_changes" and bool_val is not None and event.use_pending_changes is not bool_val:
		result = f"use_pending_changes from {event.use_pending_changes} to {bool_val}"
		event.use_pending_changes = bool_val
	elif key == "discord_key" and event.discord_key != value:
		result = f"discord_key from {event.discord_key} to {value}"
		event.discord_key = value
	elif key == "discord_minutes_before" and int_val is not None and event.discord_minutes_before != int_val:
		result = f"discord_minutes_before from {event.discord_minutes_before} to {int_val}"
		event.discord_minutes_before = int_val
	elif key == "discord_roles" and ','.join(event.discord_roles) != value:
		result = f"discord_roles from {','.join(event.discord_roles)} to {value}"
		event.discord_roles = value.split(",")
	elif key == "name":
		if value == "None":
			value = None
		else:
			value = value.replace("?", ":")
		if event.name != value:
			result = f"name from {event.name} to {value}"
			reddit.toggle_page_from_event(event, False)
			event.name = value
			reddit.create_page_from_event(event)
	if result is not None:
		return result
	return f"settings line no changes/not parsed: {line}"


def process_message(message, reddit, events):
	log.debug(f"Processing message {message.id} from u/{message.author.name}")

	event = None
	event_id_results = re.findall(r'^\w{5}', message.subject)
	if len(event_id_results) and event_id_results[0] in events:
		event = events[event_id_results[0]]

	line_results = []
	for line in message.body.splitlines():
		line = line.strip()
		if line.startswith("kill"):
			log.warning(f"u/{message.author.name} sent kill message, stopping")
			sys.exit(1)
		elif line.startswith("settings"):
			line_result = update_settings(line, event, reddit)
		elif line.startswith("approvematch"):
			line_result = approve_match(line, event)
		elif line.startswith("approveday"):
			line_result = approve_match_day(line, event)
		elif line.startswith("approveevent"):
			line_result = approve_event(line, event)
		elif line.startswith("deletematch"):
			line_result = delete_match(line, event)
		elif line.startswith("deleteday"):
			line_result = delete_match_day(line, event)
		elif line.startswith("deleteevent"):
			line_result = delete_event(message.body, event, reddit, events)
		elif line.startswith("addevent"):
			line_result = add_event(message.body, reddit, events)
		elif line.startswith("enablespoilers"):
			line_result = enable_spoilers_match_day(line, event)
		elif line.startswith("renderwiki"):
			event._dirty = True
			line_result = "rebuilt wiki page"
		else:
			line_result = "No command found for line"
		log.info(line_result)
		line_results.append(line_result)
		reddit.get_settings()  # fetch the settings to force an update on the summary wiki
	return '  \n'.join(line_results)


def parse_messages(reddit, events):
	processed_message = False
	for message in reddit.get_unread():
		if reddit.is_message(message):
			if message.author is None:
				log.info(f"Message {message.id} is a system notification")
			elif message.author.name not in utils.AUTHORIZED_USERS:
				log.info(f"Message {message.id} is from u/{message.author.name}, not authorized")
			else:
				result_message = process_message(message, reddit, events)
				reddit.reply_message(message, result_message)
				processed_message = True
		reddit.mark_read(message)

	return processed_message
