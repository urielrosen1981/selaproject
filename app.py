from flask import Flask, render_template, request
import requests
import json

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_city = request.form['city']
        city_id = cities[selected_city]

        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}&units=metric"  # Use metric units

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            data = json.loads(response.text)
            temperature = data['main']['temp']
            city_name = data['name']
            weather_description = data['weather'][0]['description']
        except requests.exceptions.RequestException as e:
            error_message = f"An error occurred while fetching weather data: {e}"
            return render_template('index.html', cities=cities, selected_city=selected_city, error=error_message)
        else:
            return render_template('index.html', cities=cities, selected_city=selected_city, temperature=temperature, city_name=city_name, weather_description=weather_description)

    return render_template('index.html', cities=cities)

if __name__ == '__main__':
    app.run(debug=True)
