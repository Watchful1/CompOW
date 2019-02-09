import pickle
import os

import globals


def save_state(events, stickies):
	state = {
		'events': events,
		'stickies': stickies
	}
	with open(globals.STATE_FILENAME, 'wb') as handle:
		pickle.dump(state, handle)


def load_state(reset=False):
	if reset or not os.path.exists(globals.STATE_FILENAME):
		state = {}
	else:
		with open(globals.STATE_FILENAME, 'rb') as handle:
			state = pickle.load(handle)
	if 'events' not in state:
		state['events'] = []
	if 'stickies' not in state:
		state['stickies'] = {'current': [None] * 2, 'saved': []}

	return state['events'], state['stickies']
