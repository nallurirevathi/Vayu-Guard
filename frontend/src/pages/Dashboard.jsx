import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
  const navigate = useNavigate();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [healthProfile, setHealthProfile] = useState('');
  
  const [prediction, setPrediction] = useState('--');
  const [isPredicting, setIsPredicting] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('vayu_token');
    const profile = localStorage.getItem('vayu_profile'); // Grab the profile!
    
    if (!token) {
      navigate('/login');
    } else {
      setIsAuthorized(true);
      setHealthProfile(profile || 'general');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('vayu_token');
    localStorage.removeItem('vayu_profile');
    navigate('/login');
  };

  const runNeuralEngine = async () => {
    setIsPredicting(true);
    try {
      // Replace the old 127.0.0.1 line with your real Render ML URL:
      const response = await axios.post('https://vayu-guard.onrender.com/forecast', {
        city: "Bengaluru",
        horizon_hours: 24,
        temperature_max: 32.0,
        temperature_min: 22.0,
        precipitation_sum: 0.0,
        wind_speed_max: 15.0,
        pm10: 45.0,
        pm25: 25.0
      });
      setPrediction(response.data.predicted_pm25_tomorrow);
    } catch (error) {
      console.error("AI Engine Error:", error);
      setPrediction('ERR');
    }
    setIsPredicting(false);
  };

  // The 80/20 Rule Engine for Health Advisories
  const generateAdvisory = () => {
    if (prediction === '--') return "Awaiting ML prediction data to generate localized health advisory.";
    if (prediction === 'ERR') return "Cannot generate advisory. Engine offline.";

    const pmValue = parseFloat(prediction);

    if (pmValue <= 15) {
      return "Air quality is excellent. Great day for outdoor activities!";
    } else if (pmValue > 15 && pmValue <= 35) {
      if (healthProfile === 'asthma') {
        return "Air quality is acceptable, but slightly elevated. As an individual with asthma, keep your inhaler handy if you plan to exercise outdoors.";
      }
      return "Air quality is good. Standard outdoor activities are fine.";
    } else {
      if (healthProfile === 'asthma') {
        return "WARNING: Poor air quality detected. High risk for asthmatic individuals. Please stay indoors and keep windows closed.";
      }
      return "Air quality is dropping. Sensitive individuals should reduce prolonged outdoor exertion.";
    }
  };

  if (!isAuthorized) return null;

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif', backgroundColor: '#f4f4f9', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <h2 style={{ color: '#333' }}>VayuGuard AI Dashboard</h2>
        <button onClick={handleLogout} style={{ padding: '10px 20px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          Secure Logout
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        
        <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <h3 style={{ marginTop: '0', color: '#007BFF' }}>Air Quality Forecast</h3>
          <p style={{ color: '#666', fontSize: '14px' }}>XGBoost Prediction Engine (Bengaluru)</p>
          
          <div style={{ textAlign: 'center', margin: '40px 0' }}>
            <div style={{ fontSize: '64px', fontWeight: 'bold', color: prediction === '--' ? '#ccc' : '#dc3545' }}>
              {isPredicting ? '...' : prediction}
            </div>
            <div style={{ fontSize: '18px', color: '#888' }}>Predicted PM2.5 Tomorrow</div>
          </div>
          
          <button 
            onClick={runNeuralEngine}
            disabled={isPredicting}
            style={{ width: '100%', padding: '12px', backgroundColor: isPredicting ? '#ccc' : '#007BFF', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
            {isPredicting ? 'Crunching Data...' : 'Run Neural Engine'}
          </button>
        </div>

        <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <h3 style={{ marginTop: '0', color: '#28a745' }}>Personalized Advisory</h3>
          <p style={{ color: '#666', fontSize: '14px' }}>Profile: <span style={{fontWeight: 'bold', textTransform: 'capitalize'}}>{healthProfile}</span></p>
          
          <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#e9ecef', borderRadius: '6px', borderLeft: prediction > 35 ? '5px solid #dc3545' : '5px solid #28a745' }}>
            <strong>Advisory:</strong> {generateAdvisory()}
          </div>
        </div>

      </div>
    </div>
  );
}

export default Dashboard;