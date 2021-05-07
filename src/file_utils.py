import pickle
import os

import static


def save_state_debug(state):
	save_state(state['events'], state['stickies'], state['flairs'], state['keys'])


def save_state(events, stickies, flairs, keys):
	state = {
		'events': events,
		'stickies': stickies,
		'flairs': flairs,
		'keys': keys
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
	if 'keys' not in state:
		state['keys'] = {'prediction_thread': None}

	for event in state['events']:
		if not hasattr(event, 'creation_time'):
			event.creation_time = static.utcnow()

		for match in event.matches:
			if not hasattr(match, 'owl_id'):
				match.owl_id = None
			if not hasattr(match, 'owl_complete'):
				match.owl_complete = None
			if not hasattr(match, 'owl_week'):
				match.owl_week = None

	return state
