class Basic(object):
    pass

State = Basic()
State.UNKNOWN = 'unknown'
State.UNINITIALIZED = 'uninitialized'
State.WAIT = 'wait'
State.VALID_REQUEST = 'valid_request'

state_set = {State.UNKNOWN, State.UNINITIALIZED, State.WAIT, State.VALID_REQUEST}
