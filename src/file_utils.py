import pickle
import os

import globals


def save_state(events):
	state = {
		'events': events
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

	return state['events']