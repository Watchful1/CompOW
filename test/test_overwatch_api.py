import discord_logging

log = discord_logging.init_logging()

import overwatch_api_parser


week = overwatch_api_parser.ScheduleWeek(4)
week.update_week()
print(week.matches[37377]['status'])
print(week.matches[37377]['competitors'][0]['name'])
print(week.matches[37377]['competitors'][1]['name'])
