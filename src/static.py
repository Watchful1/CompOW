from classes.enums import DiscordType
from datetime import datetime

STATE_FILENAME = "state.pickle"
ACCOUNT_NAME = None
USER_AGENT = "r/CompetitiveOverwatch bot (by u/Watchful1)"
SUBREDDIT = "CompetitiveOverwatch"
WEBHOOK_COW = None
WEBHOOK_THEOW = None

OVER_GG_API = "https://api.over.gg/matches/upcoming"
FLAIR_LIST = "http://rcompetitiveoverwatch.com/static/data/flairs.json"
PREDICTION_URL = "https://pickem.overwatchleague.com/en-us/leaderboard/reddit-cow/2022/kickoff-clash"
JUKED_EVENT = "https://juked.gg/e/4252#overview"

AUTHORIZED_USERS = ["Watchful1", "AkshonEsports"]


def get_webhook(discord_type):
	if discord_type == DiscordType.COW:
		return WEBHOOK_COW
	elif discord_type == DiscordType.THEOW:
		return WEBHOOK_THEOW


def utcnow():
	#return datetime.strptime("22-05-05 18:00:00", '%y-%m-%d %H:%M:%S')
	return datetime.utcnow()


missing_competition = set()
unparsed_matches = set()
