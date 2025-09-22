import os
import sys
from datetime import datetime, timezone, timedelta

import discord_logging
from lxml import etree
import requests
import json
import re
import wikitextparser as wtp
import mwparserfromhell

log = discord_logging.init_logging()

from liquipedia_parser import parse_event_markdown


def is_match(node):
	if 'name' in node:
		log.info(f"name: {node.name}")
	if 'title' in node:
		log.info(f"title: {node.title}")
	return False


def param_from_template_name(template, name):
	param = template.get(name)
	if param is None:
		return None
	templates = param.value.filter_templates()
	if len(templates) == 0:
		return None
	single_template = templates[0]
	if len(single_template.params) == 0:
		return None
	return single_template.get(1).value.strip()


timezones = {
	"ACST": [9, 30],
	"ACDT": [10, 30],
	"ADT": [-3, 0],
	"AEDT": [11, 0],
	"AEST": [10, 0],
	"AKST": [-9, 0],
	"AKDT": [-8, 0],
	"ALMT": [5, 0],
	"AMT": [4, 0],
	"AQTT": [5, 0],
	"ART": [-3, 0],
	"AST": [3, 0],
	"AZT": [4, 0],
	"BOT": [-4, 0],
	"BRST": [-2, 0],
	"BRT": [-3, 0],
	"BNT": [8, 0],
	"BST": [1, 0],
	"CAT": [2, 0],
	"CEST": [2, 0],
	"CET": [1, 0],
	"COT": [-5, 0],
	"CLST": [-3, 0],
	"CLT": [-4, 0],
	"CST": [8, 0],
	"CDT": [-5, 0],
	"CT": [-6, 0],
	"EAT": [3, 0],
	"ECT": [-5, 0],
	"EDT": [-4, 0],
	"EEST": [3, 0],
	"EET": [2, 0],
	"EST": [-5, 0],
	"GET": [4, 0],
	"GMT": [0, 0],
	"GST": [4, 0],
	"HKT": [8, 0],
	"IDT": [3, 0],
	"IRDT": [4, 30],
	"IRST": [3, 30],
	"IST": [5, 30],
	"JST": [9, 0],
	"KGT": [6, 0],
	"KST": [9, 0],
	"MDT": [-6, 0],
	"MMT": [6, 30],
	"MSK": [3, 0],
	"MST": [-7, 0],
	"MUT": [4, 0],
	"MVT": [5, 0],
	"MYT": [8, 0],
	"NPT": [5, 45],
	"NZDT": [13, 0],
	"NZST": [12, 0],
	"PDT": [-7, 0],
	"PET": [-5, 0],
	"PHST": [8, 0],
	"PHT": [8, 0],
	"PKT": [5, 0],
	"PST": [-8, 0],
	"PYT": [-4, 0],
	"SAST": [2, 0],
	"SGT": [8, 0],
	"THA": [7, 0],
	"ICT": [7, 0],
	"TJT": [5, 0],
	"TMT": [5, 0],
	"TRT": [3, 0],
	"TST": [8, 0],
	"ULAT": [8, 0],
	"UTC": [0, 0],
	"UZT": [5, 0],
	"VET": [-4, 0],
	"VLAT": [10, 0],
	"WAT": [1, 0],
	"WEST": [1, 0],
	"WET": [0, 0],
	"WIB": [7, 0],
	"WITA": [8, 0],
}


def get_timezone(timezone_name):
	if timezone_name not in timezones:
		log.info(f"Timezone not found: {timezone_name}")
		return None

	timezone_hours, timezone_minutes = timezones.get(timezone_name)
	return timezone(-timedelta(hours=timezone_hours, minutes=timezone_minutes))


if __name__ == "__main__":
	#url = "https://liquipedia.net/overwatch/api.php?action=query&meta=siteinfo&titles=Overwatch_Champions_Series/2025/NA/Stage_3/Regular_Season&exportnowrap=true&format=json"
	url = "https://liquipedia.net/overwatch/api.php?action=parse&meta=siteinfo&titles=Overwatch_Champions_Series/2025/NA/Stage_3/Regular_Season&exportnowrap=true&format=json"
	#url = "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/NA/Stage_3/Regular_Season"

	#event = parse_event_markdown(url)

	#page_content = """{{DISPLAYTITLE:Overwatch Champions Series 2025 - NA Stage 3 - Regular Season}}\n{{Overwatch Champions Series navbox/2025/Stage 3}}\n{{Tabs static\n|name1=Overview|link1=Overwatch Champions_Series/2025/NA/Stage 3\n|name2=Regular Season|link2=Overwatch Champions Series/2025/NA/Stage 3/Regular Season\n}}\n{{HiddenDataBox\n|liquipediatier=2\n|publishertier=owcs\n|name=Overwatch Champions Series 2025 - NA Stage 3 - Regular Season\n|tickername=OWCS Stage 3 NA Regular Season\n|series=Overwatch Champions Series\n|sdate=2025-09-06\n|edate=2025-10-12\n}}\n\n''This page is part of the [[Overwatch Champions Series/2025/NA/Stage 3|Overwatch Champions Series 2025 - NA Stage 3]] article.''\n\n==Results==\n==={{Stage|Standings}}===\n{{box|start|padding=2em}}\n<section begin=\"Standings\"/>\n{{GroupTableLeague2 \n|title=Standings|width=470px |show_g=true |diff=true\n|pbg1=seedup|pbg2=seedup|pbg3=seedup|pbg4=seedup|pbg5=up|pbg6=up|pbg7=down|pbg8=down\n|roundtitle=Week\n|bg1=|team1=Geekay Esports\n|bg2=|team2=Team Liquid\n|bg3=|team3=NTMR\n|bg4=|team4=Spacestation Gaming\n|bg5=|team5=Sakura Esports\n|bg6=|team6=Extinction\n|bg7=|team7=Supernova (American team)\n|bg8=|team8=DhillDucks\n|round1edate=September 7, 2025 - 23:30 {{Abbr/PST}}\n|round2edate=September 14, 2025 - 23:30 {{Abbr/PST}}\n|round3edate=September 21, 2025 - 23:30 {{Abbr/PST}}\n|round4edate=September 28, 2025 - 23:30 {{Abbr/PST}}\n|round5edate=October 5, 2025 - 23:30 {{Abbr/PST}}\n|edate=October 12, 2025 - 23:30 {{Abbr/PST}}\n|tournament=Overwatch Champions Series/2025/NA/Stage 3/Regular Season\n|tiebreaker1=series\n|tiebreaker2=ml.matchScore\n|tiebreaker3=diff\n}}\n<section end=\"Standings\"/>\n{{box|break|padding=2em}}\n{{CrossTableLeague\n|tournament=Overwatch Champions Series/2025/NA/Stage 3/Regular Season\n|single=true\n|team1=Geekay Esports\n|team2=Team Liquid\n|team3=NTMR\n|team4=Spacestation Gaming\n|team5=Sakura Esports\n|team6=Extinction\n|team7=Supernova (American team)\n|team8=DhillDucks\n|edate=2025-10-13\n}}\n{{box|end}}\n\n==Matches==\n{{box|start|padding=2em}}\n==={{HiddenSort|Week 1}}===\n{{Matchlist|id=AOQW3S7ZVT|title=Week 1|collapsed=false\n|M1header=September 6th\n|M1={{Match\n    |bestof=5\n    |date=2025-09-06 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ntmr}}\n    |opponent2={{TeamOpponent|team liquid}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-09-06 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|sakura esports}}\n    |opponent2={{TeamOpponent|spacestation gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M3={{Match\n    |date=2025-09-06 - 15:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|extinction}}\n    |opponent2={{TeamOpponent|dhillducks}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M4header=September 7th\n|M4={{Match\n    |date=2025-09-07 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|geekay esports}}\n    |opponent2={{TeamOpponent|supernova (American team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M5={{Match\n    |date=2025-09-07 - 15:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ntmr}}\n    |opponent2={{TeamOpponent|spacestation gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 2}}===\n{{MatchSection|Week 2}}\n{{Matchlist|id=Bt0sjSQ3Ec|title=Week 2|collapsed=false\n|M1header=September 13\n|M1={{Match\n    |bestof=5\n    |date=2025-09-13 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Geekay esports}}\n    |opponent2={{TeamOpponent|sakura esports}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-09-13 - 13:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|extinction}}\n    |opponent2={{TeamOpponent|team liquid}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M3header=September 14th\n|M3={{Match\n    |date=2025-09-14 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|supernova (american team)}}\n    |opponent2={{TeamOpponent|spacestation gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M4={{Match\n    |date=2025-09-14 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ntmr}}\n    |opponent2={{TeamOpponent|dhillducks}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 3}}===\n{{MatchSection|Week 3}}\n{{Matchlist|id=T5riDUSIrE|title=Week 3|collapsed=false\n|M1header=September 20th\n|M1={{Match\n    |bestof=5\n    |date=2025-09-20 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|sakura esports}}\n    |opponent2={{TeamOpponent|dhillducks}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-09-20 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|geekay esports}}\n    |opponent2={{TeamOpponent|ntmr}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M3={{Match\n    |date=2025-09-20 - 15:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|team liquid}}\n    |opponent2={{TeamOpponent|spacestation gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M4header=September 21st\n|M4={{Match\n    |date=2025-09-21 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|dhillducks}}\n    |opponent2={{TeamOpponent|supernova (American team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M5={{Match\n    |date=2025-09-21 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|extinction}}\n    |opponent2={{TeamOpponent|sakura esports}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 4}}===\n{{MatchSection|Week 4}}\n{{Matchlist|id=0ZbZvQWpqY|title=Week 4|collapsed=false\n|M1header=September 27th\n|M1={{Match\n    |bestof=5\n    |date=2025-09-27 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|sakura esports}}\n    |opponent2={{TeamOpponent|ntmr}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-09-27 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|extinction}}\n    |opponent2={{TeamOpponent|geekay esports}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M3header=September 28th\n|M3={{Match\n    |date=2025-09-28 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|dhillducks}}\n    |opponent2={{TeamOpponent|spacestation gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M4={{Match\n    |date=2025-09-28 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|supernova (american team)}}\n    |opponent2={{TeamOpponent|team liquid}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 5}}===\n{{MatchSection|Week 5}}\n{{Matchlist|id=7W4bkwFic5|title=Week 5|collapsed=false\n|M1header=October 4th\n|M1={{Match\n    |bestof=5\n    |date=2025-10-04 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|sakura esports}}\n    |opponent2={{TeamOpponent|supernova (american team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-10-04 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|geekay esports}}\n    |opponent2={{TeamOpponent|team liquid}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M3={{Match\n    |date=2025-10-04 - 15:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|extinction}}\n    |opponent2={{TeamOpponent|spacestation gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M4header=October 5th\n|M4={{Match\n    |date=2025-10-05 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ntmr}}\n    |opponent2={{TeamOpponent|supernova (american team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n\t}}\n|M5={{Match\n    |date=2025-10-05 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|geekay esports}}\n    |opponent2={{TeamOpponent|dhillducks}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n\t}}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 6}}===\n{{MatchSection|Week 6}}\n{{Matchlist|id=vFpyDZxqSf|title=Week 6|collapsed=false\n|M1header=October 11th\n|M1={{Match\n    |bestof=5\n    |date=2025-10-11 - 12:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|geekay esports}}\n    |opponent2={{TeamOpponent|spacestation gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-10-11 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|sakura esports}}\n    |opponent2={{TeamOpponent|team liquid}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M3={{Match\n    |date=2025-10-11 - 15:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|extinction}}\n    |opponent2={{TeamOpponent|supernova (american team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n    }}\n|M4header=October 12th\n|M4={{Match\n    |date=2025-10-12 - 13:30 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|dhillducks}}\n    |opponent2={{TeamOpponent|team liquid}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n\t}}\n|M5={{Match\n    |date=2025-10-12 - 15:00 {{Abbr/PST}}\n    |twitch=ow_esports|youtube=Overwatch Esports\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|extinction}}\n    |opponent2={{TeamOpponent|ntmr}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n\t|map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |faceit=\n    |mvp=\n\t}}\n}}\n{{box|end|padding=2em}}"""
	page_content = """{{DISPLAYTITLE:Overwatch Champions Series 2025 - Stage 3 Korea - Regular Season}}\n{{Overwatch Champions Series navbox/2025/Stage 3}}\n{{Tabs static\n|name1=Overview|link1=Overwatch Champions Series/2025/Asia/Stage 3/Korea\n|name2=Regular Season|link2=Overwatch Champions Series/2025/Asia/Stage 3/Korea/Regular Season\n}}\n{{HiddenDataBox\n|liquipediatier=2\n|publishertier=owcs\n|name=Overwatch Champions Series 2025 - Korea Stage 3 - Regular Season\n|tickername=OWCS Stage 3 Korea Regular Season\n|series=Overwatch Champions Series\n|sdate=2025-08-29\n|edate=2025-09-21\n}}\n\n''This page is part of the [[Overwatch_Champions_Series/2025/Asia/Stage_3/Korea|Overwatch Champions Series 2025 - Stage 3 Korea]] article.''\n\n==Standings==\n{{box|start|padding=2em}}\n<section begin=\"Standings\"/>\n{{GroupTableLeague2 \n|title=Standings|width=470px |show_g=true |diff=true\n|pbg1=up |pbg2=up |pbg3=up |pbg4=up |pbg5=stayup |pbg6=stayup |pbg7=stayup |pbg8=stayup |pbg9=down\n|team1=Crazy Raccoon\n|team2=T1\n|team3=WAE\n|team4=ZETA DIVISION\n|team5=ONSIDE Gaming\n|team6=Team Falcons\n|team7=Old Ocean\n|team8=Mir Gaming\n|team9=Cheeseburger (Korean team)\n\n|roundtitle=Week\n|tournament=Overwatch Champions Series/2025/Asia/Stage 3/Korea/Regular Season\n|tiebreaker1=series\n|tiebreaker2=diff\n|tiebreaker3=h2h series\n}}\n<section end=\"Standings\"/>\n{{box|break|padding=2em}}\n{{CrossTableLeague\n|tournament=Overwatch Champions Series/2025/Asia/Stage 3/Korea/Regular Season\n|single=true\n|team1=T1\n|team2=Crazy Raccoon\n|team3=WAE \n|team4=ZETA DIVISION\n|team5=Team Falcons\n|team6=ONSIDE Gaming\n|team7=Old Ocean\n|team8=Mir Gaming\n|team9=Cheeseburger (Korean team)\n}}\n{{box|end}}\n\n==Matches==\n{{box|start|padding=2em}}\n==={{HiddenSort|Week 1}}===\n{{Matchlist|id=U2RedCR2HL|title=Week 1|matchsection=Week 1|collapsed=false\n|M1header=August 29\n|M1={{Match\n    |bestof=5\n    |date=2025-08-29 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=https://youtu.be/EbIjW50pBYI\n    |caster1=baganeol|caster2=ChangSik\n    |opponent1={{TeamOpponent|Cheeseburger (Korean team)}}\n    |opponent2={{TeamOpponent|ZETA DIVISION}}\n    |map1={{Map|map=Busan|mode=Control|score1=2|score2=1|winner=1\n        |t1b1=wuyang|t2b1=genji|banstart=2}}\n    |map2={{Map|map=Esperança|mode=Push|score1=116.51|score2=80.80|winner=1\n        |t1b1=freja|t2b1=winston|banstart=2}}\n    |map3={{Map|map=Aatlis|mode=Flashpoint|score1=1|score2=3|winner=2\n        |t1b1=mauga|t2b1=venture|banstart=2}}\n    |map4={{Map|map=Junkertown|mode=Escort|score1=3|score2=4|winner=2\n        |t1b1=d.va|t2b1=illari|banstart=1}}\n    |map5={{Map|map=Eichenwalde|mode=Escort|score1=1|score2=2|winner=2\n        |t1b1=hazard|t2b1=brigitte|banstart=1}}\n    |mvp=BERNAR\n    }}\n|M2={{Match\n    |date=2025-08-29 - 19:45 {{Abbr/KST}}\n    |afreeca=owesports|vod=https://youtu.be/FT02aPMdJ-E\n    |caster1=baganeol|caster2=ChangSik\n    |opponent1={{TeamOpponent|Team Falcons}}\n    |opponent2={{TeamOpponent|Crazy Raccoon}}\n    |map1={{Map|map=Busan|mode=Control|score1=0|score2=2|winner=2\n        |t1b1=wrecking ball|t2b1=kiriko|banstart=1}}\n    |map2={{Map|map=Aatlis|mode=Flashpoint|score1=0|score2=3|winner=2\n        |t1b1=mercy|t2b1=cassidy|banstart=1}}\n    |map3={{Map|map=Esperança|mode=Push|score1=11.71|score2=142.41|winner=2\n        |t1b1=winston|t2b1=lucio|banstart=1}}\n    |mvp=SP1NT\n    }}\n|M3={{Match\n    |date=2025-08-29 - 21:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=https://youtu.be/CRDxEh4Wn1s\n    |caster1=baganeol|caster2=ChangSik\n    |opponent1={{TeamOpponent|T1}}\n    |opponent2={{TeamOpponent|Mir Gaming}}\n    |map1={{Map|map=Busan|mode=|score1=2|score2=0|winner=1\n        |t1b1=dva|t2b1=freja|banstart=1}}\n    |map2={{Map|map=New Queen Street|mode=Push|score1=128.11|score2=17.56|winner=1\n        |t1b1=sombra|t2b1=kiriko|banstart=2}}\n    |map3={{Map|map=Watchpoint: Gibraltar|mode=Escort|score1=3|score2=0|winner=1\n        |t1b1=freja|t2b1=brigitte|banstart=2}}\n    |mvp=ZEST\n    }}\n|M4header=August 30\n|M4={{Match\n    |date=2025-08-30 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=https://youtu.be/CRDxEh4Wn1s\n    |caster1=TheMarine|caster2=Strings\n    |opponent1={{TeamOpponent|Team Falcons}}\n    |opponent2={{TeamOpponent|ONSIDE GAMING}}\n    |map1={{Map|map=Ilios|mode=Control|score1=2|score2=0|winner=1\n        |t1b1=dva|t2b1=ana|banstart=1}}\n    |map2={{Map|map=Circuit Royal|mode=Escort|score1=2|score2=1|winner=1\n        |t1b1=wuyang|t2b1=ramattra|banstart=2}}\n    |map3={{Map|map=Aatlis|mode=Flashpoint|score1=3|score2=0|winner=1\n        |t1b1=genji|t2b1=winston|banstart=2}}\n    |mvp=Proper\n    }}\n|M5={{Match\n    |date=2025-08-30 - 18:40 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=TheMarine|caster2=Strings\n    |opponent1={{TeamOpponent|WAE}}\n    |opponent2={{TeamOpponent|Old Ocean}}\n    |map1={{Map|map=Samoa|mode=Control|score1=2|score2=0|winner=1\n        |t1b1=hazard|t2b1=kiriko|banstart=2}}\n    |map2={{Map|map=Aatlis|mode=Flashpoint|score1=3|score2=0|winner=1\n        |t1b1=wuyang|t2b1=tracer|banstart=2}}\n    |map3={{Map|map=Hollywood|mode=Hybrid|score1=2|score2=1|winner=1\n        |t1b1=kiriko|t2b1=winston|banstart=2}}\n    |mvp=Ade\n    }}\n|M6={{Match\n    |date=2025-08-30 - 21:15 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=TheMarine|caster2=Strings\n    |opponent1={{TeamOpponent|Cheeseburger (Korean team)}}\n    |opponent2={{TeamOpponent|T1}}\n    |map1={{Map|map=Lijiang Tower|mode=Control|score1=1|score2=2|winner=2\n        |t1b1=hazard|t2b1=lucio|banstart=2}}\n    |map2={{Map|map=Watchpoint: Gibraltar|mode=Escort|score1=0|score2=3|winner=2\n        |t1b1=wuyang|t2b1=winston|banstart=1}}\n    |map3={{Map|map=Aatlis|mode=Flashpoint|score1=2|score2=3|winner=2\n        |t1b1=wrecking ball|t2b1=junkrat|banstart=1}}\n    |mvp=D0NGHAK\n    }}\n|M7header=August 31\n|M7={{Match\n    |date=2025-08-31 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Mir Gaming}}\n    |opponent2={{TeamOpponent|ONSIDE GAMING}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M8={{Match\n    |date=2025-08-31 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ZETA DIVISION}}\n    |opponent2={{TeamOpponent|Old Ocean}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M9={{Match\n    |date=2025-08-31 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Crazy Raccoon}}\n    |opponent2={{TeamOpponent|WAE}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 2}}===\n{{Matchlist|id=MacTApwm2l|title=Week 2|matchsection=Week 2|collapsed=false\n|M1header=September 5\n|M1={{Match\n    |bestof=5\n    |date=2025-09-05 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|WAE}}\n    |opponent2={{TeamOpponent|Cheeseburger (Korean team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-09-05 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ONSIDE GAMING}}\n    |opponent2={{TeamOpponent|Crazy Raccoon}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M3={{Match\n    |date=2025-09-05 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ZETA DIVISION}}\n    |opponent2={{TeamOpponent|Team Falcons}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M4header=September 6\n|M4={{Match\n    |date=2025-09-06 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Mir Gaming}}\n    |opponent2={{TeamOpponent|WAE}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M5={{Match\n    |date=2025-09-06 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Old Ocean}}\n    |opponent2={{TeamOpponent|T1}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M6={{Match\n    |date=2025-09-06 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ONSIDE GAMING}}\n    |opponent2={{TeamOpponent|Cheeseburger (Korean team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M7header=September 7\n|M7={{Match\n    |date=2025-09-07 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Mir Gaming}}\n    |opponent2={{TeamOpponent|ZETA DIVISION}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M8={{Match\n    |date=2025-09-07 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Crazy Raccoon}}\n    |opponent2={{TeamOpponent|T1}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M9={{Match\n    |date=2025-09-07 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Team Falcons}}\n    |opponent2={{TeamOpponent|Old Ocean}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 3}}===\n{{Matchlist|id=YkrEAWPNag|title=Week 3|matchsection=Week 3|collapsed=false\n|M1header=September 12\n|M1={{Match\n    |bestof=5\n    |date=2025-09-12 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|WAE}}\n    |opponent2={{TeamOpponent|Team Falcons}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-09-12 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Old Ocean}}\n    |opponent2={{TeamOpponent|Mir Gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M3={{Match\n    |date=2025-09-12 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ONSIDE GAMING}}\n    |opponent2={{TeamOpponent|T1}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M4header=September 13\n|M4={{Match\n    |date=2025-09-13 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Mir Gaming}}\n    |opponent2={{TeamOpponent|Team Falcons}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M5={{Match\n    |date=2025-09-13 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Crazy Raccoon}}\n    |opponent2={{TeamOpponent|ZETA DIVISION}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M6={{Match\n    |date=2025-09-13 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Old Ocean}}\n    |opponent2={{TeamOpponent|Cheeseburger (Korean team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M7header=September 14\n|M7={{Match\n    |date=2025-09-14 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ZETA DIVISION}}\n    |opponent2={{TeamOpponent|ONSIDE GAMING}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M8={{Match\n    |date=2025-09-14 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Cheeseburger (Korean team)}}\n    |opponent2={{TeamOpponent|Crazy Raccoon}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M9={{Match\n    |date=2025-09-14 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|T1}}\n    |opponent2={{TeamOpponent|WAE}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n}}\n{{box|break|padding=2em}}\n\n==={{HiddenSort|Week 4}}===\n{{Matchlist|id=f41lsUPNte|title=Week 4|matchsection=Week 4|collapsed=false\n|M1header=September 19\n|M1={{Match\n    |bestof=5\n    |date=2025-09-19 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|T1}}\n    |opponent2={{TeamOpponent|ZETA DIVISION}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M2={{Match\n    |date=2025-09-19 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|WAE}}\n    |opponent2={{TeamOpponent|ONSIDE GAMING}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M3={{Match\n    |date=2025-09-19 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Team Falcons}}\n    |opponent2={{TeamOpponent|Cheeseburger (Korean team)}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M4header=September 20\n|M4={{Match\n    |date=2025-09-20 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Crazy Raccoon}}\n    |opponent2={{TeamOpponent|Mir Gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M5={{Match\n    |date=2025-09-20 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ZETA DIVISION}}\n    |opponent2={{TeamOpponent|WAE}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M6={{Match\n    |date=2025-09-20 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|ONSIDE GAMING}}\n    |opponent2={{TeamOpponent|Old Ocean}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M7header=September 21\n|M7={{Match\n    |date=2025-09-21 - 17:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Cheeseburger (Korean team)}}\n    |opponent2={{TeamOpponent|Mir Gaming}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M8={{Match\n    |date=2025-09-20 - 18:30 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|T1}}\n    |opponent2={{TeamOpponent|Team Falcons}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n|M9={{Match\n    |date=2025-09-20 - 20:00 {{Abbr/KST}}\n    |afreeca=owesports|vod=\n    |caster1=|caster2=\n    |opponent1={{TeamOpponent|Old Ocean}}\n    |opponent2={{TeamOpponent|Crazy Raccoon}}\n    |map1={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map2={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map3={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map4={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |map5={{Map|map=|mode=|score1=|score2=|winner=\n        |t1b1=|t2b1=|banstart=}}\n    |mvp=\n    }}\n}}\n{{box|end|padding=2em}}"""

	page_content = f"{page_content}"  # convert \n to newlines
	#log.info(page_content)

	wikicode = mwparserfromhell.parse(page_content)

	templates = wikicode.filter_templates()
	for template in templates:
		if template.name.strip() == "Match":
			log.info(template)
			team1_name = param_from_template_name(template, "opponent1")
			log.info(team1_name)
			team2_name = param_from_template_name(template, "opponent2")
			log.info(team2_name)

			date_code = template.get("date").value
			date_str = date_code.nodes[0].strip()
			date_timezone = date_code.nodes[1].name
			date_timezone = date_timezone.split("/")[1]

			timezone_obj = get_timezone(date_timezone)
			timezone_datetime = datetime.strptime(date_str, "%Y-%m-%d - %H:%M").replace(tzinfo=timezone_obj)

			game_datetime = timezone_datetime.astimezone(get_timezone("UTC"))
			log.info(game_datetime)

			team1_wins, team2_wins, total_maps = 0, 0, 0
			for map_num in range(1, 15):
				if not template.has(f"map{map_num}"):
					break
				total_maps += 1
				map_code = template.get(f"map{map_num}").value
				map_template = map_code.filter_templates()[0]
				map_winner = map_template.get("winner").value.strip()
				if map_winner:
					if map_winner == "1":
						team1_wins += 1
					elif map_winner == "2":
						team2_wins += 1
					else:
						log.info(f"something went wrong: {map_winner}")

			game_complete = False
			if team1_wins > total_maps / 2 or team2_wins > total_maps / 2:
				if team1_wins > team2_wins:
					game_complete = True
					log.info(f"{team1_name} wins {team1_wins} to {team2_wins}")
				elif team1_wins < team2_wins:
					game_complete = True
					log.info(f"{team2_name} wins {team2_wins} to {team1_wins}")
				else:
					log.info(f"Something's wrong. Wins greater than half maps, but still tied")
			elif team1_wins + team2_wins > 0:
				log.info(f"Game in progress")
			elif team1_wins + team2_wins == 0:
				log.info(f"Game not started")
			else:
				log.info(f"Something went wrong determining winner")



	sys.exit()

	teams = {}
	for team_name in re.findall(r"\|team\d+=(.+?)\n", page_content, flags=re.IGNORECASE):
		log.info(f"team: {team_name}")
		if team_name.lower() not in teams:
			teams[team_name.lower()] = team_name

	date_pattern = re.compile(r"\|date=(.+?)\n", flags=re.IGNORECASE)
	team1_pattern = re.compile(r"\|opponent1={{TeamOpponent\|(.+?)}}\n", flags=re.IGNORECASE)
	team2_pattern = re.compile(r"\|opponent2={{TeamOpponent\|(.+?)}}\n", flags=re.IGNORECASE)
	maps_pattern = re.compile(r"\|map(\d+)=.+winner=(\d*)", flags=re.IGNORECASE)
	match_start = -1
	while True:
		match_start = page_content.find("{{Match\n", match_start + 1)
		if match_start == -1:
			break
		log.info(f"Match at {match_start}")
		date_match = date_pattern.search(page_content, match_start)
		if date_match:
			date_string = date_match.group(1)
			log.info(date_string)


		team1_match = team1_pattern.search(page_content, match_start)
		team1_name = None
		if team1_match:
			team1_name = team1_match.group(1).lower()
			if team1_name in teams:
				log.info(teams[team1_name])
			else:
				log.info(f"{team1_name} not found")
		team2_match = team2_pattern.search(page_content, match_start)
		team2_name = None
		if team2_match:
			team2_name = team2_match.group(1).lower()
			if team2_name in teams:
				log.info(teams[team2_name])
			else:
				log.info(f"{team2_name} not found")

		prev_map_num, team1_wins, team2_wins, total_maps = 0, 0, 0, 0
		for map_num, map_winner in maps_pattern.findall(page_content, match_start):
			map_num_int = int(map_num)
			if map_num_int < prev_map_num:
				break
			prev_map_num = map_num_int
			total_maps += 1
			if map_winner == "1":
				team1_wins += 1
			elif map_winner == "2":
				team2_wins += 1

			log.info(f"{map_num}: {map_winner} : {team1_wins}|{team2_wins} : {total_maps}")

		if team1_wins > total_maps / 2 or team2_wins > total_maps / 2:
			if team1_wins > team2_wins:
				log.info(f"{team1_name} wins {team1_wins} to {team2_wins}")
			elif team1_wins < team2_wins:
				log.info(f"{team2_name} wins {team2_wins} to {team1_wins}")
			else:
				log.info(f"Something's wrong. Wins greater than half maps, but still tied")
		elif team1_wins + team2_wins > 0:
			log.info(f"Game in progress")
		elif team1_wins + team2_wins == 0:
			log.info(f"Game not started")
		else:
			log.info(f"Something went wrong determining winner")





	# matches = re.findall(r"\{\{Match\n", page_content, flags=re.IGNORECASE)
	# for match in matches:
	# 	log.info(match)


	log.info(f"done")





