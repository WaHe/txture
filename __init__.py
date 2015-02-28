from flask import Flask
import twilio


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, I love Digital Ocean!"

@app.route("/twiltest")
def twiltest():
    # Find these values at https://twilio.com/user/account
    client = twilio.TwilioRestClient(app.twilio_sid, app.twilio_token)

    message = client.messages.create(to="+14157862965", from_=app.twilio_number,
                                     body="Hello there!")

@app.route("/tw", methods=['GET', 'POST'])
def twilio_route():
    """Respond to incoming calls with a simple text message."""
    resp = twilio.twiml.Response()
    resp.message("Hello, you!")
    return str(resp)

if __name__ == "__main__":
    app.run()



