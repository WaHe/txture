class State(object):
    UNKNOWN = 'unknown'
    UNINITIALIZED = 'uninitialized'
    WAIT = 'wait'
    VALID_REQUEST = 'valid_request'


state_set = {State.UNKNOWN, State.UNINITIALIZED, State.WAIT, State.VALID_REQUEST}
