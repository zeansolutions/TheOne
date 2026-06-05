import os
import json

class ResponseBuilder:
    def __init__(self, reasoner):
        self.reasoner = reasoner

    @property
    def handler(self):
        return self.reasoner.handler

    def format_trace(self, trace_steps):
        """Formats a list of trace steps into a readable block."""
        if not trace_steps:
            return ""
        return "\n".join(trace_steps)

    def build_confidence_chain(self, steps, base_confidence=1.0):
        """Constructs a detailed representation of the confidence degradation along a path."""
        chain = []
        current_conf = base_confidence
        for step in steps:
            decay = step.get("decay", 1.0)
            current_conf *= decay
            chain.append({
                "step": step.get("description", ""),
                "decay": decay,
                "resulting_confidence": current_conf
            })
        return {
            "final_confidence": current_conf,
            "chain": chain
        }

    def build_answer(self, result_dict, language="ar"):
        """Ensures the reasoning result dictionary is clean and standardized."""
        if not result_dict:
            return {
                "type": "unknown",
                "result": False,
                "trace": [],
                "confidence": 0.0
            }
        
        # Standardize trace format
        if "trace" in result_dict and isinstance(result_dict["trace"], list):
            # Clean empty steps
            result_dict["trace"] = [t for t in result_dict["trace"] if t]
            
        return result_dict
