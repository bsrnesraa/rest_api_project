import requests
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

URL = "https://geocode.search.hereapi.com/v1/geocode"
location = input("Enter the location here: ")  # taking user input

api_key = '0ynVo4wSiOEmbhx2_G8_2Pnj1uyECTL8h7PjlradGWg'  # Acquire from developer.here.com
PARAMS = {'apikey': api_key, 'q': location}
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:esra1996@localhost/dist_sys'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Coordinate(db.Model):
    __tablename__ = 'coordinate'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(500), unique=True)
    coordinate_x = db.Column(db.Float)
    coordinate_y = db.Column(db.Float)

    def __init__(self, city, coordinate_x, coordinate_y):
        self.city = city
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y


class CoordinateSchema(ma.ModelSchema):
    class Meta:
        model = Coordinate


r = requests.get(url=URL, params=PARAMS)
data = r.json()
print(data)

# # Acquiring the latitude and longitude from JSON
latitude = data['items'][0]['position']['lat']
# print("Latitude is: " + str(latitude))
longitude = data['items'][0]['position']['lng']


# print("Longtitude is: " + str(longitude))


@app.route('/location', methods=['POST'])
def location():
    city = request.form["city"]
    coordinate_x = latitude
    coordinate_y = longitude
    if db.session.query(Coordinate).filter(Coordinate.city == city).count() == 0:
        data = Coordinate(city, coordinate_x, coordinate_y)
        db.session.add(data)
        db.session.commit()
    return render_template('map.html', apikey=api_key, latitude=latitude,
                           longitude=longitude)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_json', methods=["GET"])
def get_json():
    cities = Coordinate.query.all()
    city_schema = CoordinateSchema(many=True)
    output = city_schema.dump(cities)
    return jsonify({'city': output})


if __name__ == '__main__':
    app.debug = True
    app.run()
