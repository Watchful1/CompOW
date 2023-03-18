import discord_logging

log = discord_logging.get_logger()

import utils


def process_message(message):
	line_results = []
	for line in message.body.splitlines():
		if line.startswith("approvematch"):
			method()
		elif line.startswith("approveday"):
			method()
		elif line.startswith("approveevent"):
			method()
		elif line.startswith("deletematch"):
			method()
		elif line.startswith("deleteevent"):
			method()
		elif line.startswith("addevent"):
			method()

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
				process_message(message)
		reddit.mark_read(message)
