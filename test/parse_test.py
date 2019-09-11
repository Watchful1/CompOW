import overggparser
from datetime import datetime

from classes.match import Match
from classes.team import Team
from classes.stream import Stream
from classes.enums import GameState
from classes.enums import Winner


def test_parse_match():
	match_url = "https://www.over.gg/12004/nyxl-vs-atl-overwatch-league-2019-season-p-offs-sf"

	fields = overggparser.parse_match(match_url)
	match = Match(
		id=7322,
		start=datetime.strptime("2019-09-08 18:00:00", "%Y-%m-%d %H:%M:%S"),
		url=match_url,
		home=Team("New York Excelsior", "US"),
		away=Team("Atlanta Reign", "US")
		)

	overggparser.merge_fields_into_match(fields, match)

	assert match.home.name == "New York Excelsior"
	assert match.away.name == "Atlanta Reign"
	assert match.state == GameState.COMPLETE
	assert match.home_score == 4
	assert match.away_score == 2
	assert match.winner == "New York Excelsior"
	assert match.competition == "Overwatch League 2019 Season"
	assert match.competition_url == "https://www.over.gg/event/266/overwatch-league-2019-season"
	assert match.stage == "Playoffs: Semifinals"

	expected_streams = [
		Stream("https://www.twitch.tv/overwatchleague", "ENG"),
		Stream("https://www.twitch.tv/overwatchleague_kr", "KR"),
		Stream("https://www.twitch.tv/overwatchleague_fr", "FR")
	]
	for match_stream in match.streams:
		found = False
		for expected_stream in expected_streams:
			if match_stream == expected_stream and match_stream.language == expected_stream.language:
				found = True
				break
		assert found

	assert len(match.maps) == 6
	assert match.maps[0].name == "Busan"
	assert match.maps[0].winner == Winner.HOME
	assert match.maps[1].name == "King's Row"
	assert match.maps[1].winner == Winner.HOME
	assert match.maps[2].name == "Hanamura"
	assert match.maps[2].winner == Winner.AWAY
	assert match.maps[3].name == "Rialto"
	assert match.maps[3].winner == Winner.HOME
	assert match.maps[4].name == "Lijiang Tower"
	assert match.maps[4].winner == Winner.AWAY
	assert match.maps[5].name == "Numbani"
	assert match.maps[5].winner == Winner.HOME


def test_parse_match_with_tie():
	match_url = "https://www.over.gg/11948/ldn-vs-shd-overwatch-league-2019-season-play-in-sf"

	fields = overggparser.parse_match(match_url)
	match = Match(
		id=7269,
		start=datetime.strptime("2019-08-31 15:00:00", "%Y-%m-%d %H:%M:%S"),
		url=match_url,
		home=Team("London Spitfire", "US"),
		away=Team("Shanghai Dragons", "US")
		)

	overggparser.merge_fields_into_match(fields, match)

	assert len(match.maps) == 8
	assert match.maps[0].name == "Busan"
	assert match.maps[0].winner == Winner.HOME
	assert match.maps[1].name == "Numbani"
	assert match.maps[1].winner == Winner.HOME
	assert match.maps[2].name == "Hanamura"
	assert match.maps[2].winner == Winner.AWAY
	assert match.maps[3].name == "Watchpoint: Gibraltar"
	assert match.maps[3].winner == Winner.HOME
	assert match.maps[4].name == "Lijiang Tower"
	assert match.maps[4].winner == Winner.AWAY
	assert match.maps[5].name == "King's Row"
	assert match.maps[5].winner == Winner.TIED
	assert match.maps[6].name == "Dorado"
	assert match.maps[6].winner == Winner.AWAY
	assert match.maps[7].name == "Ilios"
	assert match.maps[7].winner == Winner.HOME
