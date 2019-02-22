import classes

competitions = [
	classes.Competition(
		name="Overwatch League 2019 Season",
		discord_minutes_ahead=15,
		discord_role="OWL-Notify",
		post_match_threads=True,
		post_minutes_ahead=30
	),
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



