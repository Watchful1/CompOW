from datetime import datetime, timedelta

STATE_FILENAME = "state.pickle"
ACCOUNT_NAME = None
USER_AGENT = "r/CompetitiveOverwatch bot (by u/Watchful1)"
SUBREDDIT = "CompetitiveOverwatch"

OVER_GG_API = "https://api.over.gg/matches/upcoming"

DISCORD_TOKEN = None

debug_time = datetime.strptime("2019-01-29 05:00:00", "%Y-%m-%d %H:%M:%S") - timedelta(minutes=20)
