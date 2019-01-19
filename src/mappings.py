mappings = {
	'stream': {
		"twitch": "Twitch",
		"overwatchcontenders": "Overwatch Contenders"
	},
	'flair': {
		"twitch": ""
	}
}


def get_or_default(cat, key):
	if cat in mappings:
		if key in mappings[cat]:
			return mappings[cat][key]
		else:
			return key
	else:
		return key


def get_flair(key):
	value = get_or_default("flair", key)
	return f"[](#{value})"
