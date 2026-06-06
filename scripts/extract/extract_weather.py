import requests
import pandas as pd
from datetime import date, timedelta
import os

# ==========================
# CONFIGURATION
# ==========================

cities = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867}
}

end_date = date.today()
start_date = end_date - timedelta(days=365 * 3)

output_folder = "data/raw/weather"
os.makedirs(output_folder, exist_ok=True)

# ==========================
# DOWNLOAD FUNCTION
# ==========================

def download_weather(city, lat, lon):

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        "&daily="
        "temperature_2m_max,"
        "temperature_2m_min,"
        "temperature_2m_mean,"
        "precipitation_sum,"
        "rain_sum,"
        "wind_speed_10m_max"
        "&timezone=auto"
    )

    print(f"Downloading weather data for {city}...")

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    daily = data["daily"]

    df = pd.DataFrame({
        "date": daily["time"],
        "city": city,
        "temperature_max": daily["temperature_2m_max"],
        "temperature_min": daily["temperature_2m_min"],
        "temperature_mean": daily["temperature_2m_mean"],
        "precipitation_sum": daily["precipitation_sum"],
        "rain_sum": daily["rain_sum"],
        "wind_speed_max": daily["wind_speed_10m_max"]
    })

    file_path = os.path.join(
        output_folder,
        f"{city.lower()}_weather.csv"
    )

    df.to_csv(file_path, index=False)

    print(f"Saved: {file_path}")
    print(f"Rows: {len(df)}\n")

    return df


# ==========================
# MAIN EXECUTION
# ==========================

all_data = []

for city, coords in cities.items():

    df = download_weather(
        city,
        coords["lat"],
        coords["lon"]
    )

    all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)

combined_file = os.path.join(
    output_folder,
    "all_cities_weather.csv"
)

combined_df.to_csv(combined_file, index=False)

print("=" * 50)
print("DOWNLOAD COMPLETE")
print("=" * 50)
print(f"Combined file saved: {combined_file}")
print(f"Total Rows: {len(combined_df)}")
print(combined_df.head())
print(combined_df.shape)