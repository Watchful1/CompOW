class DiscordNotification:
	def __init__(
			self,
			type,
			minutes_ahead,
			roles=[],
			channel=None
			):
		self.type = type
		self.minutes_ahead = minutes_ahead
		self.roles = roles
		self.channel = channel


class Competition:
	def __init__(
			self,
			name,
			discord=None,
			post_match_threads=False,
			post_minutes_ahead=15,
			day_in_title=False,
			prediction_thread_minutes_ahead=None,
			leave_thread_minutes=None
			):
		self.name = name
		self.discord = discord
		self.post_match_threads = post_match_threads
		self.post_minutes_ahead = post_minutes_ahead
		self.day_in_title = day_in_title
		self.prediction_thread_minutes_ahead = prediction_thread_minutes_ahead
		self.leave_thread_minutes = leave_thread_minutes

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name
