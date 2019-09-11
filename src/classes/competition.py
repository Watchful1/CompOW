class Competition:
	def __init__(
			self,
			name,
			discord_minutes_ahead=None,
			discord_roles=[],
			discord_channel="348939546878017536",
			post_match_threads=False,
			post_minutes_ahead=15,
			day_in_title=False,
			prediction_thread_minutes_ahead=None,
			leave_thread_minutes=None
			):
		self.name = name
		if discord_minutes_ahead is not None and discord_minutes_ahead > post_minutes_ahead:
			self.discord_minutes_ahead = post_minutes_ahead
		else:
			self.discord_minutes_ahead = discord_minutes_ahead
		self.discord_roles = discord_roles
		self.discord_channel = discord_channel
		self.post_match_threads = post_match_threads
		self.post_minutes_ahead = post_minutes_ahead
		self.day_in_title = day_in_title
		self.prediction_thread_minutes_ahead = prediction_thread_minutes_ahead
		self.leave_thread_minutes = leave_thread_minutes

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name
