from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from secrets import database_url
import twilio.rest
import twilio.twiml
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)


class User(db.Model):
    phone_number = db.Column(db.String(16), primary_key=True)
    email = db.Column(db.String, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    delivery_addresses = db.relationship('Address', backref='user', lazy='joined')

    def __init__(self, phone_number):
        self.phone_number = phone_number

    def __repr__(self):
        return '<User %r>' % self.phone_number


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address_line_1 = db.Column(db.String, nullable=False)
    address_line_2 = db.Column(db.String)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String, nullable=False)
    user_phone_number = db.Column(db.String, db.ForeignKey('user.phone_number'))

    def __init__(self, name, address_line_1, city, state, zip_code, user_phone_number, address_line_2=None):
        self.name = name
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.user_phone_number = user_phone_number


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


if __name__ == "__main__":
    app.run()



