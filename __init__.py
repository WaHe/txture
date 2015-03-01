from flask import Flask, request, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy
from urllib import urlencode
from collections import OrderedDict
from hashlib import sha256
from requests import HTTPError
from base64 import b64encode
from twilio.util import RequestValidator

import twilio.rest
import twilio.twiml
import datetime

from helpers.secure_update import create_queries, test_hash
from helpers.messages import init_confirm
from helpers.reformat_phone import reformat_phone
from states import State
from setup_api import ordrin_api
import settings



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
db = SQLAlchemy(app)


class User(db.Model):
    phone_number = db.Column(db.String(16), primary_key=True)
    initialized = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, default='')
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    delivery_addresses = db.relationship('Address', backref='user', lazy='joined')
    conversations = db.relationship('Conversation', backref='user', lazy='joined')

    def __init__(self, phone_number):
        self.phone_number = phone_number

    def __repr__(self):
        return '<User %r>' % self.phone_number


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address_line_1 = db.Column(db.String, nullable=False)
    address_line_2 = db.Column(db.String)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String, nullable=False)
    user_phone_number = db.Column(db.String, db.ForeignKey('user.phone_number'))

    def __init__(self, name):
        self.name = name


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String, nullable=False, default=State.UNKNOWN)
    price = db.Column(db.Integer)
    deliverer_phone_number = db.Column(db.String)
    delivery_time = db.Column(db.Integer)
    delivery_address = db.Column(db.Integer, db.ForeignKey('address.id'))
    food_string = db.Column(db.String)
    restaurant_id = db.Column(db.String)
    restaurant_name = db.Column(db.String)

    user_phone_number = db.Column(db.String, db.ForeignKey('user.phone_number'), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_phone_number):
        self.user_phone_number = user_phone_number


def get_update_link(phone_number, password):
    initial_url = settings.base_url + "/u"
    p = phone_number
    e, h = create_queries(p, password, settings.secret_reset_key)
    query_string = urlencode(OrderedDict(p=p, e=e, h=h))
    return initial_url + "?" + query_string


@app.route("/")
def index():
    # db.session.add(User(str(random.random())))
    # db.session.commit()
    return render_template('index.html')


@app.route("/users")
def users():
    uses = User.query.all()
    return str(uses)


from conversation import process_input


@app.route("/tw", methods=['POST'])
def twilio_receive():
    """Respond to incoming text messages"""
    validator = RequestValidator(settings.twilio_token)
    sig_header = request.headers.get('X-Twilio-Signature', '')
    if not validator.validate(request.url, request.form, sig_header):
        print "This request is not valid!"
        if settings.require_twilio_validation:
            return abort(401, 'Request signature was not valid.')
    else:
        print "This is a valid request :D"

    from_number = request.values.get('From', None)
    user = User.query.filter_by(phone_number=from_number).first()
    if user is None:
        # Add a new user if this phone number isn't already in the database
        user = User(from_number)
        db.session.add(user)
        db.session.commit()
    if not user.initialized:
        resp = twilio.twiml.Response()
        resp.message("Hi! welcome to txture. Set up your info here: " + get_update_link(from_number, user.password))
        return str(resp)
    if len(user.conversations) > 0:
        conv = user.conversations[0]  # TODO: there may be an issue here
    else:
        conv = None
    resp = process_input(request.values.get('Body'), user, conv, db)
    return str(resp)


def set_user_values(user, data):
    user.first_name = data.get('first_name', None)
    user.last_name = data.get('last_name', None)
    user.email = data.get('email', None)
    if data.get('password', None) is None:
        user.password = None
    else:
        m = sha256()
        m.update(request.form['password'])
        user.password = b64encode(m.digest())


def set_address_values(address, data, prefix):
    address.address_line_1 = data.get(prefix + 'address_line_1', None)
    address.address_line_2 = data.get(prefix + 'address_line_2', None)
    address.city = data.get(prefix + 'city', None)
    address.state = data.get(prefix + 'state', None)
    address.zip_code = data.get(prefix + 'zip_code', None)


@app.route("/u", methods=['GET', 'POST'])
def update_form():
    phone_number = request.args.get('p')
    expiration_time = request.args.get('e')
    request_hash = request.args.get('h')
    user = User.query.filter_by(phone_number=phone_number).first()

    # Fail if the user wasn't found
    if user is None:
        return render_template('url-failure.html')
    password = user.password if user.password is not None else ''

    # Fail if the url was invalid
    if not test_hash(phone_number, expiration_time, password, request_hash, settings.secret_reset_key):
        return render_template('url-failure.html')

    error = None
    d = Address("default")
    b = Address("billing")
    if request.method == 'POST':
        if not user.initialized:
            client = twilio.rest.TwilioRestClient(settings.twilio_sid, settings.twilio_token)
            print "got here"
            print request.form['email']
            print request.form['password']
            print request.form['first_name']
            print request.form['last_name']
            print "got here!"
            set_user_values(user, request.form)
            set_address_values(d, request.form, "delivery_")

            # Make sure the account doesn't exist before we try to create it
            try:
                ordrin_api.get_account_info(request.form.get('email', None), user.password)
            except HTTPError:
                try:
                    account_result = ordrin_api.create_account(user.email, user.password,
                                                               user.first_name, user.last_name)
                except HTTPError as e:
                    error = e.response.text
                    return render_template('u.html', user=user, delivery_address=d, billing_address=b, error=error)

            # Try creating the address
            try:
                ordrin_api.create_addr(user.email, d.name, user.phone_number.replace('+', '')[1:], d.zip_code,
                                       d.address_line_1, d.city, d.state, user.password, addr2=d.address_line_2)
            except HTTPError as e:
                error = e.response.text
                return render_template('u.html', user=user, delivery_address=d, billing_address=b, error=error)

            # Try creating the credit card
            try:
                expiry_string = request.form.get('expiry_month') + '/' + request.form.get('expiry_year', None)
                ordrin_api.create_cc(request.form.get('email', None),
                                     'default',
                                     request.form.get('card_number', None),
                                     request.form.get('security_code', None),
                                     expiry_string,
                                     request.form.get('billing_address_line_1', None),
                                     request.form.get('billing_city', None),
                                     request.form.get('billing_state', None),
                                     request.form.get('billing_zip_code', None),
                                     reformat_phone(user.phone_number),
                                     user.password,
                                     bill_addr2=request.form.get('billing_address_line_2', None)
                                     )
            except HTTPError as e:
                error = e.response.text
                return render_template('u.html', user=user, delivery_address=d, billing_address=b, error=error)
            d.user_phone_number = user.phone_number
            user.initialized = True

            # Set up the new conversation
            conv = Conversation(user.phone_number)
            conv.delivery_address = d.id
            conv.creation_date = datetime.datetime.utcnow()
            conv.state = State.WAIT
            db.session.add(d)
            db.session.add(conv)
            db.session.commit()
            client.messages.create(to=user.phone_number, from_=settings.twilio_number, body=init_confirm())
        return render_template('success.html')
    return render_template('u.html', user=user, delivery_address=d, billing_address=b, error=error)


@app.route("/success", methods=['GET'])
def success():
    return render_template('success.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')

