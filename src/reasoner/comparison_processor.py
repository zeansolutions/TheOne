import os
import json

class ComparisonProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "comparison.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def get_scale_value(self, entity, property_name):
        """
        Retrieves the scale value of an entity for a comparative property.
        """
        props = self.db.get("comparative_properties", {})
        prop_def = props.get(property_name, {})
        scale = prop_def.get("scale", [])
        
        for item in scale:
            if item["entity"] == entity:
                return item["value"]
        return None
        
    def compare_entities(self, entity_a, entity_b, property_name):
        """
        Compares two entities on a property scale.
        Returns:
            1 if entity_a > entity_b
            -1 if entity_a < entity_b
            0 if equal or unknown
        """
        val_a = self.get_scale_value(entity_a, property_name)
        val_b = self.get_scale_value(entity_b, property_name)
        
        if val_a is None or val_b is None:
            # Fallback to transitive chain check if they can be ordered indirectly
            return 0
            
        if val_a > val_b:
            return 1
        elif val_a < val_b:
            return -1
        else:
            return 0
            
    def get_comparison_rule_trace(self, entity_a, entity_b, property_name):
        """
        Generates a comparative trace.
        """
        val_a = self.get_scale_value(entity_a, property_name)
        val_b = self.get_scale_value(entity_b, property_name)
        
        if val_a is not None and val_b is not None:
            rel = "أكبر من" if val_a > val_b else ("أصغر من" if val_a < val_b else "يساوي")
            return f"مقارنة الخاصية [{property_name}]: قيمة {entity_a} ({val_a}) {rel} قيمة {entity_b} ({val_b})"
        return "لا تتوفر قيم كافية على مقياس المقارنة للمقارنة المباشرة"
