from __init__ import db, User

db.drop_all()
db.create_all()
u = User("+14157862965")
db.session.add(u)
db.session.commit()
