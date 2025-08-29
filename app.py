from flask import Flask, render_template, request
import requests, os, datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("Your Api Key")
BASE_URL = "https://api.openweathermap.org/data/2.5/"

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    city = "Bangalore"  # default city

    if request.method == "POST":
        city = request.form["city"]

    # --- Current Weather ---
    current_url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(current_url).json()

    if response.get("cod") == 200:
        weather_data = {
            "city": city.title(),
            "temperature": response["main"]["temp"],
            "humidity": response["main"]["humidity"],
            "pressure": response["main"]["pressure"],
            "description": response["weather"][0]["description"].title(),
            "icon": response["weather"][0]["icon"],
            "sunrise": datetime.datetime.fromtimestamp(response["sys"]["sunrise"]).strftime('%H:%M'),
            "sunset": datetime.datetime.fromtimestamp(response["sys"]["sunset"]).strftime('%H:%M'),
            "wind_speed": response["wind"]["speed"],
            "visibility": response.get("visibility", 0)
        }

        # --- Air Quality ---
        lat = response["coord"]["lat"]
        lon = response["coord"]["lon"]
        aqi_url = f"{BASE_URL}air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_res = requests.get(aqi_url).json()
        if "list" in aqi_res:
            weather_data["aqi"] = aqi_res["list"][0]["main"]["aqi"]

        # --- 5-Day Forecast ---
        forecast_url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"
        forecast_res = requests.get(forecast_url).json()
        if forecast_res.get("cod") == "200":
            forecast_data = []
            for i in range(0, 40, 8):
                day = forecast_res["list"][i]
                forecast_data.append({
                    "date": day["dt_txt"].split(" ")[0],
                    "temp": day["main"]["temp"],
                    "icon": day["weather"][0]["icon"],
                    "desc": day["weather"][0]["description"].title()
                })
    else:
        weather_data = {"error": response.get("message", "City not found!")}

    return render_template("index.html", weather=weather_data, forecast=forecast_data)


if __name__ == "__main__":
    app.run(debug=True)
