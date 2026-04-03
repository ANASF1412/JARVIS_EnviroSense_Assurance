import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.model_loader import ModelLoader
from services.zero_touch_pipeline import ZeroTouchPipeline
import json

def run_validation():
    print("--- 1. SENSITIVITY ANALYSIS ---")
    sensitivity = ModelLoader.analyze_risk_sensitivity()
    print("SENSITIVITY RESULT: ", json.dumps(sensitivity, indent=2))
    
    print("\n--- 2. PROBABILITY DISTRIBUTION CHECK ---")
    coverage = ModelLoader.analyze_model_coverage()
    print("COVERAGE RESULT: ", json.dumps(coverage, indent=2))
    
    print("\n--- 3. CONFIDENCE DISTRIBUTION & VALIDATION RESULTS ---")
    validation = ModelLoader.validate_models()
    
    print("\n--- 4. STRESS TEST ---")
    stress = ModelLoader.perform_stress_testing()
    
    print("\n--- 5. END-TO-END ZERO-TOUCH PIPELINE TEST ---")
    pipeline = ZeroTouchPipeline()
    result = pipeline.run_pipeline()
    print("PIPELINE RESULT: ", json.dumps(result, default=str, indent=2))

if __name__ == "__main__":
    run_validation()
