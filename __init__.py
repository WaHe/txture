from flask import Flask, request, render_template, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from secrets import database_url
from helpers.validation import validate_zip_code
from helpers.secure_update import create_queries, test_hash
import twilio.rest
import twilio.twiml
from urllib import urlencode
from collections import OrderedDict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)


class User(db.Model):
    phone_number = db.Column(db.String(16), primary_key=True)
    initialized = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    delivery_addresses = db.relationship('Address', backref='user', lazy='joined')

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


def get_update_link():
    initial_url = app.base_url + "/u"
    p = "+14157862965"
    e, h = create_queries(p, '', app.secret_reset_key)
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


@app.route("/twiltest")
def twiltest():
    # Find these values at https://twilio.com/user/account
    client = twilio.rest.TwilioRestClient(app.twilio_sid, app.twilio_token)
    message = client.messages.create(to="+14157862965", from_=app.twilio_number,
                                     body="Hello there!")
    return "sent a message!"


@app.route("/tw", methods=['POST'])
def twilio_receive():
    """Respond to incoming calls with a simple text message."""
    from_number = request.values.get('From', None)
    resp = twilio.twiml.Response()
    resp.message("Hello, you! That was from " + from_number)
    resp.message("here's another message")
    return str(resp)

@app.route("/u", methods=['GET', 'POST'])
def update_form():
    phone_number = request.args.get('p')
    expiration_time = request.args.get('e')
    request_hash = request.args.get('h')
    user = User.query.filter_by(phone_number=phone_number).first()
    password = user.password if user.password is not None else ''
    if user is None or not test_hash(phone_number, expiration_time, password, request_hash, app.secret_reset_key):
        return render_template('url-failure.html')

    error = None
    d = Address("default")
    b = Address("billing")
    if request.method == 'POST':
        if validate_zip_code(request.form['delivery_zip_code']):
            if not user.initialized:
                pass  # TODO: go to wait state
            return render_template('success.html')
        else:
            error = "Invalid zip code!"
    return render_template('u.html', user=user, delivery_address=d, billing_address=b, error=error)


@app.route("/success", methods=['GET'])
def success():
    return render_template('success.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')



