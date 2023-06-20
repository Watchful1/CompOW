import discord_logging
from lxml import etree
import requests
import json

log = discord_logging.init_logging()


def get_text_from_paths(base_node, paths):
	for path in paths:
		items = base_node.xpath(path)
		if len(items):
			result = items[0].strip().encode('ascii', 'ignore').decode("utf-8")
			if result:
				return result
	return None


if __name__ == "__main__":
	page_url = "https://liquipedia.net/overwatch/Overwatch_Contenders/2023/Summer_Series/Australia"
	category = "AU"

	categories = {
		"OWL": "Overwatch League Teams",
		"OWWC": "Overwatch World Cup",
		"NA": "Overwatch Contenders NA",
		"EU": "Overwatch Contenders EU",
		"KR": "Overwatch Contenders KR",
		"CN": "Overwatch Contenders CN",
		"AU": "Overwatch Contenders AU",
		"SEA": "Overwatch Contenders SEA",
		"College": "Collegiate",
		"Legacy": "Legacy Team Flairs",
	}
	category_name = categories[category]
	output_folder = r"C:\Users\greg\Downloads\flairs"
	new_flair_base_url = "https://rcompetitiveoverwatch.com/flairsheets/new?"
	edit_flair_base_url = "https://rcompetitiveoverwatch.com/flairsheets/edit/"

	flairs_response = requests.get(url="http://rcompetitiveoverwatch.com/static/data/flairs.json",	headers={'User-Agent': "team_parser"}, timeout=5)
	json_data = json.loads(flairs_response.text)
	category_existing_flairs = {}
	all_flairs = {}
	for flair_short_name, flair in json_data.items():
		all_flairs[flair['short_name']] = flair
		if flair['category'] == category_name:
			category_existing_flairs[flair['short_name']] = flair

	page_result = requests.get(page_url, headers={'User-Agent': "team_parser"}, timeout=5)
	tree = etree.fromstring(page_result.text, etree.HTMLParser())

	liquipedia_flairs = {}
	team_nodes = tree.xpath("//div[@class='teamcard toggle-area toggle-area-1']")
	for node in team_nodes:
		team_name = get_text_from_paths(node, [".//center/a/text()"])
		team_image = get_text_from_paths(node, [".//div[@class='teamcard-inner']/table[@class='wikitable wikitable-bordered logo']/tbody/tr/td/span/div/div/img/@src"])
		if team_name is None or "default_lightmode" in team_image:
			continue
		flair = {
			"short_name": team_name.lower().replace(' ', '-'),
			"name": team_name,
			"category": category_name,
		}
		liquipedia_flairs[flair["short_name"]] = flair

		log.info(f"{team_name}")

		img_data = requests.get(f"https://liquipedia.net{team_image}").content
		with open(f'{output_folder}/{flair["short_name"]}.png', 'wb') as handler:
			handler.write(img_data)

	for flair_short_name, flair in liquipedia_flairs.items():
		if flair['short_name'] not in category_existing_flairs:
			if flair['short_name'] not in all_flairs:
				new_flair_url = \
					f"{new_flair_base_url}" \
					f"short_name={flair['short_name']}&" \
					f"flairsheet=teams&" \
					f"name={(flair['name'].replace(' ', '%20'))}&" \
					f"category={(flair['category'].replace(' ', '%20'))}"
				log.info(f"{flair['name']} doesn't exist: {new_flair_url}")

			else:
				log.info(f"{flair['name']} wrong category {all_flairs[flair['short_name']]['category']} to {flair['category']}: {edit_flair_base_url}{all_flairs[flair['short_name']]['id']}")

	for flair_short_name, flair in category_existing_flairs.items():
		if flair_short_name not in liquipedia_flairs:
			log.info(f"{flair['name']} on flair site but not liquipedia: {edit_flair_base_url}{flair['id']}")
