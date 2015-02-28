from __init__ import app, db, User
from flask import request
import twilio.rest
import twilio.twiml
import random

@app.route("/")
def index():
    db.session.add(User(str(random.random())))
    db.session.commit()
    return "Hello, I love Digital Ocean!"

@app.route("/users")
def users():
    uses = User.query.all()
    return str(uses)


@app.route("/twiltest")
def twiltest():
    # Find these values at https://twilio.com/user/account
    client = twilio.rest.TwilioRestClient(app.twilio_sid, app.twilio_token)
    message = client.messages.create(to="+14157862965", from_=app.twilio_number,
                                     body="Hello there!")
    return "sent a message!"


@app.route("/tw", methods=['POST'])
def twilio_route():
    """Respond to incoming calls with a simple text message."""
    from_number = request.values.get('From', None)
    resp = twilio.twiml.Response()
    resp.message("Hello, you! That was from " + from_number)
    resp.message("here's another message")
    return str(resp)
