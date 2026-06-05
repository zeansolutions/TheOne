import os
import pytest
from src.graph_handler import GraphHandler
from src.tools.data_importer import DataImporter
from src.tools.data_validator import DataValidator

def test_on_demand_enrichment():
    gh = GraphHandler()
    # Mock ontology json path to ensure a local db is initialized
    gh.load_databases(
        "tests/mock_data/animals_ontology_small.json",
        "tests/mock_data/animals_facts.json",
        "data/language_rules.json"
    )
    
    # Try importing a concept
    importer = DataImporter(gh)
    trace = []
    # Fetch "عقاب" (Eagle in Arabic) or "eagle"
    # Should resolve successfully if online, or exit gracefully if offline
    success = importer.enrich_concept("عقاب", "ar", trace=trace)
    
    # Check that it either successfully populated or logged offline mode
    assert len(trace) > 0
    # The first message should describe connecting
    assert any("Connecting to ConceptNet" in t for t in trace)

def test_data_validation_and_deduplication():
    gh = GraphHandler()
    gh.load_databases(
        "tests/mock_data/animals_ontology_small.json",
        "tests/mock_data/animals_facts.json",
        "data/language_rules.json"
    )
    
    # Inject similar concepts to trigger deduplication
    # "الأسد" (already exists) and "الاسد" (duplicate without hamza)
    gh.graph.add_node("الأسد", labels=["الأسد"], category="animal")
    gh.graph.add_node("الاسد", labels=["الاسد"], category="animal")
    gh.graph.add_edge("الاسد", "الغابة", relation="lives_in", type="fact")
    
    validator = DataValidator(gh)
    report = validator.run_validation(similarity_threshold=0.85)
    
    # Verify duplicates were merged
    assert report["duplicates_merged"] > 0
    # "الاسد" should have been removed and merged into "الأسد"
    assert not gh.graph.has_node("الاسد")
    assert gh.graph.has_node("الأسد")
    
    # Verify edges were transferred
    assert gh.graph.has_edge("الأسد", "الغابة")

def test_contradiction_detection():
    gh = GraphHandler()
    gh.load_databases(
        "tests/mock_data/animals_ontology_small.json",
        "tests/mock_data/animals_facts.json",
        "data/language_rules.json"
    )
    
    # Inject contradiction: u is_a v AND u is_not_a v
    gh.graph.add_node("سمكة", labels=["سمكة"], category="animal")
    gh.graph.add_node("طائر", labels=["طائر"], category="animal")
    gh.graph.add_edge("سمكة", "طائر", relation="is_a", type="fact")
    gh.graph.add_edge("سمكة", "طائر", relation="is_not_a", type="fact")
    
    validator = DataValidator(gh)
    report = validator.run_validation()
    
    # Verify contradiction detected
    assert report["contradictions_detected"] > 0
    assert any("Subject 'سمكة' both asserted and negated relation with 'طائر'" in d for d in report["details"])
