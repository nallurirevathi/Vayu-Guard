import pandas as pd
import sqlite3
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import joblib
import os

# 1. Connect to the Database
print("Loading data from SQLite...")
db_path = "database/vayuguard.db"
conn = sqlite3.connect(db_path)

# Load the data and sort chronologically 
df = pd.read_sql_query("SELECT * FROM daily_metrics ORDER BY city, date", conn)
conn.close()

# 2. Feature Engineering (The Magic Step)
print("Engineering features...")
# We want to predict TOMORROW's PM2.5 based on TODAY's data.
# We create a 'target' column by shifting the PM2.5 value backwards by 1 day for each city.
df['target_pm25_tomorrow'] = df.groupby('city')['pm25'].shift(-1)

# Drop the last row for each city since we don't have "tomorrow's" actual data yet
df = df.dropna()

# Select our training features
features = ['temperature_max', 'temperature_min', 'precipitation_sum', 'wind_speed_max', 'pm10', 'pm25']
target = 'target_pm25_tomorrow'

# 3. Train / Test Split (Chronological)
# In time-series forecasting, we never split randomly. We train on the past to predict the future.
train_size = int(len(df) * 0.8)
train_df = df.iloc[:train_size]
test_df = df.iloc[train_size:]

X_train = train_df[features]
y_train = train_df[target]
X_test = test_df[features]
y_test = test_df[target]

# 4. Train the XGBoost Model
print("Training XGBoost Regressor...")
model = xgb.XGBRegressor(
    n_estimators=100, 
    learning_rate=0.1, 
    max_depth=5, 
    random_state=42
)
model.fit(X_train, y_train)

# 5. Evaluate the Model
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
rmse = root_mean_squared_error(y_test, predictions)

print("=" * 50)
print("MODEL EVALUATION")
print("=" * 50)
print(f"Mean Absolute Error (MAE): {mae:.2f} AQI points")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f} AQI points")

# 6. Save the Model for Production
os.makedirs("ml-service/models", exist_ok=True)
model_path = "ml-service/models/xgboost_pm25_v1.joblib"
joblib.dump(model, model_path)
print(f"\nModel saved successfully to: {model_path}")