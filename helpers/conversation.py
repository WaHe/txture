from states import State
import twilio.twiml
# TODO: fix the results of all of these functions


def unknown_processor(message, user, conversation, db):
    return State.UNINITIALIZED


def uninitialied_processor(message, user, conversation, db):
    return State.VALID_REQUEST


def wait_processor(message, user, conversation, db):
    if message == 'yes':
        conversation.state = State.VALID_REQUEST
        resp = twilio.twiml.Response()
        resp.message("YAY! This is a valid request! I can do something with this.")
        db.session.commit()
        return resp
    else:
        resp = twilio.twiml.Response()
        resp.message("Sorry, I had trouble understanding that... Try a simpler request.")
        return resp


def valid_processor(message, user, conversation, db):
    if message == 'yes':
        conversation.state = State.WAIT
        resp = twilio.twiml.Response()
        resp.message("YAY! This is the part where I order you shit. Good work!")
        db.session.commit()
        return resp
    elif message == 'no':
        conversation.state = State.WAIT
        resp = twilio.twiml.Response()
        resp.message("Ok! I just cancelled your order.")
        db.session.commit()
        return resp
    else:
        resp = twilio.twiml.Response()
        resp.message("Sorry but I need a clear 'yes' or 'no' from you. What'll it be?")
        return resp

processors = {
    State.UNKNOWN: unknown_processor,
    State.UNINITIALIZED: uninitialied_processor,
    State.WAIT: wait_processor,
    State.VALID_REQUEST: valid_processor

}


def process_input(message, user, conversation, db):
    return processors[conversation.state](message, user, conversation, db)
