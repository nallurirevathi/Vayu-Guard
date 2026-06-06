import requests
import pandas as pd
from datetime import date, timedelta
import os
import time

# ==========================
# CONFIGURATION
# ==========================
# We use the exact same coordinates we used for the weather data!
cities = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867}
}

end_date = date.today()
start_date = end_date - timedelta(days=90) # Keeping it to 90 days for testing

output_folder = "data/raw/aqi"
os.makedirs(output_folder, exist_ok=True)

# ==========================
# DOWNLOAD FUNCTION
# ==========================
def download_aqi(city, lat, lon):
    print(f"Downloading AQI data for {city}...")
    
    # Pointing to Open-Meteo's Air Quality endpoint instead of OpenAQ
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        "&hourly=pm10,pm2_5"
        "&timezone=auto"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        hourly = data["hourly"]
        
        # This gives us clean columns right out of the box!
        df = pd.DataFrame({
            "date": hourly["time"],
            "city": city,
            "pm10": hourly["pm10"],
            "pm25": hourly["pm2_5"]
        })
        
        file_path = os.path.join(output_folder, f"{city.lower()}_aqi.csv")
        df.to_csv(file_path, index=False)
        
        print(f"Saved: {file_path}")
        print(f"Rows: {len(df)}\n")
        
        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {city}: {e}\n")
        return pd.DataFrame()

# ==========================
# MAIN EXECUTION
# ==========================
all_data = []

for city, coords in cities.items():
    df = download_aqi(city, coords["lat"], coords["lon"])
    if not df.empty:
        all_data.append(df)
    
    time.sleep(1) # Be polite to the API

if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_file = os.path.join(output_folder, "all_cities_aqi.csv")
    combined_df.to_csv(combined_file, index=False)

    print("=" * 50)
    print("AQI DOWNLOAD COMPLETE")
    print("=" * 50)
    print(f"Combined file saved: {combined_file}")
    print(f"Total Rows: {len(combined_df)}")
else:
    print("Pipeline failed: No data retrieved.")