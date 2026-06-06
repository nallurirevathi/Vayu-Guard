from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os

# 1. Initialize the App
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Add this!
from pydantic import BaseModel
import joblib
import pandas as pd
import os

# 1. Initialize the App
app = FastAPI(
    title="VayuGuard ML API", 
    description="Hyperlocal air quality forecasting and health advisories.",
    version="1.0"
)

# Tell Python to allow React to talk to it!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load the Trained Model
# We load this once when the server starts so predictions are lightning fast
model_path = "models/xgboost_pm25_v1.joblib"
if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("Model loaded successfully!")
else:
    model = None
    print("Warning: Model not found. Did you run train_model.py?")

# 3. Define the Data Contracts (What the frontend sends us)
class ForecastRequest(BaseModel):
    city: str
    horizon_hours: int = 24
    temperature_max: float
    temperature_min: float
    precipitation_sum: float
    wind_speed_max: float
    pm10: float
    pm25: float

class RiskRequest(BaseModel):
    aqi: float
    user_profile: str

# 4. Define the Endpoints
@app.post("/forecast")
def get_forecast(req: ForecastRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Prediction engine is offline.")
    
    # Format the incoming JSON into a Pandas DataFrame for XGBoost
    input_features = pd.DataFrame([{
        'temperature_max': req.temperature_max,
        'temperature_min': req.temperature_min,
        'precipitation_sum': req.precipitation_sum,
        'wind_speed_max': req.wind_speed_max,
        'pm10': req.pm10,
        'pm25': req.pm25
    }])
    
    try:
        prediction = model.predict(input_features)[0]
        return {
            "city": req.city,
            "predicted_pm25_tomorrow": round(float(prediction), 2),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/health-risk")
def get_health_risk(req: RiskRequest):
    # Baseline logic for the advisory engine
    risk_level = "Low"
    advisory = "Air quality is good. Enjoy the outdoors!"
    
    if req.aqi > 50:
        risk_level = "Moderate"
        if req.user_profile.lower() in ["asthma", "elderly"]:
            advisory = "Sensitive groups should consider limiting prolonged outdoor exertion."
            
    if req.aqi > 100:
        risk_level = "High"
        advisory = "Everyone should limit outdoor exertion."
        if req.user_profile.lower() == "asthma":
            advisory = "CRITICAL: Keep inhaler nearby. Avoid all outdoor activities. Use indoor air purifiers."

    return {
        "aqi_input": req.aqi,
        "user_profile": req.user_profile,
        "risk_level": risk_level,
        "advisory": advisory
    }