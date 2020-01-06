import pickle
import os

import static


def save_state_debug(state):
	save_state(state['events'], state['stickies'], state['flairs'])


def save_state(events, stickies, flairs):
	state = {
		'events': events,
		'stickies': stickies,
		'flairs': flairs
	}
	with open(static.STATE_FILENAME, 'wb') as handle:
		pickle.dump(state, handle)


def load_state(reset=False):
	if reset or not os.path.exists(static.STATE_FILENAME):
		state = {}
	else:
		with open(static.STATE_FILENAME, 'rb') as handle:
			state = pickle.load(handle)
	if 'events' not in state:
		state['events'] = []
	if 'stickies' not in state:
		state['stickies'] = {'current': [None] * 2, 'saved': []}
	if 'flairs' not in state:
		state['flairs'] = {}

	return state
