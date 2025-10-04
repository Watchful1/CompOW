from datetime import datetime, timezone, timedelta
import pytz
import discord_logging
import prawcore
import requests
import random

log = discord_logging.get_logger()

USER_AGENT = "r/CompetitiveOverwatch bot (by u/Watchful1)"
AUTHORIZED_USERS = {
	"merger3",
	"Watchful1",
	"blankepitaph",
	"imKaku",
	"ModWilliam",
	"Dobvius",
	"FelipeDoesStats2",
	"lolburger13",
	"TheUltimate721",
	"UnknownQTY",
}
DEBUG_NOW = None
DEFAULT_ROLES = ['All-Notify', 'All-Matches']
TIMEZONES = {
	"ACST": [9, 30],
	"ACDT": [10, 30],
	"ADT": [-3, 0],
	"AEDT": [11, 0],
	"AEST": [10, 0],
	"AKST": [-9, 0],
	"AKDT": [-8, 0],
	"ALMT": [5, 0],
	"AMT": [4, 0],
	"AQTT": [5, 0],
	"ART": [-3, 0],
	"AST": [3, 0],
	"AZT": [4, 0],
	"BOT": [-4, 0],
	"BRST": [-2, 0],
	"BRT": [-3, 0],
	"BNT": [8, 0],
	"BST": [1, 0],
	"CAT": [2, 0],
	"CEST": [2, 0],
	"CET": [1, 0],
	"COT": [-5, 0],
	"CLST": [-3, 0],
	"CLT": [-4, 0],
	"CST": [8, 0],
	"CDT": [-5, 0],
	"CT": [-6, 0],
	"EAT": [3, 0],
	"ECT": [-5, 0],
	"EDT": [-4, 0],
	"EEST": [3, 0],
	"EET": [2, 0],
	"EST": [-5, 0],
	"GET": [4, 0],
	"GMT": [0, 0],
	"GST": [4, 0],
	"HKT": [8, 0],
	"IDT": [3, 0],
	"IRDT": [4, 30],
	"IRST": [3, 30],
	"IST": [5, 30],
	"JST": [9, 0],
	"KGT": [6, 0],
	"KST": [9, 0],
	"MDT": [-6, 0],
	"MMT": [6, 30],
	"MSK": [3, 0],
	"MST": [-7, 0],
	"MUT": [4, 0],
	"MVT": [5, 0],
	"MYT": [8, 0],
	"NPT": [5, 45],
	"NZDT": [13, 0],
	"NZST": [12, 0],
	"PDT": [-7, 0],
	"PET": [-5, 0],
	"PHST": [8, 0],
	"PHT": [8, 0],
	"PKT": [5, 0],
	"PST": [-8, 0],
	"PYT": [-4, 0],
	"SAST": [2, 0],
	"SGT": [8, 0],
	"THA": [7, 0],
	"ICT": [7, 0],
	"TJT": [5, 0],
	"TMT": [5, 0],
	"TRT": [3, 0],
	"TST": [8, 0],
	"ULAT": [8, 0],
	"UTC": [0, 0],
	"UZT": [5, 0],
	"VET": [-4, 0],
	"VLAT": [10, 0],
	"WAT": [1, 0],
	"WEST": [1, 0],
	"WET": [0, 0],
	"WIB": [7, 0],
	"WITA": [8, 0],
}


def process_error(message, exception, traceback):
	is_transient = \
		isinstance(exception, prawcore.exceptions.ServerError) or \
		isinstance(exception, prawcore.exceptions.ResponseException) or \
		isinstance(exception, prawcore.exceptions.RequestException) or \
		isinstance(exception, requests.exceptions.Timeout) or \
		isinstance(exception, requests.exceptions.ReadTimeout) or \
		isinstance(exception, requests.exceptions.RequestException)
	log.warning(f"{message}: {type(exception).__name__} : {exception}")
	if is_transient:
		log.info(traceback)
	else:
		log.warning(traceback)

	return is_transient


def get_timezone(timezone_name):
	if timezone_name not in TIMEZONES:
		log.info(f"Timezone not found: {timezone_name}")
		return None

	timezone_hours, timezone_minutes = TIMEZONES.get(timezone_name)
	return timezone(timedelta(hours=timezone_hours, minutes=timezone_minutes))


def base36encode(integer: int) -> str:
	chars = '0123456789abcdefghijklmnopqrstuvwxyz'
	sign = '-' if integer < 0 else ''
	integer = abs(integer)
	result = ''
	while integer > 0:
		integer, remainder = divmod(integer, 36)
		result = chars[remainder] + result
	return sign + result


def get_random_id():
	id_range_start = int("10000", 36)
	id_range_end = int("zzzzz", 36)
	return base36encode(random.randrange(id_range_start, id_range_end))


def utcnow(offset=0, use_debug=True):
	if use_debug and DEBUG_NOW is not None:
		result = DEBUG_NOW.replace(tzinfo=pytz.utc)
	else:
		result = datetime.utcnow().replace(tzinfo=pytz.utc)
	return result + timedelta(seconds=offset)


def past_timestamp(timestamp_dict, key, use_debug=True):
	if key not in timestamp_dict:
		return True
	return utcnow(use_debug) >= timestamp_dict[key]


def timestamp_within(first_datetime, second_datetime, delta):
	if first_datetime is not None and second_datetime is not None and \
			abs((first_datetime - second_datetime).total_seconds()) < delta.total_seconds():
		return True
	return False


def minutes_to_start(start):
	if start is None:
		return 99999
	if start > utcnow():
		return (start - utcnow()).total_seconds() / 60
	elif start < utcnow():
		return ((utcnow() - start).total_seconds() / 60) * -1
	else:
		return 0

