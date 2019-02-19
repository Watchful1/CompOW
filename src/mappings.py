import classes

competitions = [
	classes.Competition(
		name="Overwatch League 2019 Season",
		post_discord=True,
		discord_role="OWL-Notify",
		post_match_threads=True,
		post_minutes_ahead=30
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1 Trials: North America",
		post_match_threads=True
	),
	# classes.Competition(
	# 	name="Overwatch Contenders 2019 Season 1 Trials: Europe"
	# ),
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



