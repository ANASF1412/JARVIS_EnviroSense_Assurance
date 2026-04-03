"""
FEATURE VALIDATION UTILITIES
Validate ML input features before predictions
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
import streamlit as st


class FeatureValidator:
    """Validate features for ML models - fail-safe with detailed error messages."""

    # ===== RISK MODEL SCHEMA =====
    RISK_MODEL_FEATURES = ["Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"]
    RISK_FEATURE_RANGES = {
        "Temperature": (0, 70),           # Celsius
        "Rainfall_mm": (0, 500),          # Millimeters
        "Humidity": (0, 100),             # Percentage
        "Wind_Speed": (0, 100),           # km/h
        "Severity": (1, 5),               # Scale 1-5
    }

    # ===== INCOME MODEL SCHEMA =====
    INCOME_MODEL_FEATURES = [
        "Orders_Per_Day", "Working_Hours", "Earnings_Per_Day",
        "Temperature", "Rainfall_mm", "Humidity", "Wind_Speed", "Severity"
    ]
    INCOME_FEATURE_RANGES = {
        "Orders_Per_Day": (0, 100),
        "Working_Hours": (0, 24),
        "Earnings_Per_Day": (0, 10000),
        "Temperature": (0, 70),
        "Rainfall_mm": (0, 500),
        "Humidity": (0, 100),
        "Wind_Speed": (0, 100),
        "Severity": (1, 5),
    }

    @staticmethod
    def validate_risk_features(features: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate features for risk model.

        Args:
            features: Dict with feature values

        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []

        # Check all required features present
        missing = set(FeatureValidator.RISK_MODEL_FEATURES) - set(features.keys())
        if missing:
            errors.append(f"Missing features: {missing}")
            return False, errors

        # Check each feature
        for feature, value in features.items():
            if feature not in FeatureValidator.RISK_MODEL_FEATURES:
                errors.append(f"Unknown feature: {feature}")
                continue

            # Type check
            if not isinstance(value, (int, float)):
                errors.append(f"{feature}: Expected numeric, got {type(value).__name__}")
                continue

            # Range check
            min_val, max_val = FeatureValidator.RISK_FEATURE_RANGES[feature]
            if not (min_val <= value <= max_val):
                errors.append(
                    f"{feature}: Value {value} out of range [{min_val}, {max_val}]"
                )

        # NaN/Inf checks
        for feature, value in features.items():
            if isinstance(value, float):
                if pd.isna(value):
                    errors.append(f"{feature}: Cannot be NaN")
                elif np.isinf(value):
                    errors.append(f"{feature}: Cannot be infinite")

        return len(errors) == 0, errors

    @staticmethod
    def validate_income_features(features: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate features for income model.

        Args:
            features: Dict with feature values

        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []

        # Check all required features present
        missing = set(FeatureValidator.INCOME_MODEL_FEATURES) - set(features.keys())
        if missing:
            errors.append(f"Missing features: {missing}")
            return False, errors

        # Check each feature
        for feature, value in features.items():
            if feature not in FeatureValidator.INCOME_MODEL_FEATURES:
                errors.append(f"Unknown feature: {feature}")
                continue

            # Type check
            if not isinstance(value, (int, float)):
                errors.append(f"{feature}: Expected numeric, got {type(value).__name__}")
                continue

            # Range check
            min_val, max_val = FeatureValidator.INCOME_FEATURE_RANGES[feature]
            if not (min_val <= value <= max_val):
                errors.append(
                    f"{feature}: Value {value} out of range [{min_val}, {max_val}]"
                )

        # NaN/Inf checks
        for feature, value in features.items():
            if isinstance(value, float):
                if pd.isna(value):
                    errors.append(f"{feature}: Cannot be NaN")
                elif np.isinf(value):
                    errors.append(f"{feature}: Cannot be infinite")

        return len(errors) == 0, errors

    @staticmethod
    def safe_create_dataframe(features: Dict[str, float], model_type: str = "risk") -> Tuple[bool, pd.DataFrame | None, List[str]]:
        """
        Safely create DataFrame with validation.

        Args:
            features: Feature dictionary
            model_type: "risk" or "income"

        Returns:
            (success: bool, dataframe: pd.DataFrame or None, errors: List[str])
        """
        if model_type == "risk":
            is_valid, errors = FeatureValidator.validate_risk_features(features)
            expected_features = FeatureValidator.RISK_MODEL_FEATURES
        elif model_type == "income":
            is_valid, errors = FeatureValidator.validate_income_features(features)
            expected_features = FeatureValidator.INCOME_MODEL_FEATURES
        else:
            return False, None, [f"Unknown model_type: {model_type}"]

        if not is_valid:
            return False, None, errors

        try:
            # Create DataFrame with correct column order
            df = pd.DataFrame([{k: features[k] for k in expected_features}])
            return True, df, []
        except Exception as e:
            return False, None, [f"DataFrame creation failed: {str(e)}"]

    @staticmethod
    def log_validation_errors(errors: List[str], feature_type: str = "features") -> None:
        """Log validation errors to console and Streamlit."""
        if not errors:
            return

        print(f"❌ VALIDATION ERRORS ({feature_type}):")
        for error in errors:
            print(f"   - {error}")

        error_text = "\n".join([f"• {e}" for e in errors])
        st.error(f"❌ {feature_type} validation failed:\n{error_text}")


class ErrorHandler:
    """Centralized error handling for ML pipeline."""

    @staticmethod
    def handle_model_error(error: Exception, context: str = "", fallback_value: Any = None) -> Any:
        """
        Handle model errors gracefully.

        Args:
            error: The exception
            context: Description of what was being done
            fallback_value: Value to return on error

        Returns:
            fallback_value if error, else None
        """
        error_msg = f"❌ Model error in {context}: {str(error)}"
        print(error_msg)
        st.warning(error_msg)

        if fallback_value is not None:
            print(f"💡 Using fallback value: {fallback_value}")

        return fallback_value

    @staticmethod
    def ensure_numeric_output(value: Any, default: float = 0.5, range_limits: Tuple[float, float] = (0.0, 1.0)) -> float:
        """
        Ensure output is valid numeric.

        Args:
            value: Value to validate
            default: Default value if invalid
            range_limits: (min, max) tuple for bounds checking

        Returns:
            Valid float in range
        """
        try:
            num_value = float(value)

            # Check for NaN/Inf
            if not (num_value == num_value) or np.isinf(num_value):  # NaN check
                return default

            # Bounds check
            min_val, max_val = range_limits
            if not (min_val <= num_value <= max_val):
                num_value = max(min_val, min(max_val, num_value))

            return num_value
        except (TypeError, ValueError):
            return default

    @staticmethod
    def validate_output(output: Any, expected_type: type, range_limits: Tuple[float, float] | None = None) -> Tuple[bool, str]:
        """
        Validate model output.

        Args:
            output: Value to validate
            expected_type: Expected Python type
            range_limits: Optional (min, max) for numeric validation

        Returns:
            (is_valid: bool, message: str)
        """
        # Type check
        if not isinstance(output, expected_type):
            return False, f"Expected {expected_type.__name__}, got {type(output).__name__}"

        # Numeric specific checks
        if expected_type in (int, float):
            if pd.isna(output):
                return False, "Output is NaN"
            if np.isinf(output):
                return False, "Output is infinite"

            if range_limits:
                min_val, max_val = range_limits
                if not (min_val <= output <= max_val):
                    return False, f"Value {output} out of range [{min_val}, {max_val}]"

        return True, "Valid"


class DataQualityChecker:
    """Check data quality before sending to models."""

    @staticmethod
    def check_missing_values(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """Check for missing required fields."""
        missing = [f for f in required_fields if f not in data or data[f] is None]
        if missing:
            return False, [f"Missing fields: {missing}"]
        return True, []

    @staticmethod
    def check_outliers(value: float, feature: str, z_score_threshold: float = 3.0) -> Tuple[bool, str]:
        """
        Simple outlier check using z-score concept.
        (In production, you'd use historical distribution)
        """
        # Simple heuristic ranges for weather data
        if feature == "Temperature" and not (-15 <= value <= 60):
            return False, f"Temperature {value}°C is extreme"
        if feature == "Rainfall_mm" and value > 300:
            return False, f"Rainfall {value}mm is extreme"
        if feature == "Humidity" and not (0 <= value <= 100):
            return False, f"Humidity {value}% is out of range"

        return True, "Normal"

    @staticmethod
    def get_data_quality_report(features: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive data quality report."""
        report = {
            "total_fields": len(features),
            "valid_fields": 0,
            "invalid_fields": [],
            "issues": []
        }

        for field, value in features.items():
            if value is None or (isinstance(value, float) and (pd.isna(value) or np.isinf(value))):
                report["invalid_fields"].append(field)
                report["issues"].append(f"{field}: Invalid value {value}")
            else:
                report["valid_fields"] += 1

        report["quality_score"] = (report["valid_fields"] / report["total_fields"]) * 100 if report["total_fields"] > 0 else 0

        return report
