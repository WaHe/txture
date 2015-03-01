from requests import HTTPError
from states import State
from ordrin_helpers import match_food_item, place_order
import twilio.twiml
from helpers.nlp_parse import nlp_parse

# TODO: fix the results of all of these functions


def calculate_tip(price):
    return price * 0.15


def unknown_processor(message, user, conversation, db):
    return State.UNINITIALIZED


def uninitialied_processor(message, user, conversation, db):
    return State.VALID_REQUEST


def wait_processor(message, user, conversation, db):
    nouns, preps = nlp_parse(message)
    matched_food = match_food_item(nouns, preps, user.delivery_addresses[0])
    if nouns is not None and preps is not None:
        conversation.state = State.VALID_REQUEST
        resp = twilio.twiml.Response()
        price = matched_food['price'] / 100.0
        resp.message("How does a " + matched_food['name'] + " from " + matched_food['restaurant_name']
                     + ' Sound? That would cost $' + "%.2f" % (price + calculate_tip(price)) + '.')
        conversation.food_string = matched_food['item'] + '/1,' + matched_food['options']
        conversation.price = matched_food['price']
        conversation.restaurant_id = matched_food['restaurant_id']
        conversation.restaurant_name = matched_food['restaurant_name']
        db.session.commit()
        return resp
    else:
        resp = twilio.twiml.Response()
        resp.message("Sorry, I had trouble understanding that... Try a simpler request," +
                     " like \"May I obtain a burrito?\"")
        return resp


def valid_processor(message, user, conversation, db):
    if message == 'yes':
        conversation.state = State.WAIT
        resp = twilio.twiml.Response()
        try:
            print ((conversation.price / 100) * 0.15)
            print conversation.food_string
            place_order(conversation.restaurant_id, conversation.food_string,
                        "%.2f" % ((conversation.price / 100) * 0.15),
                        user, user.delivery_addresses[0])
            resp.message("Awesome! That should be delivered soon.")
        except HTTPError as e:
            resp.message("Sorry, there was an issue placing your order :/")
            print e.response.text
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
