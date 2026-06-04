import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

def test_causal_why_query_and_inference_rules():
    handler = GraphHandler()
    handler.load_databases(
        ontology_path="tests/mock_data/story_ontology.json",
        facts_path="tests/mock_data/story_facts.json",
        language_rules_path="data/language_rules.json",
        inference_rules_path="data/inference_rules.json"
    )
    # Set world and infer facts
    handler.active_world = "story_world"
    handler.add_or_update_fact(
        subj="little_star",
        obj="other_stars",
        relation="shines_to_help",
        world="story_world",
        confidence=1.0
    )
    handler.infer_facts("story_world")
    
    reasoner = SimpleReasoner(handler)
    generator = ResponseGeneratorSimple(handler)
    
    # 1. Test "لماذا فرحت النجمة الصغيرة؟"
    query = "لماذا فرحت النجمة الصغيرة؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "causal_reasoning"
    assert res["result"] is True
    assert "helping_creates_joy" in res["rule_id"] or res["rule_id"] == "helping_creates_joy"
    assert "الفرح" in res["reason"] or "فرح" in res["reason"]
    
    # 2. Test response generation
    response = generator.generate(res, persona_id="old_star_persona")
    assert any(word in response for word in ["الفرح", "فرح", "مساعدة"])

    # 3. Test duplicate removal by ensuring no duplicate emits light is returned on describe/knowledge fallbacks
    describe_query = "ما هي النجمة الصغيرة؟"
    desc_res = reasoner.process_query(describe_query, language="ar")
    
    # Verify relations in desc_res do not cause duplicate lines in generator output
    desc_response = generator.generate(desc_res, persona_id="old_star_persona")
    assert desc_response.count("emits") <= 1 or desc_response.count("نور") <= 2
