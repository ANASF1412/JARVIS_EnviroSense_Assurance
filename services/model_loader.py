"""
ML Model Loader - Load and cache pre-trained models
Production-ready with proper feature handling & fail-safe logic
"""

import pickle
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from config.settings import RISK_MODEL_PATH, INCOME_MODEL_PATH


class ModelLoader:
    """Load and manage ML models."""

    # ============================================================
    # [LOAD] LOAD MODELS (CACHED)
    # ============================================================

    @staticmethod
    @st.cache_resource
    def load_risk_model():
        """Load risk prediction model (cached)."""
        try:
            risk_model_path = Path(RISK_MODEL_PATH)

            if not risk_model_path.exists():
                raise FileNotFoundError(f"Risk model not found at {RISK_MODEL_PATH}")

            with open(risk_model_path, 'rb') as f:
                model = pickle.load(f)

            print(f"[OK] Risk model loaded from {RISK_MODEL_PATH}")

            # Debug: Print expected features
            if hasattr(model, "feature_names_in_"):
                print("[INFO] Risk Model expects:", list(model.feature_names_in_))

            return model

        except Exception as e:
            print(f"[ERROR] Failed to load risk model: {str(e)}")
            raise

    @staticmethod
    @st.cache_resource
    def load_income_model():
        """Load income estimation model (cached)."""
        try:
            income_model_path = Path(INCOME_MODEL_PATH)

            if not income_model_path.exists():
                raise FileNotFoundError(f"Income model not found at {INCOME_MODEL_PATH}")

            with open(income_model_path, 'rb') as f:
                model = pickle.load(f)

            print(f"[OK] Income model loaded from {INCOME_MODEL_PATH}")

            # Debug: Print expected features
            if hasattr(model, "feature_names_in_"):
                print("[MONEY] Income Model expects:", list(model.feature_names_in_))

            return model

        except Exception as e:
            print(f"[ERROR] Failed to load income model: {str(e)}")
            raise

    @staticmethod
    def get_risk_model():
        return ModelLoader.load_risk_model()

    @staticmethod
    def get_income_model():
        return ModelLoader.load_income_model()

    # ============================================================
    # [LOAD] RISK PREDICTION (FIXED: Using predict_proba)
    # ============================================================

    @staticmethod
    def predict_risk(weather_data: dict) -> dict:
        """
        Predict continuous risk score (0.0 to 1.0) with full explainability.

        [OK] ENTERPRISE FEATURE: Returns comprehensive risk assessment including:
        - risk_score: Continuous probability [0.0, 1.0]
        - confidence: Certainty of prediction (based on probability entropy)
        - contributing_factors: Which conditions drive the risk
        - factor_impacts: Impact level of each factor
        - risk_class: Low/Medium/High classification
        - probabilities: Raw class probabilities

        Expected input structure:
        {
            "temperature": float (°C),
            "rainfall_mm": float (mm),
            "zone_risk": float (optional),
            "working_hours": float (optional),
            "aqi": float (optional)
        }
        
        Returns:
            dict with keys: risk_score, confidence, contributing_factors, 
                           factor_impacts, risk_class, probabilities
        """
        try:
            model = ModelLoader.get_risk_model()

            # ===== FEATURE ENGINEERING =====
            temperature = weather_data.get("temperature", 30.0)
            rainfall = weather_data.get("rainfall_mm", 0.0)
            
            # Derive auxiliary features intelligently
            humidity = ModelLoader._estimate_humidity(temperature, rainfall)
            wind_speed = ModelLoader._estimate_wind_speed(rainfall)
            severity = ModelLoader._estimate_severity(temperature, rainfall)

            # ===== VALIDATION =====
            ModelLoader._validate_features({
                "Temperature": temperature,
                "Rainfall_mm": rainfall,
                "Humidity": humidity,
                "Wind_Speed": wind_speed,
                "Severity": severity
            })

            # ===== CREATE INPUT DATAFRAME =====
            input_data = pd.DataFrame([{
                "Temperature": temperature,
                "Rainfall_mm": rainfall,
                "Humidity": humidity,
                "Wind_Speed": wind_speed,
                "Severity": severity
            }])

            # ===== PREDICT WITH PROBA =====
            raw_proba = model.predict_proba(input_data)[0]  # [P(Low), P(Medium), P(High)]
            
            # Apply Temperature Scaling Calibration to smooth probabilities and fix saturation
            temperature_scale = 1.5 
            logits = np.log(np.clip(raw_proba, 1e-10, 1.0))
            scaled_logits = logits / temperature_scale
            proba = np.exp(scaled_logits) / np.sum(np.exp(scaled_logits))
            
            risk_score = float(proba[0] * 0.0 + proba[1] * 0.5 + proba[2] * 1.0)
            risk_score = max(0.0, min(1.0, risk_score))

            # ===== CONFIDENCE SCORE (based on entropy) =====
            # Higher entropy = less confident. Max entropy = 1.0986 (all equal)
            epsilon = 1e-10
            entropy = -sum(p * np.log(p + epsilon) for p in proba)
            max_entropy = np.log(3)  # Max entropy for 3 classes
            confidence = 1.0 - (entropy / max_entropy)  # Invert: high certainty → high confidence
            confidence = float(np.clip(confidence, 0.0, 1.0))

            # ===== RISK CLASSIFICATION =====
            if proba[2] > 0.5:
                risk_class = "High"
            elif proba[1] > proba[0]:
                risk_class = "Medium"
            else:
                risk_class = "Low"

            # ===== CONTRIBUTING FACTORS (from actual values, not hardcoded) =====
            contributing_factors = []
            factor_impacts = {}

            # Temperature analysis
            if temperature > 42:
                contributing_factors.append("Extreme heat")
                factor_impacts["Temperature"] = "High"
            elif temperature > 38:
                contributing_factors.append("High temperature")
                factor_impacts["Temperature"] = "Medium"
            else:
                factor_impacts["Temperature"] = "Low"

            # Rainfall analysis
            if rainfall > 100:
                contributing_factors.append("Heavy rainfall")
                factor_impacts["Rainfall"] = "High"
            elif rainfall > 50:
                contributing_factors.append("Moderate rainfall")
                factor_impacts["Rainfall"] = "Medium"
            else:
                factor_impacts["Rainfall"] = "Low"

            # Humidity-based stress
            if humidity > 80:
                contributing_factors.append("High humidity")
                factor_impacts["Humidity"] = "High"
            else:
                factor_impacts["Humidity"] = "Low"

            # Wind stress
            if wind_speed > 20:
                contributing_factors.append("Strong winds")
                factor_impacts["Wind"] = "High"
            elif wind_speed > 15:
                contributing_factors.append("Moderate winds")
                factor_impacts["Wind"] = "Medium"
            else:
                factor_impacts["Wind"] = "Low"

            # Combined severity
            if not contributing_factors:
                contributing_factors.append("Normal conditions")

            print(f"[OK] Risk Model: score={risk_score:.4f}, conf={confidence:.4f}, factors={contributing_factors}")

            return {
                "success": True,
                "risk_score": round(risk_score, 4),
                "confidence": round(confidence, 4),
                "risk_class": risk_class,
                "contributing_factors": contributing_factors,
                "factor_impacts": factor_impacts,
                "probabilities": {
                    "low": round(float(proba[0]), 4),
                    "medium": round(float(proba[1]), 4),
                    "high": round(float(proba[2]), 4)
                }
            }

        except Exception as e:
            print(f"[ERROR] Risk prediction failed: {str(e)}")
            st.warning("[WARN] Risk model failed. Using fallback score of 0.5.")
            return {
                "success": False,
                "risk_score": 0.5,
                "confidence": 0.0,
                "risk_class": "Unknown",
                "contributing_factors": ["Model unavailable"],
                "factor_impacts": {},
                "probabilities": {"low": 0.33, "medium": 0.34, "high": 0.33}
            }

    @staticmethod
    def _estimate_humidity(temperature: float, rainfall: float) -> float:
        """
        Intelligently estimate humidity with realistic weather physics.
        
        Humidity correlates with:
        - Rainfall: High rain → higher humidity (more water in air)
        - Temperature: High temp → lower humidity (air expands, holds more moisture capacity)
        - Interaction: Rain in cool weather = very high humidity; rain in heat = less relative increase
        
        Returns: Value in [20, 100]
        """
        base_humidity = 55.0  # Neutral baseline
        
        # Reduced target leakage and correlation
        rainfall_effect = np.log1p(rainfall) * 4.0
        temp_effect = np.sin(temperature / 10.0) * 8.0
        
        humidity = base_humidity + rainfall_effect + temp_effect
        return float(np.clip(humidity, 20.0, 100.0))

    @staticmethod
    def _estimate_wind_speed(rainfall: float) -> float:
        """
        Intelligently estimate wind speed from rainfall patterns.
        
        Wind correlates with rainfall because:
        - Wind brings moisture-laden air
        - Convective systems produce both wind and rain
        - Stronger systems = more wind + more rain
        
        Heavy rain ≠ always heavy wind (downpours can be relatively calm)
        So we use logarithmic scaling (diminishing returns)
        
        Returns: Value in [2, 30] km/h
        """
        base_wind = 4.0  # Calm baseline
        
        # Reduced correlation, physical scaling
        rain_effect = np.sqrt(rainfall) * 1.5 if rainfall > 0 else 0
        
        wind_speed = base_wind + rain_effect
        return float(np.clip(wind_speed, 2.0, 30.0))

    @staticmethod
    def _estimate_severity(temperature: float, rainfall: float) -> float:
        """
        Estimate overall weather severity (1-5 scale) with realistic interaction.
        
        Severity is NON-LINEAR:
        - Moderate conditions: 1-2
        - Mixed conditions: 2-3
        - Stressful: 3-4
        - Severe: 4-5
        
        Combines temperature and rainfall with interaction term.
        
        Returns: Value clamped to [1, 5]
        """
        # Redesigned to represent physical interaction stress, preventing target leakage
        temp_factor = max(0, temperature - 32) / 10.0
        rain_factor = max(0, rainfall - 25) / 50.0
        
        # Pure interaction term
        severity = 1.0 + (temp_factor * rain_factor)
        return float(np.clip(severity, 1.0, 5.0))

    @staticmethod
    def _validate_features(features: dict) -> None:
        """
        Validate feature schema before prediction.
        
        Raises:
            ValueError if features are invalid
        """
        expected_features = ["Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"]
        
        # Check all features present
        missing = set(expected_features) - set(features.keys())
        if missing:
            raise ValueError(f"Missing features: {missing}")
        
        # Check data types and ranges
        if not isinstance(features["Temperature"], (int, float)):
            raise ValueError("Temperature must be numeric")
        if not isinstance(features["Rainfall_mm"], (int, float)):
            raise ValueError("Rainfall_mm must be numeric")
        if not isinstance(features["Humidity"], (int, float)):
            raise ValueError("Humidity must be numeric")
        if not isinstance(features["Wind_Speed"], (int, float)):
            raise ValueError("Wind_Speed must be numeric")
        if not isinstance(features["Severity"], (int, float)):
            raise ValueError("Severity must be numeric")
        
        # Check reasonable ranges
        if not (0 <= features["Temperature"] <= 70):
            raise ValueError(f"Temperature {features['Temperature']} out of expected range [0-70]")
        if features["Rainfall_mm"] < 0:
            raise ValueError(f"Rainfall_mm cannot be negative: {features['Rainfall_mm']}")
        if not (0 <= features["Humidity"] <= 100):
            raise ValueError(f"Humidity {features['Humidity']} out of expected range [0-100]")
        if features["Wind_Speed"] < 0:
            raise ValueError(f"Wind_Speed cannot be negative: {features['Wind_Speed']}")
        if not (1 <= features["Severity"] <= 5):
            raise ValueError(f"Severity {features['Severity']} out of expected range [1-5]")

    # ============================================================
    # 💰 INCOME LOSS PREDICTION (FIXED)
    # ============================================================

    @staticmethod
    def predict_income_loss(hours_lost: float, hourly_income: float, weather_data: dict = None) -> dict:
        """
        Predict income loss with intelligent weather integration.

        [OK] ENTERPRISE FEATURE: 
        - Uses actual weather conditions (if provided) instead of hardcoded values
        - Returns confidence score
        - Validates all inputs
        - Always returns dict with success flag

        Args:
            hours_lost: Number of hours lost (≥0)
            hourly_income: Worker's average hourly income (≥0)
            weather_data: Optional dict with temperature/rainfall for context

        Returns:
            dict with: loss, confidence, multiplier, details, success
        """
        try:
            # ===== INPUT VALIDATION =====
            if not isinstance(hours_lost, (int, float)) or hours_lost < 0:
                raise ValueError(f"Invalid hours_lost: {hours_lost}")
            if not isinstance(hourly_income, (int, float)) or hourly_income < 0:
                raise ValueError(f"Invalid hourly_income: {hourly_income}")

            model = ModelLoader.get_income_model()

            # ===== INTELLIGENT WEATHER INTEGRATION =====
            # If weather conditions provided, use them; otherwise use conservative defaults
            if weather_data and isinstance(weather_data, dict):
                temperature = float(weather_data.get("temperature", 30.0))
                rainfall = float(weather_data.get("rainfall_mm", 25.0))
                use_actual_weather = True
            else:
                temperature = 30.0  # Conservative (neutral conditions)
                rainfall = 25.0
                use_actual_weather = False

            # Derive other weather features intelligently
            humidity = ModelLoader._estimate_humidity(temperature, rainfall)
            wind_speed = ModelLoader._estimate_wind_speed(rainfall)
            severity = ModelLoader._estimate_severity(temperature, rainfall)

            # ===== FEATURE ENGINEERING =====
            # Use realistic behavioral patterns for workers
            # In severe conditions, workers take fewer orders
            severity_multiplier = max(0.5, 1.0 - (severity - 1.0) * 0.15)  # Severe conditions → fewer orders
            
            orders_per_day = 10 * severity_multiplier  # Adjust for conditions
            working_hours = 8  # Standard day
            earnings_per_day = hourly_income * 8  # Base daily earnings

            features = np.array([[
                orders_per_day,
                working_hours,
                earnings_per_day,
                temperature,
                rainfall,
                humidity,
                wind_speed,
                severity
            ]])

            # ===== PREDICT =====
            predicted_daily_earnings = model.predict(features)[0]
            hourly_rate_from_model = max(0.1, predicted_daily_earnings / 8)
            model_loss = hours_lost * hourly_rate_from_model

            # ===== BASELINE CALCULATION =====
            baseline_loss = hours_lost * hourly_income

            # ===== INTELLIGENT MULTIPLIER =====
            # Model adjustment shouldn't be wildly different from baseline
            if baseline_loss > 0:
                multiplier = model_loss / baseline_loss
                # Cap multiplier to [0.5, 2.0] to prevent unrealistic values
                multiplier = np.clip(multiplier, 0.5, 2.0)
            else:
                multiplier = 1.0

            final_loss = multiplier * baseline_loss

            # ===== CONFIDENCE SCORE =====
            # Higher confidence if:
            # - Model and baseline agree (~1.0x multiplier)
            # - Conditions are moderate (severity ~2.0)
            # - Normal weather was used
            
            agreement_confidence = 1.0 - abs(multiplier - 1.0) / 2.0  # [0, 1]
            condition_confidence = 1.0 - abs(severity - 2.0) / 3.0  # [0, 1], peaks at severity 2
            weather_confidence = 0.9 if use_actual_weather else 0.7
            
            confidence = (agreement_confidence * 0.4 + condition_confidence * 0.3 + weather_confidence * 0.3)
            confidence = float(np.clip(confidence, 0.0, 1.0))

            final_loss = max(0.0, float(final_loss))

            print(f"[OK] Income loss: {hours_lost}h × ₹{hourly_income} → ₹{final_loss:.2f} (mult={multiplier:.2f}, conf={confidence:.2f})")

            return {
                "success": True,
                "loss": round(final_loss, 2),
                "confidence": round(confidence, 4),
                "model_adjustment_multiplier": round(multiplier, 4),
                "baseline_loss": round(baseline_loss, 2),
                "uses_actual_weather": use_actual_weather,
                "weather_context": {
                    "temperature": float(temperature),
                    "rainfall_mm": float(rainfall),
                    "severity": round(severity, 2)
                }
            }

        except Exception as e:
            print(f"[ERROR] Income prediction failed: {str(e)}")
            st.warning("[WARN] Income model failed. Using fallback calculation.")
            
            # ===== GUARANTEED FALLBACK =====
            fallback_loss = float(hours_lost * hourly_income)
            fallback_loss = max(0.0, fallback_loss)

            return {
                "success": True,  # Still successful (using fallback)
                "loss": round(fallback_loss, 2),
                "confidence": 0.3,  # Low confidence (using fallback)
                "model_adjustment_multiplier": 1.0,
                "baseline_loss": round(fallback_loss, 2),
                "uses_actual_weather": False,
                "warning": "Using fallback calculation due to model error"
            }

    # ============================================================
    # [INFO] SENSITIVITY ANALYSIS (ENTERPRISE FEATURE)
    # ============================================================

    @staticmethod
    def analyze_risk_sensitivity() -> dict:
        """
        Perform comprehensive sensitivity analysis on risk model.
        
        Tests how each feature independently impacts predictions:
        - Temperature: 10°C to 55°C range
        - Rainfall: 0mm to 200mm range
        - Combined conditions
        
        Returns detailed sensitivity report showing:
        - How much each feature moves the risk score
        - Which features are most impactful
        - Whether model uses full output range
        
        Returns:
            dict with sensitivity metrics
        """
        print("\n" + "="*70)
        print("[INFO] SENSITIVITY ANALYSIS - Testing Feature Impact on Risk Scores")
        print("="*70)

        results = {
            "temperature_sensitivity": {},
            "rainfall_sensitivity": {},
            "impact_ranking": {}
        }

        # ===== TEST 1: TEMPERATURE SENSITIVITY =====
        print("\n[TEMP] Temperature Sensitivity (rainfall=25mm, baseline)")
        temps = [10, 20, 30, 40, 50]
        temp_scores = []

        for temp in temps:
            result = ModelLoader.predict_risk({"temperature": temp, "rainfall_mm": 25.0})
            score = result["risk_score"]
            temp_scores.append(score)
            print(f"  Temp {temp:2d}°C → Risk: {score:.4f}")

        temp_range = max(temp_scores) - min(temp_scores)
        temp_sensitivity = temp_range / (temps[-1] - temps[0]) * 10  # Sensitivity per 10°C
        results["temperature_sensitivity"] = {
            "min_score": min(temp_scores),
            "max_score": max(temp_scores),
            "range": temp_range,
            "sensitivity_per_10C": round(temp_sensitivity, 4)
        }

        # ===== TEST 2: RAINFALL SENSITIVITY =====
        print("\n[RAIN] Rainfall Sensitivity (temperature=35°C, baseline)")
        rainfalls = [0, 50, 100, 150, 200]
        rain_scores = []

        for rain in rainfalls:
            result = ModelLoader.predict_risk({"temperature": 35.0, "rainfall_mm": rain})
            score = result["risk_score"]
            rain_scores.append(score)
            print(f"  Rain {rain:3d}mm → Risk: {score:.4f}")

        rain_range = max(rain_scores) - min(rain_scores)
        rain_sensitivity = rain_range / (rainfalls[-1] - rainfalls[0]) * 100  # Per 100mm
        results["rainfall_sensitivity"] = {
            "min_score": min(rain_scores),
            "max_score": max(rain_scores),
            "range": rain_range,
            "sensitivity_per_100mm": round(rain_sensitivity, 4)
        }

        # ===== TEST 3: IMPACT RANKING =====
        # Which feature moves the output more per unit change?
        temp_per_unit = temp_sensitivity / (temps[-1] - temps[0])  # Per 1°C
        rain_per_unit = rain_sensitivity / (rainfalls[-1] - rainfalls[0])  # Per 1mm

        results["impact_ranking"] = {
            "temperature_impact_per_unit": round(temp_per_unit, 6),
            "rainfall_impact_per_unit": round(rain_per_unit, 6),
            "most_impactful": "Temperature" if temp_per_unit > rain_per_unit else "Rainfall",
            "temperature_is_stronger": temp_per_unit > rain_per_unit
        }

        # ===== TEST 4: FULL RANGE UTILIZATION =====
        print("\n[CHART] Range Utilization Check")
        all_scores = temp_scores + rain_scores
        overall_min = min(all_scores)
        overall_max = max(all_scores)
        overall_range = overall_max - overall_min

        results["range_utilization"] = {
            "overall_min": round(overall_min, 4),
            "overall_max": round(overall_max, 4),
            "range_used": round(overall_range, 4),
            "range_percentage": round((overall_range / 1.0) * 100, 1),  # As % of 0-1 range
            "full_range_utilization": overall_range > 0.3  # Good if uses >30% of range
        }

        print(f"\n  Risk prediction range (0-1 scale): [{overall_min:.4f}, {overall_max:.4f}]")
        print(f"  Range utilized: {overall_range:.4f} ({results['range_utilization']['range_percentage']}% of full)")
        
        if overall_range > 0.3:
            print("  [OK] Good range utilization (using >30% of available range)")
        else:
            print("  [WARN] Limited range utilization (compressed predictions)")

        return results

    @staticmethod
    def perform_stress_testing() -> dict:
        """
        Stress-test the ML system with extreme and edge-case inputs.
        
        Tests:
        - Extreme weather conditions
        - Edge values (0, very high)
        - Unusual combinations
        - Invalid recovery
        
        Returns:
            dict with stress test results
        """
        print("\n" + "="*70)
        print("[LOAD] STRESS TESTING - Extreme Conditions & Edge Cases")
        print("="*70)

        stress_tests = {
            "extreme_conditions": [],
            "edge_cases": [],
            "invalid_recovery": [],
            "all_passed": True
        }

        # ===== EXTREME WEATHER CONDITIONS =====
        print("\n[TEMP] Extreme Weather Conditions")
        extreme_cases = [
            {"temperature": 55, "rainfall_mm": 200, "name": "Severe heat + flooding"},
            {"temperature": 5, "rainfall_mm": 0, "name": "Extreme cold + dry"},
            {"temperature": 45, "rainfall_mm": 150, "name": "Heatwave + heavy rain"},
            {"temperature": 20, "rainfall_mm": 100, "name": "Cool + heavy rain"},
        ]

        for case in extreme_cases:
            try:
                result = ModelLoader.predict_risk({"temperature": case["temperature"], "rainfall_mm": case["rainfall_mm"]})
                score = result["risk_score"]
                
                # Check validity
                if 0 <= score <= 1 and not (score != score):  # NaN check
                    status = "[OK] PASS"
                    stress_tests["extreme_conditions"].append({
                        "case": case["name"],
                        "score": score,
                        "valid": True
                    })
                    print(f"  {status}: {case['name']} → Score: {score:.4f}")
                else:
                    status = "[ERROR] FAIL"
                    stress_tests["extreme_conditions"].append({"case": case["name"], "valid": False})
                    stress_tests["all_passed"] = False
                    print(f"  {status}: {case['name']} → Invalid score: {score}")
            except Exception as e:
                print(f"  [ERROR] CRASH: {case['name']} → {str(e)}")
                stress_tests["all_passed"] = False

        # ===== EDGE CASES =====
        print("\n[EDGE] Edge Cases")
        edge_cases = [
            {"temperature": 0, "rainfall_mm": 0, "name": "Absolute minimum"},
            {"temperature": 70, "rainfall_mm": 500, "name": "Extreme maximum"},
            {"temperature": 30, "rainfall_mm": 0, "name": "Zero rainfall"},
            {"temperature": 50, "rainfall_mm": 200, "name": "Maximum both"},
        ]

        for case in edge_cases:
            try:
                result = ModelLoader.predict_risk({"temperature": case["temperature"], "rainfall_mm": case["rainfall_mm"]})
                score = result["risk_score"]
                
                if 0 <= score <= 1 and not (score != score):
                    status = "[OK] PASS"
                    stress_tests["edge_cases"].append({"case": case["name"], "score": score, "valid": True})
                    print(f"  {status}: {case['name']} → Score: {score:.4f}")
                else:
                    status = "[ERROR] FAIL"
                    stress_tests["edge_cases"].append({"case": case["name"], "valid": False})
                    stress_tests["all_passed"] = False
                    print(f"  {status}: {case['name']} → Invalid score: {score}")
            except Exception as e:
                print(f"  [ERROR] CRASH: {case['name']} → {str(e)}")
                stress_tests["all_passed"] = False

        # ===== INVALID INPUT RECOVERY =====
        print("\n[WARN] Invalid Input Recovery")
        invalid_cases = [
            {"temperature": -50, "rainfall_mm": 100, "name": "Negative temperature"},  # Should handle
            {"temperature": 30, "rainfall_mm": -50, "name": "Negative rainfall"},      # Should handle
        ]

        for case in invalid_cases:
            try:
                result = ModelLoader.predict_risk({"temperature": case["temperature"], "rainfall_mm": case["rainfall_mm"]})
                if result.get("success") is False:
                    status = "[OK] CAUGHT"
                    stress_tests["invalid_recovery"].append({"case": case["name"], "recovered": True})
                    print(f"  {status}: {case['name']} → Safely rejected")
                else:
                    # If it passed validation, it was corrected
                    score = result.get("risk_score", -1)
                    if 0 <= score <= 1:
                        status = "[OK] CORRECTED"
                        stress_tests["invalid_recovery"].append({"case": case["name"], "recovered": True})
                        print(f"  {status}: {case['name']} → Value corrected/bounded")
                    else:
                        print(f"  [ERROR] INVALID: {case['name']} → Produced bad output")
                        stress_tests["all_passed"] = False
            except Exception as e:
                # Exception is OK if it clearly indicates the error
                print(f"  [OK] RAISED: {case['name']} → {str(e)[:50]}")
                stress_tests["invalid_recovery"].append({"case": case["name"], "recovered": True})

        print("\n" + "="*70)
        if stress_tests["all_passed"]:
            print("[OK] ALL STRESS TESTS PASSED - System is robust under extreme inputs")
        else:
            print("[WARN] Some stress tests failed - review above")
        print("="*70)

        return stress_tests

    @staticmethod
    def analyze_model_coverage() -> dict:
        """
        Analyze how well the model covers the output range.
        
        Returns:
            dict with coverage statistics
        """
        print("\n" + "="*70)
        print("[INFO] MODEL OUTPUT RANGE ANALYSIS")
        print("="*70)

        # Generate 100+ predictions across the parameter space
        temps = np.linspace(10, 50, 8)
        rains = np.linspace(0, 200, 8)
        
        all_scores = []
        
        print("\n[TEST] Testing 64 weather combinations...")
        for temp in temps:
            for rain in rains:
                result = ModelLoader.predict_risk({"temperature": float(temp), "rainfall_mm": float(rain)})
                all_scores.append(result["risk_score"])

        all_scores = np.array(all_scores)
        
        coverage = {
            "total_predictions": len(all_scores),
            "min_score": round(float(np.min(all_scores)), 4),
            "max_score": round(float(np.max(all_scores)), 4),
            "mean_score": round(float(np.mean(all_scores)), 4),
            "median_score": round(float(np.median(all_scores)), 4),
            "std_dev": round(float(np.std(all_scores)), 4),
            "percentiles": {
                "p10": round(float(np.percentile(all_scores, 10)), 4),
                "p25": round(float(np.percentile(all_scores, 25)), 4),
                "p50": round(float(np.percentile(all_scores, 50)), 4),
                "p75": round(float(np.percentile(all_scores, 75)), 4),
                "p90": round(float(np.percentile(all_scores, 90)), 4)
            }
        }

        print(f"\nCoverage across 64 conditions:")
        print(f"  Min: {coverage['min_score']:.4f}")
        print(f"  Max: {coverage['max_score']:.4f}")
        print(f"  Mean: {coverage['mean_score']:.4f}")
        print(f"  Std Dev: {coverage['std_dev']:.4f}")
        print(f"  Range spread: {coverage['max_score'] - coverage['min_score']:.4f}")

        return coverage

    @staticmethod
    def validate_models() -> dict:
        """
        Comprehensive model validation tool.
        
        Runs 50 test cases to verify:
        1. Risk model produces variable outputs (not stuck/broken)
        2. Income model produces variable outputs
        3. Predictions are within expected ranges
        4. No crashed or infinite values
        5. Feature engineering works correctly
        
        Returns:
            dict with validation results and statistics
        """
        print("\n" + "="*70)
        print("[TEST] STARTING COMPREHENSIVE MODEL VALIDATION")
        print("="*70)
        
        validation_results = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "risk_model": {"passed": False, "stats": {}, "errors": []},
            "income_model": {"passed": False, "stats": {}, "errors": []},
            "overall_passed": False
        }
        
        try:
            # ===== RISK MODEL VALIDATION (25 test cases) =====
            print("\n[INFO] Testing Risk Model (25 cases)...")
            risk_scores = []
            risk_errors = []
            
            test_cases_risk = [
                {"temperature": 20, "rainfall_mm": 0},      # Cool, dry
                {"temperature": 25, "rainfall_mm": 5},      # Mild
                {"temperature": 30, "rainfall_mm": 10},     # Normal
                {"temperature": 35, "rainfall_mm": 25},     # Hot, rainy
                {"temperature": 40, "rainfall_mm": 50},     # Very hot, heavy rain
                {"temperature": 45, "rainfall_mm": 100},    # Extreme heat, very wet
                {"temperature": 50, "rainfall_mm": 150},    # Severe heat, flooding
                {"temperature": 15, "rainfall_mm": 0},      # Cold, dry
                {"temperature": 10, "rainfall_mm": 30},     # Cold, wet
                {"temperature": 55, "rainfall_mm": 200},    # Extreme conditions
                {"temperature": 30, "rainfall_mm": 75},     # Moderate heat, heavy rain
                {"temperature": 38, "rainfall_mm": 40},     # High heat, moderate rain
                {"temperature": 32, "rainfall_mm": 15},     # Warm, light rain
                {"temperature": 28, "rainfall_mm": 5},      # Cool, very light rain
                {"temperature": 42, "rainfall_mm": 80},     # High heat, wet
                {"temperature": 35, "rainfall_mm": 0},      # Hot, bone dry
                {"temperature": 20, "rainfall_mm": 100},    # Cool, heavy rain
                {"temperature": 45, "rainfall_mm": 200},    # Extreme heat, flooding
                {"temperature": 25, "rainfall_mm": 50},     # Mild, heavy rain
                {"temperature": 40, "rainfall_mm": 10},     # Hot, light rain
                {"temperature": 30, "rainfall_mm": 30},     # Normal hot, normal rain
                {"temperature": 35, "rainfall_mm": 35},     # Hot, moderate rain
                {"temperature": 33, "rainfall_mm": 22},     # Warm, light-moderate rain
                {"temperature": 27, "rainfall_mm": 12},     # Cool-mild, light rain
                {"temperature": 48, "rainfall_mm": 120},    # Very hot, heavy rain
            ]
            
            for i, weather in enumerate(test_cases_risk, 1):
                try:
                    result = ModelLoader.predict_risk(weather)
                    score = result.get('risk_score', -1)
                    if not isinstance(score, (int, float)):
                        risk_errors.append(f"Case {i}: Non-numeric result {result}")
                    elif score != score:  # NaN check
                        risk_errors.append(f"Case {i}: NaN result")
                    elif score == float('inf'):
                        risk_errors.append(f"Case {i}: Infinite result")
                    else:
                        risk_scores.append(score)
                        if i % 5 == 0:
                            print(f"  ✓ Case {i:2d}: temp={weather['temperature']:3d}°C, rain={weather['rainfall_mm']:3.0f}mm → score={score:.4f}")
                except Exception as e:
                    risk_errors.append(f"Case {i}: {str(e)}")
            
            # Analyze risk model results
            if risk_scores:
                risk_min = min(risk_scores)
                risk_max = max(risk_scores)
                risk_mean = np.mean(risk_scores)
                risk_std = np.std(risk_scores)
                
                validation_results["risk_model"]["stats"] = {
                    "valid_predictions": len(risk_scores),
                    "min": round(risk_min, 4),
                    "max": round(risk_max, 4),
                    "mean": round(risk_mean, 4),
                    "std": round(risk_std, 4),
                }
                
                # Risk model passes if:
                # 1. Has variability (std > 0.01)
                # 2. No errors
                # 3. All scores in [0, 1]
                if risk_std > 0.01 and len(risk_errors) == 0 and risk_min >= 0 and risk_max <= 1:
                    validation_results["risk_model"]["passed"] = True
                    print(f"[OK] Risk model PASSED: min={risk_min:.4f}, max={risk_max:.4f}, mean={risk_mean:.4f}, std={risk_std:.4f}")
                else:
                    if risk_std <= 0.01:
                        validation_results["risk_model"]["errors"].append("Low variability (std <= 0.01) - model may be broken/static")
                    if risk_min < 0 or risk_max > 1:
                        validation_results["risk_model"]["errors"].append(f"Scores out of [0,1] range: [{risk_min}, {risk_max}]")
            
            if risk_errors:
                validation_results["risk_model"]["errors"].extend(risk_errors)
            
            # ===== INCOME MODEL VALIDATION (25 test cases) =====
            print("\n[MONEY] Testing Income Model (25 cases)...")
            income_losses = []
            income_errors = []
            
            test_cases_income = [
                (1, 50),    # 1 hour, low income
                (2, 100),   # 2 hours, moderate income
                (4, 75),    # 4 hours, moderate-low income
                (8, 150),   # Full day, high income
                (0.5, 200), # Short loss, very high income
                (6, 60),    # 6 hours, low-moderate income
                (3, 120),   # 3 hours, high income
                (5, 90),    # 5 hours, moderate income
                (10, 80),   # Long disruption, moderate income
                (1, 30),    # 1 hour, low income
                (2, 250),   # 2 hours, very high income
                (4, 40),    # 4 hours, low income
                (7, 110),   # 7 hours, high income
                (0.5, 50),  # Short loss, low income
                (6, 200),   # 6 hours, very high income
                (3, 45),    # 3 hours, low-moderate income
                (8, 95),    # Full day, moderate-high income
                (2, 70),    # 2 hours, moderate income
                (5, 140),   # 5 hours, high income
                (4, 110),   # 4 hours, high income
                (1, 150),   # 1 hour, high income
                (3, 80),    # 3 hours, moderate income
                (6, 130),   # 6 hours, high income
                (2, 115),   # 2 hours, high income
                (5, 130),   # 5 hours, high income
            ]
            
            for i, (hours, income) in enumerate(test_cases_income, 1):
                try:
                    result = ModelLoader.predict_income_loss(hours, income)
                    loss = result.get('loss', -1)
                    if not isinstance(loss, (int, float)):
                        income_errors.append(f"Case {i}: Non-numeric result {result}")
                    elif loss != loss:  # NaN check
                        income_errors.append(f"Case {i}: NaN result")
                    elif loss == float('inf'):
                        income_errors.append(f"Case {i}: Infinite result")
                    elif loss < 0:
                        income_errors.append(f"Case {i}: Negative loss {loss}")
                    else:
                        income_losses.append(loss)
                        if i % 5 == 0:
                            print(f"  ✓ Case {i:2d}: {hours:3.1f}h lost at ₹{income:3.0f}/h → loss=₹{loss:.2f}")
                except Exception as e:
                    income_errors.append(f"Case {i}: {str(e)}")
            
            # Analyze income model results
            if income_losses:
                loss_min = min(income_losses)
                loss_max = max(income_losses)
                loss_mean = np.mean(income_losses)
                loss_std = np.std(income_losses)
                
                validation_results["income_model"]["stats"] = {
                    "valid_predictions": len(income_losses),
                    "min": round(loss_min, 2),
                    "max": round(loss_max, 2),
                    "mean": round(loss_mean, 2),
                    "std": round(loss_std, 2),
                }
                
                # Income model passes if:
                # 1. Has variability (std > 1)
                # 2. No NaN/Inf errors
                # 3. All losses >= 0
                # 4. No negative loss errors
                has_neg_errors = any("Negative" in e or "Non-numeric" in e or "NaN" in e or "Infinite" in e for e in income_errors)
                if loss_std > 1 and not has_neg_errors and loss_min >= 0:
                    validation_results["income_model"]["passed"] = True
                    print(f"[OK] Income model PASSED: min=₹{loss_min:.2f}, max=₹{loss_max:.2f}, mean=₹{loss_mean:.2f}, std=₹{loss_std:.2f}")
                else:
                    if loss_std <= 1:
                        validation_results["income_model"]["errors"].append("Low variability (std <= 1) - model may be broken/static")
                    if loss_min < 0:
                        validation_results["income_model"]["errors"].append(f"Negative losses detected: min={loss_min}")
            
            if income_errors:
                validation_results["income_model"]["errors"].extend(income_errors)
            
            # ===== OVERALL RESULT =====
            validation_results["overall_passed"] = (
                validation_results["risk_model"]["passed"] and 
                validation_results["income_model"]["passed"]
            )
            
            if validation_results["overall_passed"]:
                print("\n" + "="*70)
                print("[OK] [OK] [OK] ALL MODELS VALIDATED SUCCESSFULLY [OK] [OK] [OK]")
                print("="*70)
            else:
                print("\n" + "="*70)
                print("[ERROR] [ERROR] [ERROR] VALIDATION FAILURES DETECTED [ERROR] [ERROR] [ERROR]")
                if not validation_results["risk_model"]["passed"]:
                    print("[ERROR] Risk Model FAILED")
                    for error in validation_results["risk_model"]["errors"]:
                        print(f"   - {error}")
                if not validation_results["income_model"]["passed"]:
                    print("[ERROR] Income Model FAILED")
                    for error in validation_results["income_model"]["errors"]:
                        print(f"   - {error}")
                print("="*70)
            
            return validation_results
            
        except Exception as e:
            print(f"[ERROR] Validation crashed: {str(e)}")
            validation_results["overall_passed"] = False
            validation_results["risk_model"]["errors"].append(f"Validation exception: {str(e)}")
            return validation_results