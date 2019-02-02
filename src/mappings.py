mappings = {
	'stream': {
		"twitch": "Twitch",
		"overwatchcontenders": "Overwatch Contenders"
	},
	'flair': {
		"twitch": ""
	},
	'competition': [
		[
			"Overwatch League Season 2",
		],
		[
			"Overwatch Contenders 2019 Season 1 Trials",
		],
		[
			"Assembly Winter 2019",
		],
	]
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


def competition_ranking(competition):
	if competition is None:
		return None
	for i, competition_group in enumerate(mappings['competition']):
		for competition_name in competition_group:
			if competition_name in competition:
				return i
	return None


def competition_matches(competition):
	if competition_ranking(competition) is not None:
		return True
	else:
		return False
