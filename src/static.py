from classes.enums import DiscordType

STATE_FILENAME = "state.pickle"
ACCOUNT_NAME = None
USER_AGENT = "r/CompetitiveOverwatch bot (by u/Watchful1)"
SUBREDDIT = "CompetitiveOverwatch"
WEBHOOK_COW = None
WEBHOOK_THEOW = None

OVER_GG_API = "https://api.over.gg/matches/upcoming"
FLAIR_LIST = "http://rcompetitiveoverwatch.com/static/data/flairs.json"
PREDICTION_URL = "https://lerhond.pl/predictor/owl-2020/"

AUTHORIZED_USERS = ["Watchful1", "AkshonEsports"]


def get_webhook(discord_type):
	if discord_type == DiscordType.COW:
		return WEBHOOK_COW
	elif discord_type == DiscordType.THEOW:
		return WEBHOOK_THEOW


missing_competition = set()
