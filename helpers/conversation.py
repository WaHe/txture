from states import State

# TODO: fix the results of all of these functions
def unknown_processor(message, user, conversation):
    return State.UNINITIALIZED


def uninitialied_processor(message, user, conversation):
    return State.VALID_REQUEST


def wait_processor(message, user, conversation):
    return State.WAIT


def valid_processor(message, user, conversation):
    return State.WAIT

processors = {
    State.UNKNOWN: unknown_processor,
    State.UNINITIALIZED: uninitialied_processor,
    State.WAIT: wait_processor,
    State.VALID_REQUEST: valid_processor

}


def process_input(state, message, user, conversation):
    return processors[state](message, user, conversation)
