import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

@pytest.fixture
def setup_engine():
    handler = GraphHandler()
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "tests", "mock_data", "animals_ontology_small.json")
    facts_path = os.path.join(project_dir, "tests", "mock_data", "animals_facts.json")
    language_rules_path = os.path.join(project_dir, "tests", "mock_data", "animals_language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    generator = ResponseGeneratorSimple(handler)
    return reasoner, generator

def test_query_classification_animal(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("هل الأسد حيوان؟")
    assert res["type"] == "classification"
    assert res["result"] is True
    
    response = generator.generate(res)
    assert "أسد هو حيوان" in response or "الأسد هو حيوان" in response

def test_query_classification_predator(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("هل الأسد مفترس؟")
    assert res["type"] == "classification"
    assert res["result"] is True
    
    response = generator.generate(res)
    assert "أسد هو مفترس" in response or "الأسد هو مفترس" in response

def test_query_location(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("أين يعيش الأسد؟")
    assert res["type"] == "location"
    assert res["location"] == "savanna"
    
    response = generator.generate(res)
    assert "السافانا" in response

def test_query_hypothetical(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("لو الأسد عاش في القطب، ماذا يحتاج؟")
    assert res["type"] == "hypothetical"
    assert res["needs_adaptation"] is True
    assert res["transferred_property"] == "thick_fur"
    assert res["analogy_candidate"] == "polar_bear"
    
    response = generator.generate(res)
    assert "فرو سميك" in response
    assert "دب قطبي" in response

def test_query_comparison(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("ما الفرق بين الأسد والدب القطبي؟")
    assert res["type"] == "comparison"
    
    response = generator.generate(res)
    assert "أسد" in response
    assert "دب قطبي" in response
    assert "فرو خفيف" in response or "فرو خفيف" in response or "فرو سميك" in response

def test_query_unknown_fail_safe(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("هل الفيل بيطير؟")
    assert res["type"] == "unknown"
    assert res["confidence"] == 0.0
    
    response = generator.generate(res)
    assert "معنديش أي معلومة" in response or "معرفش" in response

def test_query_multi_turn_context(setup_engine):
    reasoner, generator = setup_engine
    
    # Turn 1: Establish subject "الأسد"
    res1 = reasoner.process_query("هل الأسد حيوان؟")
    assert res1["type"] == "classification"
    assert res1["result"] is True
    
    # Turn 2: Query location implicitly (using verb 'يعيش')
    res2 = reasoner.process_query("أين يعيش؟")
    assert res2["type"] == "location"
    assert res2["concept"] == "feline_carnivore"
    assert res2["location"] == "savanna"
    
    response = generator.generate(res2)
    assert "السافانا" in response

def test_world_switching_and_conflict(setup_engine):
    reasoner, generator = setup_engine
    
    # 1. Check in reality
    res1 = reasoner.process_query("هل الشمس تشرق من الشرق؟")
    assert res1["type"] == "classification"
    assert res1["result"] is True
    
    # 2. Teach new fact in fantasy world and query (combined query)
    res2 = reasoner.process_query("في عالم خيالي الشمس تشرق من الغرب. هل الشمس تشرق من الشرق؟")
    assert res2["type"] == "classification"
    assert res2["result"] is False
    
    # 3. Query direction in active fantasy world
    res3 = reasoner.process_query("أين تشرق الشمس؟")
    assert res3["type"] == "location"
    assert res3["location"] == "c_west"


def test_relation_path_queries(setup_engine):
    reasoner, generator = setup_engine
    
    # Test 1: Direct specific relationship (lives_in)
    res_direct = reasoner.process_query("ما علاقة الأسد بالسافانا؟")
    assert res_direct["type"] == "relation_path"
    assert res_direct["is_deep"] is False
    assert res_direct["path_found"] is True
    assert len(res_direct["path_nodes"]) == 2
    
    response_direct = generator.generate(res_direct)
    assert "علاقة مباشرة" in response_direct
    assert "أسد" in response_direct
    assert "السافانا" in response_direct
    
    # Test 2: Indirect/deep relationship exists, but query is specific (should return path_found=False)
    res_indirect_specific = reasoner.process_query("ما علاقة الأسد بعين الماء؟")
    assert res_indirect_specific["type"] == "relation_path"
    assert res_indirect_specific["is_deep"] is False
    assert res_indirect_specific["path_found"] is False
    
    # Test 3: Indirect/deep relationship with deep keyword (should find path)
    res_deep = reasoner.process_query("ما العلاقة العميقة بين الأسد وعين الماء؟")
    assert res_deep["type"] == "relation_path"
    assert res_deep["is_deep"] is True
    assert res_deep["path_found"] is True
    assert len(res_deep["path_nodes"]) >= 3
    
    response_deep = generator.generate(res_deep)
    assert "علاقة غير مباشر" in response_deep or "عميق" in response_deep
    assert "أسد" in response_deep
    assert "عين" in response_deep or "نبع" in response_deep

def test_query_classification_multiword(setup_engine):
    reasoner, generator = setup_engine
    
    # "polar_bear" (دب قطبي) is a "carnivore" which is an "animal" (كائن حي / حيوان)
    # This query contains two multi-word concepts: "الدب القطبي" and "كائن حي"
    res = reasoner.process_query("هل الدب القطبي كائن حي؟")
    assert res["type"] == "classification"
    assert res["result"] is True
    assert res["concept1"] == "polar_bear"
    assert res["concept2"] == "animal"
    
    response = generator.generate(res)
    assert "دب قطبي" in response or "الدب القطبي" in response
    assert "كائن حي" in response or "حيوان" in response


def test_wh_query_exclusion(setup_engine):
    reasoner, generator = setup_engine
    
    # "why did Alistair find the golden key?" should not resolve as classification.
    # It contains "did" but starts with "why", so it is a Wh-query.
    # Because there is no causal rule, it must fall back to "unknown".
    res = reasoner.process_query("why did Alistair find the golden key?", language="en")
    assert res["type"] == "unknown"
    
    # "where does the polar bear live?" is a Wh-query.
    res2 = reasoner.process_query("where does the polar bear live?", language="en")
    assert res2["type"] == "location"
    assert res2["location"] == "arctic"


def test_trace_translations(setup_engine):
    reasoner, generator = setup_engine
    from src.manager.multilingual_persona_engine import MultilingualPersonaEngine
    engine = MultilingualPersonaEngine(reasoner.handler)
    renderer = engine.expression_renderer
    
    # 1. English trace translation verification for classification query
    res_en = reasoner.process_query("Is the dinosaur fur?", language="en")
    # Trace step translating "لا يوجد علاقة تصنيفية..." to English
    translated = [renderer.translate_trace_step(step, "en") for step in res_en.get("trace", [])]
    assert any("No taxonomic relation or logical rule connects the two concepts" in step for step in translated)

    # 2. French trace translation verification for classification query
    res_fr = reasoner.process_query("Est-ce que le dinosaure est de la fourrure?", language="fr")
    translated_fr = [renderer.translate_trace_step(step, "fr") for step in res_fr.get("trace", [])]
    assert any("Aucune relation taxonomique ou règle logique ne relie les deux concepts" in step for step in translated_fr)




