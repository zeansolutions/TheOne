import os
import sys
import json
import time
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to sys.path so we can import src
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.manager.multilingual_persona_engine import MultilingualPersonaEngine
from src.maintenance.sleep_cycle import CognitiveSleepCycle
from src.reasoner.curiosity_engine import CuriosityEngine
from src.conflict_resolver import ConflictResolver

# Initialize global engine instances
handler = GraphHandler()
ontology_path = os.path.join(project_root, "data/ontology.json")
facts_path = os.path.join(project_root, "data/facts.json")
language_rules_path = os.path.join(project_root, "data/language_rules.json")

try:
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    print("🧠 TheOne Engine databases loaded successfully.")
except Exception as e:
    print(f"❌ Error loading TheOne databases: {e}")
    sys.exit(1)

reasoner = SimpleReasoner(handler)
persona_engine = MultilingualPersonaEngine(handler)
conflict_resolver = ConflictResolver(handler)

active_lang = "en"

procedural_steps_path = os.path.join(project_root, "data/procedural_steps.json")


def load_procedural_steps():
    if os.path.exists(procedural_steps_path):
        try:
            with open(procedural_steps_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading procedural steps: {e}")
    return {}

def save_procedural_steps(data):
    try:
        os.makedirs(os.path.dirname(procedural_steps_path), exist_ok=True)
        with open(procedural_steps_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving procedural steps: {e}")
        return False



class TheOneAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence standard HTTP request logs to keep terminal clean
        pass

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()

        response_data = {"error": "Endpoint not found"}

        try:
            if path == "/api/status":
                concepts = [node for node, data in handler.graph.nodes(data=True) if data.get("type") == "concept"]
                facts_count = len([1 for u, v, data in handler.graph.edges(data=True) if data.get("type") == "fact"])
                inferred_count = len([1 for u, v, data in handler.graph.edges(data=True) if data.get("type") == "inferred"])
                
                # Extract all unique worlds
                worlds = set()
                for u, v, data in handler.graph.edges(data=True):
                    if "world" in data:
                        worlds.add(data["world"])
                
                # Load relations metadata
                metadata_path = os.path.join(project_root, "data/relations_metadata.json")
                relations = []
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            meta_data = json.load(f)
                            relations = [r.get("id") for r in meta_data.get("relations", []) if r.get("id")]
                    except Exception:
                        pass
                
                # Fallback to basic relation types if empty
                if not relations:
                    relations = ['is_a', 'part_of', 'lives_in', 'has_property', 'eats', 'rises_from', 'causes', 'resembles', 'requires']
                else:
                    # Make sure basic relations are always present
                    basic = ['is_a', 'part_of', 'lives_in', 'has_property', 'eats', 'rises_from', 'causes', 'resembles', 'requires']
                    for r in basic:
                        if r not in relations:
                            relations.append(r)
                
                response_data = {
                    "status": "online",
                    "active_world": handler.active_world,
                    "active_language": active_lang,
                    "concepts_count": len(concepts),
                    "facts_count": facts_count,
                    "inferred_count": inferred_count,
                    "worlds": list(worlds) if worlds else ["reality"],
                    "personas": [p.get("id") for p in persona_engine.personas_db] if (hasattr(persona_engine, "personas_db") and persona_engine.personas_db) else ["sage_friend", "scientist", "witty_mentor"],
                    "relations": relations
                }
                
            elif path == "/api/graph":
                nodes = []
                for node, data in handler.graph.nodes(data=True):
                    nodes.append({
                        "id": node,
                        "label": data.get("labels", [node])[0],
                        "labels": data.get("labels", [node]),
                        "category": data.get("category", "unknown"),
                        "type": data.get("type", "concept")
                    })
                
                edges = []
                for u, v, data in handler.graph.edges(data=True):
                    edges.append({
                        "source": u,
                        "target": v,
                        "relation": data.get("relation", "linked"),
                        "world": data.get("world", "reality"),
                        "confidence": data.get("confidence", 1.0),
                        "type": data.get("type", "relation")
                    })
                
                response_data = {
                    "nodes": nodes,
                    "edges": edges
                }
                
            elif path == "/api/curiosity":
                query_params = parse_qs(parsed_path.query)
                limit = int(query_params.get("limit", [5])[0])
                lang = query_params.get("lang", [active_lang])[0]
                
                curiosity = CuriosityEngine(handler)
                questions = curiosity.generate_questions(limit=limit, lang=lang)
                response_data = {
                    "questions": questions or []
                }
                
            elif path == "/api/worlds":
                worlds = set()
                for u, v, data in handler.graph.edges(data=True):
                    if "world" in data:
                        worlds.add(data["world"])
                response_data = {
                    "worlds": list(worlds) if worlds else ["reality"]
                }
                
            elif path == "/api/procedural/get":
                response_data = load_procedural_steps()
                
        except Exception as e:
            response_data = {"error": str(e)}

        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        global active_lang
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = {}
        if post_data:
            try:
                body = json.loads(post_data.decode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON body: {str(e)}"}, ensure_ascii=False).encode('utf-8'))
                return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()

        response_data = {"error": "Endpoint not found"}

        try:
            if path == "/api/query":
                query = body.get("query", "").strip()
                lang_pref = body.get("lang", active_lang)
                persona_pref = body.get("persona") # Forced persona ID
                
                if query:
                    # 1. Detect language
                    detected_lang = persona_engine.language_engine.detect_language(query)
                    selected_lang = persona_engine.language_engine.select_language(detected_lang, user_preference=lang_pref)
                    
                    # 2. Run logical reasoning
                    start_time = time.perf_counter()
                    res = reasoner.process_query(query, interactive=True, language=selected_lang)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                    
                    # 3. Multilingual Persona response generation
                    history = reasoner.conversation_manager.get_history()
                    engine_res = persona_engine.process_response(
                        query, res, conversation_history=history, 
                        user_preference=lang_pref, force_persona_id=persona_pref
                    )
                    
                    # Format reasoning trace nicely
                    formatted_trace = persona_engine.expression_renderer.format_trace(res.get("trace", []), selected_lang)
                    
                    response_data = {
                        "response": engine_res["response"],
                        "language": engine_res["language"],
                        "persona": engine_res["persona"],
                        "confidence": res.get("confidence", 1.0),
                        "elapsed_ms": elapsed_ms,
                        "trace": res.get("trace", []),
                        "formatted_trace": formatted_trace,
                        "success": True
                    }
                else:
                    response_data = {"error": "Empty query"}
                    
            elif path == "/api/teach":
                subj = body.get("subject")
                obj = body.get("object")
                relation = body.get("relation")
                world = body.get("world", "reality")
                confidence = float(body.get("confidence", 1.0))
                modality = body.get("modality", None)
                lang = body.get("lang", active_lang)
                
                # Canonicalize subject and object to canonical indefinite stems
                subj = handler.canonicalize_concept(subj, lang)
                obj = handler.canonicalize_concept(obj, lang)
                
                # Check for dynamic concepts adding if they do not exist
                if subj and not handler.graph.has_node(subj):
                    handler.graph.add_node(subj, labels=[subj], category="user_defined", type="concept")
                if obj and not handler.graph.has_node(obj):
                    handler.graph.add_node(obj, labels=[obj], category="user_defined", type="concept")
                
                if subj and obj and relation:
                    # Run add_or_update_fact (handles confidence based thresholds and contradiction checks)
                    # For GUI, we pass interactive=False by default to receive JSON response, OR we can handle user selection
                    res = handler.add_or_update_fact(
                        subj, obj, relation=relation, world=world,
                        confidence=confidence, interactive=False, modality=modality, language=lang
                    )
                    
                    # Persist changes
                    handler.save_databases(ontology_path, facts_path)
                    
                    # Re-run logical inferences so the graph stays updated
                    handler.infer_facts(handler.active_world)
                    
                    response_data = {
                        "success": True,
                        "status": res["status"],
                        "message": res["message"]
                    }
                else:
                    response_data = {"error": "Missing subject, object, or relation"}
                    
            elif path == "/api/resolve_conflict":
                subj = body.get("subject")
                obj = body.get("object")
                relation = body.get("relation")
                world = body.get("world", "reality")
                action = body.get("action") # "replace" | "merge" | "ignore"
                
                # Canonicalize subject and object to canonical indefinite stems
                subj = handler.canonicalize_concept(subj, active_lang)
                obj = handler.canonicalize_concept(obj, active_lang)
                
                # Locate existing conflict edge
                existing_edges = []
                for u, v, key, data in list(handler.graph.out_edges(subj, data=True, keys=True)):
                    if data.get("type") == "fact" and data.get("world") == world and data.get("relation") == relation:
                        existing_edges.append((u, v, key, data))
                
                message = "No conflict found"
                if existing_edges:
                    u, v, key, data = existing_edges[0]
                    if action == "replace":
                        handler.graph.remove_edge(u, v, key=key)
                        handler.graph.add_edge(
                            subj, obj, relation=relation, world=world,
                            confidence=1.0, type="fact", timestamp=datetime.datetime.now(datetime.UTC).isoformat() + "Z",
                            source="user_interactive", status="active", update_history=[]
                        )
                        message = f"Replaced Old fact with [{obj}]"
                    elif action == "merge":
                        handler.graph.add_edge(
                            subj, obj, relation=relation, world=world,
                            confidence=1.0, type="fact", timestamp=datetime.datetime.now(datetime.UTC).isoformat() + "Z",
                            source="user_interactive", status="active", update_history=[]
                        )
                        message = f"Merged facts. Both are now active."
                    elif action == "ignore":
                        message = "Ignored new fact, retained old fact."
                        
                    handler.save_databases(ontology_path, facts_path)
                    handler.infer_facts(handler.active_world)
                    response_data = {"success": True, "message": message}
                else:
                    response_data = {"error": "Conflict not resolved"}

            elif path == "/api/sleep":
                depth = int(body.get("depth", 2))
                cleanup = bool(body.get("cleanup", True))
                
                sleep_cycle = CognitiveSleepCycle(handler)
                stats = sleep_cycle.run_sleep_cycle()
                
                handler.save_databases(ontology_path, facts_path)
                
                response_data = {
                    "success": True,
                    "message": "💤 Cognitive Sleep Cycle Completed successfully!",
                    "stats": stats
                }
                
            elif path == "/api/set_language":
                lang = body.get("lang", "en")
                active_lang = lang
                response_data = {
                    "success": True,
                    "active_language": active_lang
                }
                
            elif path == "/api/set_world":
                world = body.get("world", "reality")
                handler.set_active_world(world)
                
                # Re-run inferences for this world
                handler.infer_facts(world)
                
                response_data = {
                    "success": True,
                    "active_world": handler.active_world
                }

            elif path == "/api/delete_edge":
                source = body.get("source")
                target = body.get("target")
                relation = body.get("relation")
                world = body.get("world", "reality")
                
                to_remove = []
                for u, v, key, data in list(handler.graph.edges(keys=True, data=True)):
                    if u == source and v == target and data.get("relation") == relation:
                        if data.get("type") == "fact" and data.get("world") == world:
                            to_remove.append((u, v, key))
                            
                for u, v, key in to_remove:
                    handler.graph.remove_edge(u, v, key=key)
                    
                handler.save_databases(ontology_path, facts_path)
                handler.infer_facts(handler.active_world)
                response_data = {
                    "success": True,
                    "message": f"Successfully deleted relation [{source} -> {relation} -> {target}]"
                }

            elif path == "/api/add_relation":
                rel_id = body.get("id", "").strip().lower()
                rel_name = body.get("name", rel_id).strip()
                transitive = bool(body.get("transitive", False))
                symmetric = bool(body.get("symmetric", False))
                decay = float(body.get("decay", 0.0))
                
                if not rel_id:
                    response_data = {"error": "Relation ID is required"}
                else:
                    metadata_path = os.path.join(project_root, "data/relations_metadata.json")
                    meta_data = {"relations": []}
                    if os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                meta_data = json.load(f)
                        except Exception:
                            pass
                            
                    # Check if exists
                    exists = False
                    for r in meta_data.get("relations", []):
                        if r["id"] == rel_id:
                            r["name"] = rel_name
                            r["transitive"] = transitive
                            r["symmetric"] = symmetric
                            r["decay"] = decay
                            exists = True
                            break
                            
                    if not exists:
                        meta_data.setdefault("relations", []).append({
                            "id": rel_id,
                            "name": rel_name,
                            "transitive": transitive,
                            "symmetric": symmetric,
                            "decay": decay
                        })
                        
                    try:
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(meta_data, f, indent=2, ensure_ascii=False)
                    except Exception as e:
                        pass
                        
                    response_data = {
                        "success": True,
                        "message": f"Successfully registered relation '{rel_id}'."
                    }

            elif path == "/api/import_json":
                # Expects a JSON object matching LLM extraction schemas
                stats = handler.import_json_data(body)
                response_data = {
                    "success": True,
                    "message": "Knowledge import completed successfully!",
                    "stats": stats
                }

            elif path == "/api/clear_db":
                clear_type = body.get("type", "facts") # "facts" | "all" | "world"
                target_world = body.get("world")
                
                if clear_type == "facts":
                    # Remove all fact edges
                    to_remove = []
                    for u, v, key, data in list(handler.graph.edges(keys=True, data=True)):
                        if data.get("type") == "fact":
                            to_remove.append((u, v, key))
                    for u, v, key in to_remove:
                        handler.graph.remove_edge(u, v, key=key)
                    handler.facts = []
                    message = "Successfully cleared all facts database."
                elif clear_type == "world" and target_world:
                    # Remove fact edges for this world
                    to_remove = []
                    for u, v, key, data in list(handler.graph.edges(keys=True, data=True)):
                        if data.get("type") == "fact" and data.get("world") == target_world:
                            to_remove.append((u, v, key))
                    for u, v, key in to_remove:
                        handler.graph.remove_edge(u, v, key=key)
                    handler.facts = [f for f in handler.facts if f.get("world") != target_world]
                    message = f"Successfully deleted world '{target_world}'."
                elif clear_type == "all":
                    # Clear entire graph and facts database
                    handler.graph.clear()
                    handler.facts = []
                    message = "Successfully cleared entire databases (ontology, facts, rules)."
                else:
                    message = "Invalid clear parameters."

                handler.save_databases(ontology_path, facts_path)
                handler.infer_facts(handler.active_world)
                response_data = {
                    "success": True,
                    "message": message
                }

            elif path == "/api/procedural/add":
                procedure_name = body.get("procedure_name", "").strip()
                steps = body.get("steps", [])
                if not procedure_name:
                    response_data = {"error": "Procedure name is required"}
                elif not isinstance(steps, list):
                    response_data = {"error": "Steps must be a list of strings"}
                else:
                    data = load_procedural_steps()
                    data[procedure_name] = [str(s) for s in steps]
                    save_procedural_steps(data)
                    response_data = {"success": True, "message": "Procedure saved successfully"}

            elif path == "/api/procedural/delete":
                procedure_name = body.get("procedure_name", "").strip()
                if not procedure_name:
                    response_data = {"error": "Procedure name is required"}
                else:
                    data = load_procedural_steps()
                    if procedure_name in data:
                        del data[procedure_name]
                        save_procedural_steps(data)
                        response_data = {"success": True, "message": "Procedure deleted successfully"}
                    else:
                        response_data = {"error": "Procedure not found"}



        except Exception as e:
            response_data = {"error": str(e)}

        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TheOneAPIHandler)
    print(f"🚀 TheOne HTTP API Server running on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping API server...")
        httpd.server_close()

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
