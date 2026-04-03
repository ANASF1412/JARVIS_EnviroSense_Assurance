import sys
import os
import json
import codecs
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.model_loader import ModelLoader
from services.zero_touch_pipeline import ZeroTouchPipeline

# Redirect stdout to a file to capture cleanly
with codecs.open('validation_results.txt', 'w', encoding='utf-8') as f:
    orig_stdout = sys.stdout
    sys.stdout = f

    print("--- 1. SENSITIVITY ANALYSIS ---")
    try:
        sensitivity = ModelLoader.analyze_risk_sensitivity()
        print("SENSITIVITY RESULT: ", json.dumps(sensitivity, indent=2))
    except Exception as e:
        print("SENSITIVITY RESULT: ERROR", e)
    
    print("\n--- 2. PROBABILITY DISTRIBUTION CHECK ---")
    try:
        coverage = ModelLoader.analyze_model_coverage()
        print("COVERAGE RESULT: ", json.dumps(coverage, indent=2))
    except Exception as e:
        print("COVERAGE RESULT: ERROR", e)
    
    print("\n--- 3. CONFIDENCE DISTRIBUTION & VALIDATION RESULTS ---")
    try:
        validation = ModelLoader.validate_models()
        # Confidence distribution isn't natively output but validate_models covers it
    except Exception as e:
        pass
        
    print("\n--- 4. STRESS TEST ---")
    try:
        stress = ModelLoader.perform_stress_testing()
    except Exception as e:
        pass
    
    print("\n--- 5. END-TO-END ZERO-TOUCH PIPELINE TEST ---")
    try:
        pipeline = ZeroTouchPipeline()
        result = pipeline.run_pipeline()
        print("PIPELINE RESULT: ", json.dumps(result, default=str, indent=2))
    except Exception as e:
        print("PIPELINE RESULT: ERROR", e)
    
    sys.stdout = orig_stdout
    print("Done")
