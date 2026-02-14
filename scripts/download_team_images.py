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
	pages = [
		# ("NA", "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/NA/Stage_3"),
		# ("EU", "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/EMEA/Stage_3"),
		# ("KOREA", "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/Asia/Stage_3/Korea"),
		# ("CHINA", "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/China/Stage_3"),
		("JAPAN", "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/Asia/Stage_3/Japan"),
		("PACIFIC", "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/Asia/Stage_3/Pacific"),
		#("COLLEGE", "https://liquipedia.net/overwatch/Overwatch_Collegiate/Homecoming/Open/2025"),
	]

	category_mapping = {
		"OWL": "Overwatch League Teams",
		"OWWC": "Overwatch World Cup",
		"NA": "OWCS NA",
		"EU": "OWCS EU",
		"KOREA": "OWCS Korea",
		"CHINA": "OWCS China",
		"JAPAN": "OWCS Japan",
		"PACIFIC": "OWCS Pacific",
		"COLLEGE": "Collegiate",
		"Legacy": "Legacy Team Flairs",
	}
	category_names = set()
	for category, page_url in pages:
		category_names.add(category_mapping[category])
	output_folder = r"C:\Users\greg\Downloads\flairs"
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	output_folder_new = r"C:\Users\greg\Downloads\flairs\new"
	if not os.path.exists(output_folder_new):
		os.makedirs(output_folder_new)
	# new_flair_base_url = "http://localhost:5000/flairsheets/new?"
	# edit_flair_base_url = "http://localhost:5000/flairsheets/edit/"
	new_flair_base_url = "https://rcompetitiveoverwatch.com/flairsheets/new?"
	edit_flair_base_url = "https://rcompetitiveoverwatch.com/flairsheets/edit/"

	flairs_response = requests.get(url="http://rcompetitiveoverwatch.com/static/data/flairs.json",	headers={'User-Agent': "team_parser"}, timeout=5)
	json_data = json.loads(flairs_response.text)
	category_existing_flairs = {}
	all_flairs = {}
	all_flairs_names = {}
	for flair_short_name, flair in json_data.items():
		all_flairs[flair['short_name']] = flair
		all_flairs_names[flair['name']] = flair
		if flair['category'] in category_names:
			category_existing_flairs[flair['short_name']] = flair

	liquipedia_flairs = {}
	for category, page_url in pages:
		log.info(f"Downloading {category} from {page_url}")
		page_result = requests.get(page_url, headers={'User-Agent': "team_parser"}, timeout=5)
		tree = etree.fromstring(page_result.text, etree.HTMLParser())

		team_nodes = tree.xpath("//div[@class='teamcard toggle-area toggle-area-1']")
		for node in team_nodes:
			team_name = get_text_from_paths(node, [".//center/a/text()"])
			team_image = get_text_from_paths(node, [".//div[@class='teamcard-inner']/table[@class='wikitable wikitable-bordered logo']/tbody/tr/td/span/div/div/img/@src"])
			if team_name is None or "default_lightmode" in team_image:
				continue
			flair = {
				"short_name": team_name.lower().replace(' ', '-').replace('.', '-'),
				"name": team_name,
				"category": category_mapping[category],
			}
			liquipedia_flairs[flair["short_name"]] = flair

			log.info(f"Found team on liquipedia: {team_name}")

			# img_data = requests.get(f"https://liquipedia.net{team_image}").content
			# with open(f'{output_folder}/{flair["short_name"]}.png', 'wb') as handler:
			# 	handler.write(img_data)

	check_images, new_flairs, wrong_category, move_to_legacy = [], [], [], []
	for flair_short_name, flair in liquipedia_flairs.items():
		reddit_flair = all_flairs.get(flair['short_name']) or all_flairs_names.get(flair['name'])
		if not reddit_flair:
			# couldn't find existing flair
			new_flair_url = \
				f"{new_flair_base_url}" \
				f"short_name={flair['short_name']}&" \
				f"flairsheet=teams&" \
				f"name={(flair['name'].replace(' ', '%20'))}" \
				f"{('&category='+(flair['category'].replace(' ', '%20')) if 'category' in flair else '')}"
			new_flairs.append(f"{flair['name']} doesn't exist: {new_flair_url}")
			# move image into new folder
			#os.rename(f'{output_folder}/{flair["short_name"]}.png', f'{output_folder_new}/{flair["short_name"]}.png')
		elif reddit_flair["category"] != flair["category"]:
			# flair exists, but in wrong category
			wrong_category.append(f"{flair['name']} wrong category {reddit_flair['category']} to {flair['category']}: {edit_flair_base_url}{reddit_flair['id']}")
		else:
			check_images.append(f"{flair['name']} correct, check image: {edit_flair_base_url}{reddit_flair['id']}")

	for flair_short_name, flair in category_existing_flairs.items():
		if flair_short_name not in liquipedia_flairs:
			move_to_legacy.append(f"{flair['name']} on flair site but not liquipedia: {edit_flair_base_url}{flair['id']}")

	log.info(f"---------------------------------------------")

	log.info(f"Check that images are correct for {len(check_images)} flairs")
	for line in check_images:
		log.info(line)

	log.info(f"---------------------------------------------")

	log.info(f"Flairs in wrong category {len(wrong_category)}")
	for line in wrong_category:
		log.info(line)

	log.info(f"---------------------------------------------")

	log.info(f"Flairs not in any category, move to legacy {len(move_to_legacy)}")
	for line in move_to_legacy:
		log.info(line)

	log.info(f"---------------------------------------------")

	log.info(f"New flairs {len(new_flairs)}")
	for line in new_flairs:
		log.info(line)
