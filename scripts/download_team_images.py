import os

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
	page_url = "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/Asia/Stage_1/Korea"
	categories = ["ASIA"]

	category_mapping = {
		"OWL": "Overwatch League Teams",
		"OWWC": "Overwatch World Cup",
		"NA": "OWCS NA",
		"EU": "OWCS EU",
		"ASIA": "OWCS Asia",
		"College": "Collegiate",
		"Legacy": "Legacy Team Flairs",
	}
	category_names = []
	for category in categories:
		category_names.append(category_mapping[category])
	output_folder = r"C:\Users\greg\Downloads\flairs"
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	# new_flair_base_url = "http://localhost:5000/flairsheets/new?"
	# edit_flair_base_url = "http://localhost:5000/flairsheets/edit/"
	new_flair_base_url = "https://rcompetitiveoverwatch.com/flairsheets/new?"
	edit_flair_base_url = "https://rcompetitiveoverwatch.com/flairsheets/edit/"

	flairs_response = requests.get(url="http://rcompetitiveoverwatch.com/static/data/flairs.json",	headers={'User-Agent': "team_parser"}, timeout=5)
	json_data = json.loads(flairs_response.text)
	category_existing_flairs = {}
	category_existing_flairs_names = {}
	all_flairs = {}
	all_flairs_names = {}
	for flair_short_name, flair in json_data.items():
		all_flairs[flair['short_name']] = flair
		all_flairs_names[flair['name']] = flair
		if flair['category'] in category_names:
			category_existing_flairs[flair['short_name']] = flair
			category_existing_flairs_names[flair['name']] = flair

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
			"short_name": team_name.lower().replace(' ', '-').replace('.', '-'),
			"name": team_name,
		}
		if len(category_names) == 1:
			flair["category"] = category_names[0]
		liquipedia_flairs[flair["short_name"]] = flair

		log.info(f"Found team on liquipedia: {team_name}")

		img_data = requests.get(f"https://liquipedia.net{team_image}").content
		with open(f'{output_folder}/{flair["short_name"]}.png', 'wb') as handler:
			handler.write(img_data)

	log.info(f"---------------------------------------------")

	for flair_short_name, flair in liquipedia_flairs.items():
		reddit_flair = category_existing_flairs.get(flair['short_name']) or category_existing_flairs_names.get(flair['name'])
		if not reddit_flair:
			reddit_flair = all_flairs.get(flair['short_name']) or all_flairs_names.get(flair['name'])
			if not reddit_flair:
				new_flair_url = \
					f"{new_flair_base_url}" \
					f"short_name={flair['short_name']}&" \
					f"flairsheet=teams&" \
					f"name={(flair['name'].replace(' ', '%20'))}" \
					f"{('&category='+(flair['category'].replace(' ', '%20')) if 'category' in flair else '')}"
				log.info(f"{flair['name']} doesn't exist: {new_flair_url}")

			elif 'category' in flair:
				log.info(f"{flair['name']} wrong category {reddit_flair['category']} to {flair['category']}: {edit_flair_base_url}{reddit_flair['id']}")

			else:
				log.info(f"{flair['name']} in category {reddit_flair['category']}: {edit_flair_base_url}{reddit_flair['id']}")

		else:
			log.info(f"{flair['name']} correct, check image: {edit_flair_base_url}{reddit_flair['id']}")

	if len(category_names) == 1:
		for flair_short_name, flair in category_existing_flairs.items():
			if flair_short_name not in liquipedia_flairs:
				log.info(f"{flair['name']} on flair site but not liquipedia: {edit_flair_base_url}{flair['id']}")
