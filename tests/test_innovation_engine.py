import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

@pytest.fixture
def setup_innovation_engine():
    handler = GraphHandler()
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "data", "ontology.json")
    facts_path = os.path.join(project_dir, "data", "facts.json")
    language_rules_path = os.path.join(project_dir, "data", "language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    generator = ResponseGeneratorSimple(handler)
    return handler, reasoner, generator

def test_decomposition_and_direct_match(setup_innovation_engine):
    handler, reasoner, generator = setup_innovation_engine
    
    # Programmatically define entities for innovation
    handler.graph.add_node("Solar_Energy", type="concept", labels=["Solar Energy", "شمس"])
    handler.graph.add_node("Bread_Baking", type="concept", labels=["Bread Baking", "خبز"])
    handler.graph.add_node("Heat", type="concept", labels=["Heat", "حرارة"])
    
    handler.graph.add_edge("Solar_Energy", "Heat", relation="provides", type="fact", world="reality")
    handler.graph.add_edge("Bread_Baking", "Heat", relation="requires", type="fact", world="reality")
    
    # 1. Test get_decompositions
    decomp_solar = reasoner.innovation_engine.get_decompositions("Solar_Energy", "reality")
    assert "Heat" in decomp_solar["capabilities"]
    
    decomp_bread = reasoner.innovation_engine.get_decompositions("Bread_Baking", "reality")
    assert "Heat" in decomp_bread["requirements"]

    # 2. Test innovate - Incomplete Validation
    res = reasoner.innovation_engine.innovate("Solar_Energy", "Bread_Baking", "reality", "en")
    assert res["success"] is True
    assert res["matching_property"] == "Heat"
    assert res["match_type"] == "direct"
    assert res["validation_status"] == "incomplete_validation"
    assert "mass" in res["validation_message"]

    # Test generation of incomplete validation response
    query_res = {
        "type": "innovation",
        "result": True,
        "concept1_label": "Solar Energy",
        "concept2_label": "Bread Baking",
        "matching_property": "Heat",
        "match_type": "direct",
        "path_str": "Heat",
        "validation_status": res["validation_status"],
        "validation_message": res["validation_message"]
    }
    response = generator.generate(query_res, language="en")
    assert "Physical validation incomplete" in response

def test_thermodynamic_validation_success(setup_innovation_engine):
    handler, reasoner, generator = setup_innovation_engine
    
    handler.graph.add_node("Solar_Energy", type="concept", labels=["Solar Energy", "شمس"])
    handler.graph.add_node("Bread_Baking", type="concept", labels=["Bread Baking", "خبز"])
    handler.graph.add_node("Heat", type="concept", labels=["Heat", "حرارة"])
    
    handler.graph.add_edge("Solar_Energy", "Heat", relation="provides", type="fact", world="reality")
    handler.graph.add_edge("Bread_Baking", "Heat", relation="requires", type="fact", world="reality")
    
    # Assign physical constants to nodes (Q_provided = 1000 J, mass = 0.5 kg, c = 2.0 J/(kg*K), delta_T = 10.0 K => Q_req = 10 J)
    handler.graph.nodes["Solar_Energy"]["energy_provided"] = 1000.0
    handler.graph.nodes["Bread_Baking"]["mass"] = 0.5
    handler.graph.nodes["Bread_Baking"]["specific_heat"] = 2.0
    handler.graph.nodes["Bread_Baking"]["temp_change"] = 10.0

    res = reasoner.innovation_engine.innovate("Solar_Energy", "Bread_Baking", "reality", "en")
    assert res["success"] is True
    assert res["validation_status"] == "validated"
    assert "sufficient to heat target" in res["validation_message"]

    # Format output using response generator
    query_res = {
        "type": "innovation",
        "result": True,
        "concept1_label": "Solar Energy",
        "concept2_label": "Bread Baking",
        "matching_property": "Heat",
        "match_type": "direct",
        "path_str": "Heat",
        "validation_status": res["validation_status"],
        "validation_message": res["validation_message"]
    }
    response = generator.generate(query_res, language="en")
    assert "Successfully innovated" in response
    assert "sufficient to heat target" in response

def test_thermodynamic_validation_fail(setup_innovation_engine):
    handler, reasoner, _ = setup_innovation_engine
    
    handler.graph.add_node("Solar_Energy", type="concept", labels=["Solar Energy", "شمس"])
    handler.graph.add_node("Bread_Baking", type="concept", labels=["Bread Baking", "خبز"])
    handler.graph.add_node("Heat", type="concept", labels=["Heat", "حرارة"])
    
    handler.graph.add_edge("Solar_Energy", "Heat", relation="provides", type="fact", world="reality")
    handler.graph.add_edge("Bread_Baking", "Heat", relation="requires", type="fact", world="reality")
    
    # Energy provided is 5 J, but required is 10 J
    handler.graph.nodes["Solar_Energy"]["energy_provided"] = 5.0
    handler.graph.nodes["Bread_Baking"]["mass"] = 0.5
    handler.graph.nodes["Bread_Baking"]["specific_heat"] = 2.0
    handler.graph.nodes["Bread_Baking"]["temp_change"] = 10.0

    res = reasoner.innovation_engine.innovate("Solar_Energy", "Bread_Baking", "reality", "en")
    assert res["success"] is True
    assert res["validation_status"] == "failed"
    assert "insufficient to heat target" in res["validation_message"]

def test_property_parsing_from_graph(setup_innovation_engine):
    handler, reasoner, _ = setup_innovation_engine
    
    handler.graph.add_node("Solar_Energy", type="concept", labels=["Solar Energy", "شمس"])
    handler.graph.add_node("Bread_Baking", type="concept", labels=["Bread Baking", "خبز"])
    handler.graph.add_node("Heat", type="concept", labels=["Heat", "حرارة"])
    
    handler.graph.add_edge("Solar_Energy", "Heat", relation="provides", type="fact", world="reality")
    handler.graph.add_edge("Bread_Baking", "Heat", relation="requires", type="fact", world="reality")
    
    # Define values as key_value nodes instead of node attributes
    handler.graph.add_node("energy_provided_15.0", type="concept", labels=["energy_provided_15.0"])
    handler.graph.add_edge("Solar_Energy", "energy_provided_15.0", relation="has_property", type="fact", world="reality")
    
    handler.graph.add_node("mass_0.5", type="concept", labels=["mass_0.5"])
    handler.graph.add_edge("Bread_Baking", "mass_0.5", relation="has_property", type="fact", world="reality")
    
    handler.graph.add_node("specific_heat_2.0", type="concept", labels=["specific_heat_2.0"])
    handler.graph.add_edge("Bread_Baking", "specific_heat_2.0", relation="has_property", type="fact", world="reality")
    
    handler.graph.add_node("temp_change_10.0", type="concept", labels=["temp_change_10.0"])
    handler.graph.add_edge("Bread_Baking", "temp_change_10.0", relation="has_property", type="fact", world="reality")

    res = reasoner.innovation_engine.innovate("Solar_Energy", "Bread_Baking", "reality", "en")
    assert res["success"] is True
    assert res["validation_status"] == "validated"
    assert "15.0 J" in res["validation_message"]

def test_indirect_path_discovery(setup_innovation_engine):
    handler, reasoner, _ = setup_innovation_engine
    
    handler.graph.add_node("Solar_Energy", type="concept", labels=["Solar Energy", "شمس"])
    handler.graph.add_node("Bread_Baking", type="concept", labels=["Bread Baking", "خبز"])
    
    # Solar_Energy provides Heat_Source
    handler.graph.add_node("Heat_Source", type="concept", labels=["Heat Source"])
    handler.graph.add_edge("Solar_Energy", "Heat_Source", relation="provides", type="fact", world="reality")
    
    # Bread_Baking requires Oven_Heat
    handler.graph.add_node("Oven_Heat", type="concept", labels=["Oven Heat"])
    handler.graph.add_edge("Bread_Baking", "Oven_Heat", relation="requires", type="fact", world="reality")
    
    # Create path: Heat_Source --is_a--> Thermal_Node --has_property--> Oven_Heat
    handler.graph.add_node("Thermal_Node", type="concept", labels=["Thermal Node"])
    handler.graph.add_edge("Heat_Source", "Thermal_Node", relation="is_a", type="fact", world="reality")
    handler.graph.add_edge("Thermal_Node", "Oven_Heat", relation="has_property", type="fact", world="reality")
    
    res = reasoner.innovation_engine.innovate("Solar_Energy", "Bread_Baking", "reality", "en")
    assert res["success"] is True
    assert res["match_type"] == "indirect"
    assert "Heat Source -> Thermal Node -> Oven Heat" in res["path_str"]

def test_simple_reasoner_process_query(setup_innovation_engine):
    handler, reasoner, generator = setup_innovation_engine
    
    # Register the concepts and lexicon rules so that query parser maps the terms
    # Solar_Energy concept
    handler.graph.add_node("solar_energy", type="concept", labels=["طاقة شمسية", "Solar Energy", "شمس"])
    handler.language_rules.setdefault("ar", {}).setdefault("lexicon", {})["الشمس"] = "solar_energy"
    handler.language_rules["ar"]["lexicon"]["شمس"] = "solar_energy"
    handler.language_rules["ar"]["lexicon"]["طاقة شمسية"] = "solar_energy"
    
    # Bread_Baking concept
    handler.graph.add_node("bread_baking", type="concept", labels=["خبز", "Bread Baking"])
    handler.language_rules["ar"]["lexicon"]["الخبز"] = "bread_baking"
    handler.language_rules["ar"]["lexicon"]["خبز"] = "bread_baking"
    
    # Heat capability/requirement
    handler.graph.add_node("heat", type="concept", labels=["حرارة", "Heat"])
    handler.graph.add_edge("solar_energy", "heat", relation="provides", type="fact", world="reality")
    handler.graph.add_edge("bread_baking", "heat", relation="requires", type="fact", world="reality")
    
    # Physical constraints for validation
    handler.graph.nodes["solar_energy"]["energy_provided"] = 1200.0
    handler.graph.nodes["bread_baking"]["mass"] = 0.5
    handler.graph.nodes["bread_baking"]["specific_heat"] = 2.0
    handler.graph.nodes["bread_baking"]["temp_change"] = 100.0 # Q_req = 100 J
    
    # Run process_query
    query = "ابتكر فكرة تربط بين الشمس والخبز"
    res = reasoner.process_query(query, language="ar")
    assert res["type"] == "innovation"
    assert res["result"] is True
    
    response = generator.generate(res, language="ar")
    assert "تم ابتكار فكرة جديدة تربط [طاقة شمسية] بـ [خبز] عبر المفهوم المشترك [حرارة]" in response
    assert "1200.0" in response
