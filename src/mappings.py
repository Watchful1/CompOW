import classes

mappings = {
	'stream': {
		"twitch": "Twitch",
		"overwatchcontenders": "Overwatch Contenders"
	},
	'flair': {
		"twitch": ""
	}
}

competitions = [
	classes.Competition(
		name="Overwatch League 2019 Season",
		post_discord=True,
		discord_role="OWL-Notify",
		post_match_threads=True
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1 Trials"
	),
]


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


def get_competition(competition_name):
	if competition_name is None:
		return None, None
	for i, competition in enumerate(competitions):
		if competition_name in competition.name:
			return i, competition
	return None, None


def competition_ranking(competition_name):
	i, competition = get_competition(competition_name)
	return i


def competition_matches(competition):
	if competition_ranking(competition) is not None:
		return True
	else:
		return False



