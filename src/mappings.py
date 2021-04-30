from classes.competition import Competition
from classes.competition import DiscordNotification
from classes.enums import DiscordType

#contenders 420968531929071628
#match-discussion 377127072243515393
#ow-esports 348939546878017536

cow_roles = {
	'OWL-Notify': '<@&481314680665538569>',
	'OWL-News': '<@&517000617290367016>',
	'Game-News': '<@&517000502924279808>',
	'Community-News': '<@&517000366735228929>',
	'KRContenders': '<@&481315112993554433>',
	'NAContenders': '<@&481315228529721344>',
	'PAContenders': '<@&481315465340387328>',
	'EUContenders': '<@&481315364345479169>',
	'SAContenders': '<@&481315668721926144>',
	'CNContenders': '<@&481315825802936320>',
	'AUContenders': '<@&481315928865505280>',
	'All-Matches': '<@&517000657111220229>',
	'All-Notify': '<@&481316252661579786>',
}
cow_channels = {
	'match-discussion': '377127072243515393',
	'ow-esports': '348939546878017536',
}

competitions = [
	Competition(
		name="Overwatch League 2021 Season",
		discord=[
			DiscordNotification(
				type=DiscordType.COW,
				minutes_ahead=15,
				roles=[cow_roles['OWL-Notify'], "@everyone"],
				channel=cow_channels['match-discussion']
			),
			DiscordNotification(
				type=DiscordType.THEOW,
				minutes_ahead=5,
				roles=["@everyone"]
			)
		],
		post_match_threads=True,
		post_minutes_ahead=30,
		leave_thread_minutes=4 * 60,
		event_build_hours_ahead=96,
		spoiler_stages=["May Melee: West", "May Melee: East", "May Melee: Tournament"]
	),
	Competition(
		name="Overwatch Contenders 2021 Season 1: Australia",
		discord=[
			DiscordNotification(
				type=DiscordType.COW,
				minutes_ahead=15,
				roles=[cow_roles['AUContenders'], "@here"],
				channel=cow_channels['ow-esports']
			),
			DiscordNotification(
				type=DiscordType.THEOW,
				minutes_ahead=5
			)
		]
	),
	Competition(
		name="Overwatch Contenders 2021 Season 1: North America",
		discord=[
			DiscordNotification(
				type=DiscordType.COW,
				minutes_ahead=15,
				roles=[cow_roles['NAContenders'], "@here"],
				channel=cow_channels['ow-esports']
			),
			DiscordNotification(
				type=DiscordType.THEOW,
				minutes_ahead=5
			)
		]
	),
	Competition(
		name="Overwatch Contenders 2021 Season 1: Europe",
		discord=[
			DiscordNotification(
				type=DiscordType.COW,
				minutes_ahead=15,
				roles=[cow_roles['EUContenders'], "@here"],
				channel=cow_channels['ow-esports']
			),
			DiscordNotification(
				type=DiscordType.THEOW,
				minutes_ahead=5
			)
		]
	),
	Competition(
		name="Overwatch Contenders 2021 Season 1: Korea",
		discord=[
			DiscordNotification(
				type=DiscordType.COW,
				minutes_ahead=15,
				roles=[cow_roles['KRContenders'], "@here"],
				channel=cow_channels['ow-esports']
			),
			DiscordNotification(
				type=DiscordType.THEOW,
				minutes_ahead=5
			)
		]
	),
	Competition(
		name="Overwatch Contenders 2021 Season 1: China",
		discord=[
			DiscordNotification(
				type=DiscordType.COW,
				minutes_ahead=15,
				roles=[cow_roles['CNContenders'], "@here"],
				channel=cow_channels['ow-esports']
			),
			DiscordNotification(
				type=DiscordType.THEOW,
				minutes_ahead=5
			)
		]
	),
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
