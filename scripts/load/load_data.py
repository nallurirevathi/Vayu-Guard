import pandas as pd
from sqlalchemy import create_engine
import os

# 1. Configuration
input_file = "data/processed/merged_aqi_weather.csv"
db_folder = "database"
db_path = f"sqlite:///{db_folder}/vayuguard.db"

# Ensure the database folder exists
os.makedirs(db_folder, exist_ok=True)

# 2. Execution
print(f"Reading processed data from {input_file}...")
try:
    df = pd.read_csv(input_file)
    
    # Create the database connection
    engine = create_engine(db_path)
    
    # Load the dataframe into a SQL table named 'daily_metrics'
    # if_exists='replace' means it will overwrite the table if we run the script again
    print("Loading data into the SQL database...")
    df.to_sql('daily_metrics', con=engine, if_exists='replace', index=False)
    
    print("=" * 50)
    print("ETL PIPELINE COMPLETE: DATA LOADED SUCCESSFULLY")
    print("=" * 50)
    print(f"Database created at: {db_folder}/vayuguard.db")
    print(f"Table 'daily_metrics' contains {len(df)} rows.")

except Exception as e:
    print(f"Error during loading: {e}")