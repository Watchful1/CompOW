from classes.competition import Competition
from classes.competition import DiscordNotification
from classes.enums import DiscordType

competitions = [
	# Competition(
	# 	name="Overwatch League 2020 Season",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["OWL-Notify", "everyone"],
	# 			channel="377127072243515393"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5,
	# 			roles=["everyone"]
	# 		)
	# 	],
	# 	post_match_threads=True,
	# 	post_minutes_ahead=30,
	# 	day_in_title=True,
	# 	prediction_thread_minutes_ahead=4 * 60,
	# 	leave_thread_minutes=12 * 60
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: Australia",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["AUContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: North America East",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["NAContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: North America West",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["NAContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: Pacific",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["PACContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: Europe",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["EUContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: South America",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["SAContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: Korea",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["KRContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	# Competition(
	# 	name="Overwatch Contenders 2020 Season 1: China",
	# 	discord=[
	# 		DiscordNotification(
	# 			type=DiscordType.COW,
	# 			minutes_ahead=15,
	# 			roles=["CNContenders", "here"],
	# 			channel="420968531929071628"
	# 		),
	# 		DiscordNotification(
	# 			type=DiscordType.THEOW,
	# 			minutes_ahead=5
	# 		)
	# 	]
	# ),
	Competition(
		name="Esports Shanghai Masters",
		post_minutes_ahead=24760,
		discord=[
			DiscordNotification(
				type=DiscordType.COW,
				minutes_ahead=15,
				roles=["here"],
				channel="420968531929071628"
			),
			DiscordNotification(
				type=DiscordType.THEOW,
				minutes_ahead=24760
			)
		]
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
