from flask import Flask, render_template, request
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# Replace with your actual OpenWeatherMap API key
API_KEY = '71ccfe590d6e26ca968e24d33d361a5a'

# City data with IDs for OpenWeatherMap API
cities = {
    'Tel Aviv': 293396,
    'Jerusalem': 281184,
    'Haifa': 294801,
    'Eilat': 295277,
    'Beersheba': 295530
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/', methods=['GET', 'POST'])
def index():
    historical_data = Temperature.query.order_by(Temperature.date.desc()).all()

    if request.method == 'POST':
        selected_city = request.form['city']
        city_id = cities[selected_city]

        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}&units=metric"

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = json.loads(response.text)
            temperature = data['main']['temp']
            city_name = data['name']
            weather_description = data['weather'][0]['description']

            # Store the data in the database
            new_temperature = Temperature(city=city_name, temperature=temperature, description=weather_description)
            db.session.add(new_temperature)
            db.session.commit()

            # Update historical data after the new entry
            historical_data = Temperature.query.order_by(Temperature.date.desc()).all()
        except requests.exceptions.RequestException as e:
            error_message = f"An error occurred while fetching weather data: {e}"
            return render_template('index.html', cities=cities, selected_city=selected_city, error=error_message, historical_data=historical_data)
        else:
            return render_template('index.html', cities=cities, selected_city=selected_city, temperature=temperature, city_name=city_name, weather_description=weather_description, historical_data=historical_data)

    return render_template('index.html', cities=cities, historical_data=historical_data)

if __name__ == '__main__':
    app.run(debug=True)
