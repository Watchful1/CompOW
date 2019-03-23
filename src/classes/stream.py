from urllib.parse import urlparse

import mappings


def extract_url_name(url):
	try:
		parsed_url = urlparse(url)
	except Exception as err:
		return url

	if "twitch.tv" in parsed_url.netloc.lower():
		last_slash = url.rfind("/", 0, len(url) - 1)
		if url[-1] == '/':
			return url[last_slash + 1:-1]
		else:
			return url[last_slash + 1:]
	else:
		return parsed_url.netloc


class Stream:
	def __init__(self, url, language=None, name=None):
		self.url = url
		self.language = language
		if name is None:
			self.name = extract_url_name(url)
		else:
			self.name = name

	def __eq__(self, other):
		return self.url == other.url

	def __lt__(self, other):
		if other is None:
			return False
		self_ranking = mappings.stream_ranking(self.url, self.language)
		other_ranking = mappings.stream_ranking(self.url, self.language)
		return self_ranking < other_ranking
