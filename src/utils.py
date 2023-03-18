from datetime import datetime

AUTHORIZED_USERS = set("Watchful1")
DEBUG_NOW = None


def utcnow(use_debug=True):
	if use_debug and DEBUG_NOW is not None:
		return DEBUG_NOW
	else:
		return datetime.utcnow()


def past_timestamp(timestamp_dict, key, use_debug=True):
	if key not in timestamp_dict:
		return True
	return utcnow(use_debug) >= timestamp_dict[key]
