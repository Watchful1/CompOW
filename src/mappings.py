import classes

competitions = [
	classes.Competition(
		name="Overwatch League 2019 Season",
		discord_minutes_ahead=15,
		discord_role="OWL-Notify",
		discord_channel="377127072243515393",
		post_match_threads=True,
		post_minutes_ahead=30,
		day_in_title=True
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: Australia",
		discord_minutes_ahead=15,
		discord_role="AUContenders",
		discord_channel="420968531929071628"
	)
]


def get_competition(competition_name):
	if competition_name is None:
		return None, None
	for i, competition in enumerate(competitions):
		if competition_name == competition.name:
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



