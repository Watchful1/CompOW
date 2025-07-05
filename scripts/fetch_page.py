import requests
from fake_useragent import UserAgent
import urllib.request
import random

if __name__ == "__main__":
	#url = "https://liquipedia.net/overwatch/api.php?action=query&meta=siteinfo&titles=Overwatch_Champions_Series/2025/Asia/Stage_2/Japan&exportnowrap=true&format=json"
	url = "https://liquipedia.net/overwatch/Overwatch_Champions_Series/2025/Midseason_Championship"

	user_agent = UserAgent().chrome
	print(user_agent)

	# proxy = FreeProxy(https=True).get()
	# print(proxy)
	#
	# proxies = {"https": proxy}
	# headers = {'User-Agent': user_agent}
	# result = requests.get(url, headers=headers, proxies=proxies)
	#
	# result_json = result.json()
	# print(result_json["query"]["export"]["*"])


	username = 'xxxxxxxxxx'
	password = 'yyyyyyyyyyyyyyyy'
	country = 'US'

	proxy_url = f'http://customer-{username}-cc-US:{password}@pr.oxylabs.io:7777'

	proxies = {"https": proxy_url, "http": proxy_url}
	headers = {'User-Agent': user_agent}
	result = requests.get(url, headers=headers, proxies=proxies)

	result_json = result.content
	print(result_json)


	# username = 'USERNAME'
	# password = 'PASSWORD'
	#entry = ('http://customer-%s:%s@pr.oxylabs.io:7777' % (username, password))
	# query = urllib.request.ProxyHandler({
	# 	'http': entry,
	# 	'https': entry,
	# })
	# execute = urllib.request.build_opener(query)
	# print(execute.open('https://ip.oxylabs.io/location').read())
