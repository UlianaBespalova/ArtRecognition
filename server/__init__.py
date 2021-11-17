from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from numpy import genfromtxt
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

fit_vecs = genfromtxt('server/data/vectors.csv', delimiter='|')
knn = NearestNeighbors(metric='cosine', algorithm='brute')
knn.fit(fit_vecs)


from server import routes, models



def getBD():
    str = ''''''
    items = str.split('\n')
    for i in items:
        words = i.split(' | ')
        print("Picture(title='{}', painter='{}', image='{}')".format(words[0], words[1], words[2]))
