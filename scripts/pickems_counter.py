import discord_logging
import requests
from collections import defaultdict

log = discord_logging.init_logging(debug=True)

if __name__ == "__main__":
	urls = [
		# "https://pickem.overwatchleague.com/api/leaderboards?slug=reddit-cow&season=2023&stage=summer-stage&event=summer-ea",
		"https://pickem.overwatchleague.com/api/leaderboards?slug=reddit-cow&season=2023&stage=spring-stage",
		"https://pickem.overwatchleague.com/api/leaderboards?slug=reddit-cow&season=2023&stage=summer-stage",
		"https://pickem.overwatchleague.com/api/leaderboards?slug=reddit-cow&season=2023&stage=midseason-madness",
		"https://pickem.overwatchleague.com/api/leaderboards?slug=reddit-cow&season=2023&stage=playoffs",
	]

	users = defaultdict(int)
	for url in urls:
		for user in requests.get(url).json():
			if user['points'] is not None:
				users[user['username']] += int(user['points'])

	i = 0
	prev_points = None
	winners = []
	winner_points = None
	second = []
	second_points = None
	for user in sorted(users, key=users.get, reverse=True):
		points = users[user]
		log.info(f"{user}: {points}")

		if len(winners) == 0:
			winners.append(user)
			winner_points = points
		elif points == winner_points:
			winners.append(user)
		elif len(second) == 0:
			second.append(user)
			second_points = points
		elif points == second_points:
			second.append(user)
		i += 1
		if i >= 7:
			break

	stage = "Summer Stage"

	if len(winners) > 1:
		log.info(f"The winners of the Pick'ems for {stage} are {' and '.join(winners)}! Get your predictions in now!")
	else:
		log.info(f"The winner of the Pick'ems for {stage} is {' and '.join(winners)}! Get your predictions in now!")

	log.info(
		f'''{' and '.join(winners)} had {winner_points} points. That is their battlenet tag, so if anyone knows their reddit username or twitter handle, please let them know about this thread.

{' and '.join(winners)} please link your battlenet accounts in the [flair site](https://rcompetitiveoverwatch.com/redditflair), which we'll use as proof. If you don't play ranked, you won't be able to verify your rank in the flair site, but you only need to click "Verify your rank" and then "Sign in with Blizzard". And then comment below to get your prize. If the winners don't show up in the next few days, we'll go to the second place which is {' and '.join(second)} with {second_points} points.

We will have a prize for the top scorer EACH WEEK as well as best playoff bracket and best overall at the end of the tournament. You can [join the subreddit leaderboard here](https://pickem.overwatchleague.com/en-us/leaderboard/reddit-cow/2023) by clicking "Join a leaderboard" and putting in the code `reddit-cow`.'''
	)

