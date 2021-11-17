from server import db

class Picture(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250), index=True, unique=False)
    painter = db.Column(db.String(150), index=True, unique=False)
    image = db.Column(db.String(300), index=True, unique=False)

    def __repr__(self):
        return '<Picture {} {} {} {}>'.format(self.id, self.title, self.painter, self.image)