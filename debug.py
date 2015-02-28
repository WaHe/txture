from __init__ import app
from settings import set_secrets

set_secrets(app)
app.debug = True
app.run(host='0.0.0.0')
