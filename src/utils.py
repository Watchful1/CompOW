from datetime import datetime, timedelta
import pytz
import discord_logging
import prawcore
import requests
import random

log = discord_logging.get_logger()

USER_AGENT = "r/CompetitiveOverwatch bot (by u/Watchful1)"
AUTHORIZED_USERS = set("Watchful1")
DEBUG_NOW = None


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


def minutes_to_start(start):
	if start is None:
		return 99999
	if start > utcnow():
		return (start - utcnow()).total_seconds() / 60
	elif start < utcnow():
		return ((utcnow() - start).total_seconds() / 60) * -1
	else:
		return 0

