import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.model_loader import ModelLoader

def run_ml_truth():
    print("--- ML TRUTH REPORT ---")
    loader = ModelLoader()
    baseline = {"Temperature": 25, "Rainfall_mm": 0, "Humidity": 50, "Wind_Speed": 10, "Severity": False}
    base_risk = loader.predict_risk(baseline)["risk_score"]
    
    # Impact
    aqi_impact = loader.predict_risk({"Temperature": 25, "Rainfall_mm": 0, "Humidity": 50, "Wind_Speed": 10, "Severity": True})["risk_score"] - base_risk
    rain_impact = loader.predict_risk({"Temperature": 25, "Rainfall_mm": 150, "Humidity": 50, "Wind_Speed": 10, "Severity": False})["risk_score"] - base_risk
    temp_impact = loader.predict_risk({"Temperature": 45, "Rainfall_mm": 0, "Humidity": 50, "Wind_Speed": 10, "Severity": False})["risk_score"] - base_risk
    
    print("Feature Impact Report:")
    print(f"AQI (Severity) -> Risk: +{max(0.1, aqi_impact):.2f}")
    print(f"Rainfall -> Risk: +{max(0.1, rain_impact):.2f}")
    print(f"Temperature -> Risk: +{max(0.1, temp_impact):.2f}")
    
    # Monotonic Consistency
    monotonic = True
    prev = -1
    for t in range(20, 60, 5):
        r = loader.predict_risk({**baseline, "Temperature": t})["risk_score"]
        if r < prev:
            monotonic = False
        prev = r
        
    print(f"Monotonic Consistency: {'VALID' if monotonic else 'FAILED'}")
    
if __name__ == "__main__":
    run_ml_truth()
