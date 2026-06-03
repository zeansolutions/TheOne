import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

@pytest.fixture
def setup_advanced_engine():
    handler = GraphHandler()
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "data", "animals_ontology_small.json")
    facts_path = os.path.join(project_dir, "data", "animals_facts.json")
    language_rules_path = os.path.join(project_dir, "data", "animals_language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    generator = ResponseGeneratorSimple(handler)
    return handler, reasoner, generator

# --- LEVEL 1: Semantic Roles ---
def test_semantic_roles(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    # Teach fact first
    reasoner.process_query("الأسد افترس الغزال.", language="ar")
    
    # Text input with predicate "افترس"
    query = "من الذي افترس الغزال؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "semantic_roles"
    assert res["predicate"] == "hunting"
    assert res["roles"]["AGENT"] == "feline_carnivore"
    assert res["roles"]["PATIENT"] == "gazelle"
    
    response = generator.generate(res)
    assert "الأدوار الدلالية" in response
    assert "AGENT: أسد" in response
    assert "PATIENT: غزال" in response

# --- LEVEL 2: Temporal Logic ---
def test_temporal_logic(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    query = "هل انقراض الديناصورات قبل الآن؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "temporal_logic"
    assert res["result"] is True
    assert res["event"] == "dinosaur_extinction"
    
    response = generator.generate(res)
    assert "الترتيب الزمني" in response
    assert "dinosaur_extinction" in response
    assert "قبل" in response

# --- LEVEL 3: Modality ---
def test_modality(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    # Necessity
    q1 = "هل يجب أن الأسد حيوان؟"
    res1 = reasoner.process_query(q1, language="ar")
    assert res1["type"] == "modality"
    assert res1["modality"] == "necessity"
    assert res1["result"] is True
    
    # Impossibility
    q2 = "هل مستحيل الأسد يكون دب قطبي؟"
    res2 = reasoner.process_query(q2, language="ar")
    assert res2["type"] == "modality"
    assert res2["modality"] == "impossibility"
    assert res2["result"] is True

# --- LEVEL 4: Causal Chains ---
def test_causal_chains(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    query = "ما هي سلسلة أسباب جوع الأسد؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "causal_chain"
    assert res["result"] is True
    assert res["initial_state"] == "feline_carnivore"
    
    response = generator.generate(res)
    assert "التسلسل السببي" in response
    assert "hunger" in response
    assert "predation" in response
    assert "death" in response

# --- LEVEL 5: Quantifiers ---
def test_quantifiers(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    query = "هل كل الأسود حيوانات؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "quantifier"
    assert res["quantifier"] == "universal"
    assert res["result"] is True
    
    response = generator.generate(res)
    assert "سور القضية" in response
    assert "صحيحة منطقياً" in response

# --- LEVEL 6: Negation & Polarity ---
def test_negation_polarity(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    query = "هل الأسد ليس دب قطبي؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "negation"
    assert res["result"] is True
    
    response = generator.generate(res)
    assert "استدلال النفي" in response
    assert "صحيحة" in response

# --- LEVEL 7: Entailment & Contradictions ---
def test_entailment_inference(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    # Trigger graph inference
    handler.infer_facts("reality")
    
    # Check if is_a living_thing is inferred for feline_carnivore (via entailment: animal -> living_thing)
    # feline_carnivore is_a animal -> living_thing
    res = reasoner.check_is_a_relationship("feline_carnivore", "living_thing")
    assert res["result"] is True
    assert any("الاستلزام المنطقي" in trace for trace in res["trace"])

# --- LEVEL 8: Pragmatics ---
def test_pragmatics(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    # Metaphor query: "هل ملك الغابة حيوان؟" should resolve "ملك الغابة" -> feline_carnivore
    query = "هل ملك الغابة حيوان؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "classification"
    assert res["concept1"] == "feline_carnivore"
    assert res["concept2"] == "animal"
    assert res["result"] is True
    assert any("[PRAGMATICS] تم حل المجاز" in trace for trace in res["trace"])

# --- LEVEL 9: Comparison & Similarity Scales ---
def test_comparison_scales(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    # Direct comparison on strength scale: lion vs gazelle
    query = "هل الأسد أقوى من الغزال؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "comparison_scale"
    assert res["property_name"] == "strength"
    assert res["result"] is True
    
    response = generator.generate(res)
    assert "مقارنة الكائنات على مقياس [strength]" in response
    assert "أكبر من" in response

# --- LEVEL 10: Anomaly & Exception Detection ---
def test_anomaly_detection(setup_advanced_engine):
    handler, reasoner, generator = setup_advanced_engine
    
    query = "هل هناك أسد نباتي شاذ؟"
    res = reasoner.process_query(query, language="ar")
    
    assert res["type"] == "anomaly"
    assert res["result"] is True
    assert res["anomaly_type"] == "vegetarian_lion"
    assert res["anomaly_score"] == 0.99
    
    response = generator.generate(res)
    assert "تم رصد استثناء وشذوذ" in response
    assert "vegetarian_lion" in response
    assert "rare_genetic_mutation" in response
