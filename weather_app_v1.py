import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "my_token*(!Ds"
# you can get API keys for free here - https://api-ninjas.com/api/jokes
RSA_KEY = "" #Your API key here

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def get_weather(city, date):           #city = "Kyiv", date = "2024-02-16"
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    url = f"{base_url}/{city}/{date}/{date}?unitGroup=us&key={RSA_KEY}&contentType=json"

    headers = {"X-Api-Key": RSA_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


def fahrenheit_to_celsius(fahrenheit):
    celsius = (fahrenheit - 32) * 5 / 9
    return round(celsius)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/weather", methods=["POST"])
def joke_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")
    requester_name = json_data.get("requester_name")
    location = json_data.get("location")
    date = json_data.get("date")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    weather_data = get_weather(location, date)
    
    weather = {"tempmax": fahrenheit_to_celsius(weather_data["days"][0]["temp"]),
            "tempmin": fahrenheit_to_celsius(weather_data["days"][0]["tempmin"]),
            "temp": fahrenheit_to_celsius(weather_data["days"][0]["temp"]),
            "feelslike": fahrenheit_to_celsius(weather_data["days"][0]["feelslike"]),
            "humidity": weather_data["days"][0]["humidity"],
            "windspeed": weather_data["days"][0]["windspeed"],
            "description": weather_data["days"][0]["description"]}

    timestamp = dt.datetime.now()

    result = {
        "requester_name": requester_name,
        "timestamp": timestamp.isoformat(),
        "location": location,
        "date": date,
        "weather": weather,
    }

    return result
