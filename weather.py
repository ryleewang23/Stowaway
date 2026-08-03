"""
weather.py

Handles communication with the Open-Meteo API.

Features
--------
✔ Geocoding
✔ 14-day weather forecast
✔ Historical weather lookup
✔ Weather summary generation
"""

import requests
from datetime import date

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


####################################################
# LOCATION SEARCH
####################################################

def search_locations(search_text, count=8):
    """
    Returns several possible location matches.

    Example:
    Searching "San Francisco" may return:
    - San Francisco, California, United States
    - San Francisco, Córdoba, Argentina
    """

    search_text = str(search_text).strip()

    if len(search_text) < 2:
        return []

    response = requests.get(
        GEOCODE_URL,
        params={
            "name": search_text,
            "count": count,
            "language": "en",
            "format": "json"
        },
        timeout=15
    )

    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    locations = []

    for result in results:
        name_parts = [result.get("name", "")]

        admin_area = result.get("admin1")

        if admin_area:
            name_parts.append(admin_area)

        country = result.get("country")

        if country:
            name_parts.append(country)

        display_name = ", ".join(
            part for part in name_parts if part
        )

        locations.append(
            {
                "display_name": display_name,
                "name": result.get("name", ""),
                "admin1": result.get("admin1", ""),
                "country": result.get("country", ""),
                "country_code": result.get(
                    "country_code",
                    ""
                ),
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "timezone": result.get(
                    "timezone",
                    "auto"
                ),
                "population": result.get(
                    "population"
                )
            }
        )

    return locations


def geocode(city_name):
    """
    Keeps compatibility with older parts of the app by
    returning the first matching result.
    """

    results = search_locations(city_name, count=1)

    if not results:
        raise ValueError(
            "No matching location was found."
        )

    location = results[0]

    return {
        "name": location["name"],
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": location["timezone"]
    }


####################################################
# FORECAST
####################################################

def get_forecast(latitude, longitude):
    """
    Returns a 14-day weather forecast.
    """

    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily":
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_sum",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "timezone": "auto"
        }
    )

    response.raise_for_status()

    return response.json()["daily"]


####################################################
# HISTORICAL WEATHER
####################################################

def historical_range(latitude, longitude,
                     month, day,
                     years_back=10):
    """
    Returns:
        Average high
        Min high
        Max high
        Rain frequency
    """

    temperatures = []
    rainy_days = 0

    current_year = date.today().year

    for year in range(current_year - years_back,
                      current_year):

        target_date = f"{year}-{month:02d}-{day:02d}"

        response = requests.get(
            ARCHIVE_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": target_date,
                "end_date": target_date,
                "daily":
                    "temperature_2m_max,"
                    "precipitation_sum",
                "temperature_unit": "fahrenheit",
                "precipitation_unit": "inch",
                "timezone": "auto"
            }
        )

        response.raise_for_status()

        data = response.json()

        daily = data.get("daily")

        if not daily:
            continue

        temps = daily.get("temperature_2m_max")

        if temps:

            temperatures.append(temps[0])

            if daily["precipitation_sum"][0] > 0:
                rainy_days += 1

    if len(temperatures) == 0:
        return None

    return {
        "average_high":
            round(sum(temperatures) / len(temperatures), 1),

        "minimum_high":
            min(temperatures),

        "maximum_high":
            max(temperatures),

        "rain_probability":
            round(
                rainy_days /
                len(temperatures) * 100,
                1
            )
    }


####################################################
# WEATHER SUMMARY
####################################################

def create_weather_summary(history):
    """
    Creates a human-readable Fahrenheit summary.
    """

    if history is None:
        return "Historical weather unavailable."

    return (
        f"Typical high: {history['average_high']}°F "
        f"(range {history['minimum_high']}°F"
        f"–{history['maximum_high']}°F). "
        f"Rain occurred on approximately "
        f"{history['rain_probability']}% "
        f"of comparable dates."
    )


####################################################
# TEST
####################################################

if __name__ == "__main__":

    city = input("Enter city: ")

    location = geocode(city)

    print("\nLocation")
    print(location)

    forecast = get_forecast(
        location["latitude"],
        location["longitude"]
    )

    print("\nForecast")

    for day in range(5):

        print(
            forecast["time"][day],
            forecast["temperature_2m_max"][day],
            "°C"
        )

    today = date.today()

    history = historical_range(
        location["latitude"],
        location["longitude"],
        today.month,
        today.day
    )

    print("\nHistorical")

    print(create_weather_summary(history))
