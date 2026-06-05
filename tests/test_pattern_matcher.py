import os
import json
import pytest
from src.reasoner.pattern_matcher import GenericPatternMatcher

def test_basic_pattern_matching():
    # Load language rules
    rules_path = "tests/mock_data/animals_language_rules.json"
    matcher = GenericPatternMatcher(rules_path)
    
    # 1. Test classification query
    result = matcher.match("هل الأسد حيوان؟")
    assert result is not None
    assert result.intent == "classification"
    assert result.extracted_entities.get("concept1") == "الأسد"
    assert result.extracted_entities.get("concept2") == "حيوان"
    
    # 2. Test location query
    result = matcher.match("أين يعيش الأسد؟")
    assert result is not None
    assert result.intent == "location"
    assert result.extracted_entities.get("concept") == "الأسد"

def test_fuzzy_matching():
    rules_path = "tests/mock_data/animals_language_rules.json"
    matcher = GenericPatternMatcher(rules_path)
    
    # Levenshtein distance check with minor spelling typo
    # "هل الاسد حيون؟" -> "حيوان" is close
    result = matcher.match("هل الاسد حيون؟")
    assert result is not None
    assert result.intent == "classification"
    assert "الاسد" in result.extracted_entities.values() or "الأسد" in result.extracted_entities.values()

def test_pattern_matching_failure():
    rules_path = "tests/mock_data/animals_language_rules.json"
    matcher = GenericPatternMatcher(rules_path)
    
    # Random words should not match
    result = matcher.match("كلام عشوائي لا معنى له على الإطلاق")
    assert result is None
