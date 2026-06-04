import os
import json
import pytest
from api import load_procedural_steps, save_procedural_steps

def test_procedural_load_save():
    # Save a test procedure
    test_data = {
        "test_procedure": ["step 1", "step 2"]
    }
    
    from api import procedural_steps_path
    original_exists = os.path.exists(procedural_steps_path)
    original_data = {}
    if original_exists:
        try:
            with open(procedural_steps_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
        except Exception:
            pass
            
    try:
        # Save test data
        assert save_procedural_steps(test_data) == True
        
        # Load and verify
        loaded = load_procedural_steps()
        assert "test_procedure" in loaded
        assert loaded["test_procedure"] == ["step 1", "step 2"]
        
    finally:
        # Restore original file
        if original_exists:
            with open(procedural_steps_path, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, ensure_ascii=False, indent=2)
        elif os.path.exists(procedural_steps_path):
            try:
                os.remove(procedural_steps_path)
            except Exception:
                pass
