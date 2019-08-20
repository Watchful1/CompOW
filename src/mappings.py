from classes.competition import Competition

competitions = [
	Competition(
		name="Overwatch League 2019 Season",
		discord_minutes_ahead=15,
		discord_roles=["OWL-Notify","everyone"],
		discord_channel="377127072243515393",
		post_match_threads=True,
		post_minutes_ahead=30,
		day_in_title=True,
		prediction_thread_minutes_ahead=8 * 60
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: Australia",
		discord_minutes_ahead=15,
		discord_roles=["AUContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: North America East",
		discord_minutes_ahead=15,
		discord_roles=["NAContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: North America West",
		discord_minutes_ahead=15,
		discord_roles=["NAContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: Pacific",
		discord_minutes_ahead=15,
		discord_roles=["PACContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: Europe",
		discord_minutes_ahead=15,
		discord_roles=["EUContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: South America",
		discord_minutes_ahead=15,
		discord_roles=["SAContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: Korea",
		discord_minutes_ahead=15,
		discord_roles=["KRContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019 Season 2: China",
		discord_minutes_ahead=15,
		discord_roles=["CNContenders", "here"],
		discord_channel="420968531929071628"
	),
	Competition(
		name="Overwatch Contenders 2019: The Gauntlet",
		discord_minutes_ahead=15,
		discord_roles=["here"],
		discord_channel="420968531929071628"
	)
]
stream_languages = [
	"eng",
	"kr"
]
stream_urls = [
	"https://www.twitch.tv/overwatchleague",
	"https://www.twitch.tv/overwatchcontenders",
	"https://www.twitch.tv/broadcastgg"
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


def stream_ranking(stream_url, stream_language):
	if stream_url is None:
		return 10
	language_rank = 9
	if stream_language is not None:
		for i, language in enumerate(stream_languages):
			if stream_language.lower() == language:
				language_rank = i
				break
	url_rank = 9
	for i, url in enumerate(stream_urls):
		if stream_url == url:
			url_rank = i
			break

	return language_rank + (url_rank / 10)
