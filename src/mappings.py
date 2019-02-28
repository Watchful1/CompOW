import classes

competitions = [
	classes.Competition(
		name="Overwatch League 2019 Season",
		discord_minutes_ahead=15,
		discord_roles=["OWL-Notify","everyone"],
		discord_channel="377127072243515393",
		post_match_threads=True,
		post_minutes_ahead=30,
		day_in_title=True,
		prediction_thread_minutes_ahead=8 * 60
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: Australia",
		discord_minutes_ahead=15,
		discord_roles=["AUContenders", "here"],
		discord_channel="420968531929071628"
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: North America East",
		discord_minutes_ahead=15,
		discord_roles=["NAContenders", "here"],
		discord_channel="420968531929071628"
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: North America West",
		discord_minutes_ahead=15,
		discord_roles=["NAContenders", "here"],
		discord_channel="420968531929071628"
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: Pacific",
		discord_minutes_ahead=15,
		discord_roles=["PACContenders", "here"],
		discord_channel="420968531929071628"
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: Europe",
		discord_minutes_ahead=15,
		discord_roles=["EUContenders", "here"],
		discord_channel="420968531929071628"
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: South America",
		discord_minutes_ahead=15,
		discord_roles=["SAContenders", "here"],
		discord_channel="420968531929071628"
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: Korea",
		discord_minutes_ahead=15,
		discord_roles=["KRContenders", "here"],
		discord_channel="420968531929071628"
	),
	classes.Competition(
		name="Overwatch Contenders 2019 Season 1: China",
		discord_minutes_ahead=15,
		discord_roles=["CNContenders", "here"],
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



