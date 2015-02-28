from __init__ import app
from secrets import set_secrets

set_secrets(app)
app.debug = True
app.run()
