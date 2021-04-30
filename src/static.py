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
PREDICTION_URL = "https://pickem.overwatchleague.com/"
JUKED_EVENT = "https://juked.gg/e/4252#overview"

AUTHORIZED_USERS = ["Watchful1", "AkshonEsports"]


def get_webhook(discord_type):
	if discord_type == DiscordType.COW:
		return WEBHOOK_COW
	elif discord_type == DiscordType.THEOW:
		return WEBHOOK_THEOW


debug_now = None
#debug_now = datetime.strptime("04-30-21 09:00:00", '%m-%d-%y %H:%M:%S')


def utcnow():
	if debug_now is not None:
		return debug_now
	else:
		return datetime.utcnow()


missing_competition = set()
unparsed_matches = set()
