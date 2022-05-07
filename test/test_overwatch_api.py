import discord_logging

log = discord_logging.init_logging()

import overwatch_api_parser


week = overwatch_api_parser.ScheduleWeek(2)
week.update_week()

for match in week.matches.values():
	print(str(match))
