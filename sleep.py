import argparse
from src.graph_handler import GraphHandler
from src.maintenance.sleep_cycle import CognitiveSleepCycle

def main():
    parser = argparse.ArgumentParser(description="Cognitive Sleep Cycle for TheOne")
    parser.add_argument("--depth", type=int, default=2, help="Depth for sleep operations")
    parser.add_argument("--cleanup", action="store_true", help="Perform node cleanup")
    args = parser.parse_args()

    handler = GraphHandler()
    handler.load_databases(
        "data/animals_ontology_small.json",
        "data/animals_facts.json",
        "data/animals_language_rules.json"
    )

    sleep_cycle = CognitiveSleepCycle(handler)
    stats = sleep_cycle.run_sleep_cycle()
    print("💤 Cognitive Sleep Cycle Completed successfully!")
    print(f"📊 Stats: {stats}")

if __name__ == "__main__":
    main()
