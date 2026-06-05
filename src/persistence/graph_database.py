import os
import json
import sqlite3
import networkx as nx
from typing import Dict, List, Any, Optional

class SqliteBackedDict(dict):
    """A dictionary wrapper that syncs set/delete operations to SQLite metadata table."""
    def __init__(self, conn, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._conn = conn

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if getattr(self, "_loading", False):
            return
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO metadata (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, json.dumps(value, ensure_ascii=False)))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error setting metadata '{key}': {e}")

    def __delitem__(self, key):
        super().__delitem__(key)
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM metadata WHERE key=?", (key,))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error deleting metadata '{key}': {e}")


class GraphDatabaseSQLite(nx.MultiDiGraph):
    """
    An SQLite-backed NetworkX MultiDiGraph.
    All modifications to nodes, edges, and graph attributes are synchronized
    with an SQLite database file to implement memory-efficient persistence.
    """
    def __init__(self, db_path: str, *args, **kwargs):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._loading = True
        self._init_db()
        
        super().__init__(*args, **kwargs)
        
        # Override self.graph with the SQLite-backed dictionary
        initial_attrs = dict(self.graph)
        self.graph = SqliteBackedDict(self._conn)
        self.graph._loading = True
        for k, v in initial_attrs.items():
            self.graph[k] = v
        self.graph._loading = False

        self._load_from_db()
        self._loading = False

    def _init_db(self):
        try:
            cursor = self._conn.cursor()
            # 1. concepts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concepts (
                    id TEXT PRIMARY KEY,
                    labels TEXT,
                    category TEXT,
                    confidence REAL DEFAULT 1.0
                )
            """)
            # 2. edges table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    target TEXT,
                    key INTEGER,
                    relation TEXT,
                    type TEXT,
                    world TEXT,
                    confidence REAL,
                    reason TEXT,
                    timestamp TEXT,
                    source_type TEXT,
                    status TEXT,
                    update_history TEXT,
                    modality TEXT,
                    causal_purpose TEXT,
                    metadata TEXT,
                    FOREIGN KEY(source) REFERENCES concepts(id),
                    FOREIGN KEY(target) REFERENCES concepts(id),
                    UNIQUE(source, target, key)
                )
            """)
            # 3. metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite initialization error: {e}")

    def _load_from_db(self):
        self._loading = True
        try:
            cursor = self._conn.cursor()
            # Load concepts
            cursor.execute("SELECT id, labels, category, confidence FROM concepts")
            for row in cursor.fetchall():
                c_id, labels_json, category, confidence = row
                try:
                    labels = json.loads(labels_json)
                except Exception:
                    labels = [c_id]
                super().add_node(c_id, labels=labels, category=category, type="concept", confidence=confidence)

            # Load edges
            cursor.execute("""
                SELECT source, target, key, relation, type, world, confidence, reason, timestamp,
                       source_type, status, update_history, modality, causal_purpose, metadata
                FROM edges
            """)
            for row in cursor.fetchall():
                (source, target, key, relation, etype, world, confidence, reason, timestamp,
                 source_type, status, update_history_json, modality, causal_purpose, metadata_json) = row
                try:
                    update_history = json.loads(update_history_json) if update_history_json else []
                except Exception:
                    update_history = []
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except Exception:
                    metadata = {}

                super().add_edge(
                    source, target, key=key,
                    relation=relation,
                    type=etype,
                    world=world,
                    confidence=confidence,
                    reason=reason,
                    timestamp=timestamp,
                    source=source_type,
                    status=status,
                    update_history=update_history,
                    modality=modality,
                    causal_purpose=causal_purpose,
                    metadata=metadata
                )

            # Load metadata
            self.graph._loading = True
            cursor.execute("SELECT key, value FROM metadata")
            for row in cursor.fetchall():
                k, v_json = row
                try:
                    val = json.loads(v_json)
                except Exception:
                    val = v_json
                self.graph[k] = val
            self.graph._loading = False

        except sqlite3.Error as e:
            print(f"SQLite error loading graph: {e}")
        finally:
            self._loading = False

    def add_node(self, node_for_adding, **attr):
        super().add_node(node_for_adding, **attr)
        if getattr(self, "_loading", False):
            return
        try:
            labels = attr.get("labels", [node_for_adding])
            category = attr.get("category", "concept")
            confidence = attr.get("confidence", 1.0)
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO concepts (id, labels, category, confidence)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    labels=excluded.labels,
                    category=excluded.category,
                    confidence=excluded.confidence
            """, (node_for_adding, json.dumps(labels, ensure_ascii=False), category, confidence))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error adding concept '{node_for_adding}': {e}")

    def remove_node(self, n):
        super().remove_node(n)
        if getattr(self, "_loading", False):
            return
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM concepts WHERE id=?", (n,))
            cursor.execute("DELETE FROM edges WHERE source=? OR target=?", (n, n))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error removing concept '{n}': {e}")

    def add_edge(self, u_of_edge, v_of_edge, key=None, **attr):
        # Ensure concepts exist in SQLite
        if not self.has_node(u_of_edge):
            self.add_node(u_of_edge, labels=[u_of_edge], category="concept")
        if not self.has_node(v_of_edge):
            self.add_node(v_of_edge, labels=[v_of_edge], category="concept")

        actual_key = super().add_edge(u_of_edge, v_of_edge, key=key, **attr)
        if getattr(self, "_loading", False):
            return actual_key

        try:
            relation = attr.get("relation", "")
            etype = attr.get("type", "fact")
            world = attr.get("world", "reality")
            confidence = attr.get("confidence", 1.0)
            reason = attr.get("reason", None)
            timestamp = attr.get("timestamp", "")
            source_type = attr.get("source", "automated")
            status = attr.get("status", "active")
            update_history = attr.get("update_history", [])
            modality = attr.get("modality", None)
            causal_purpose = attr.get("causal_purpose", None)
            metadata = attr.get("metadata", {})

            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO edges (source, target, key, relation, type, world, confidence, reason, timestamp,
                                   source_type, status, update_history, modality, causal_purpose, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source, target, key) DO UPDATE SET
                    relation=excluded.relation,
                    type=excluded.type,
                    world=excluded.world,
                    confidence=excluded.confidence,
                    reason=excluded.reason,
                    timestamp=excluded.timestamp,
                    source_type=excluded.source_type,
                    status=excluded.status,
                    update_history=excluded.update_history,
                    modality=excluded.modality,
                    causal_purpose=excluded.causal_purpose,
                    metadata=excluded.metadata
            """, (
                u_of_edge, v_of_edge, actual_key, relation, etype, world, confidence, reason, timestamp,
                source_type, status, json.dumps(update_history, ensure_ascii=False), modality, causal_purpose,
                json.dumps(metadata, ensure_ascii=False)
            ))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error adding edge {u_of_edge} -> {v_of_edge} (key {actual_key}): {e}")
        return actual_key

    def remove_edge(self, u, v, key=None):
        keys_to_remove = []
        if key is not None:
            keys_to_remove = [key]
        else:
            if self.has_edge(u, v):
                keys_to_remove = list(self[u][v].keys())

        super().remove_edge(u, v, key=key)
        if getattr(self, "_loading", False):
            return

        try:
            cursor = self._conn.cursor()
            for k in keys_to_remove:
                cursor.execute("DELETE FROM edges WHERE source=? AND target=? AND key=?", (u, v, k))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error removing edge {u} -> {v} (key {key}): {e}")

    def clear(self):
        super().clear()
        if getattr(self, "_loading", False):
            return
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM concepts")
            cursor.execute("DELETE FROM edges")
            cursor.execute("DELETE FROM metadata")
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error clearing graph: {e}")

    def __deepcopy__(self, memo):
        # Create an in-memory clone of the GraphDatabaseSQLite to act as an isolated sandbox.
        cls = self.__class__
        clone = cls(":memory:")
        
        clone._loading = True
        
        # Copy concepts
        cursor = self._conn.cursor()
        cursor.execute("SELECT id, labels, category, confidence FROM concepts")
        clone_cursor = clone._conn.cursor()
        for row in cursor.fetchall():
            c_id, labels_json, category, confidence = row
            clone_cursor.execute("INSERT INTO concepts (id, labels, category, confidence) VALUES (?, ?, ?, ?)",
                                 (c_id, labels_json, category, confidence))
            
        # Copy edges
        cursor.execute("""
            SELECT source, target, key, relation, type, world, confidence, reason, timestamp,
                   source_type, status, update_history, modality, causal_purpose, metadata
            FROM edges
        """)
        for row in cursor.fetchall():
            clone_cursor.execute("""
                INSERT INTO edges (source, target, key, relation, type, world, confidence, reason, timestamp,
                                   source_type, status, update_history, modality, causal_purpose, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)
            
        # Copy metadata
        cursor.execute("SELECT key, value FROM metadata")
        for row in cursor.fetchall():
            clone_cursor.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", row)
            
        clone._conn.commit()
        
        # Load the in-memory structures of the clone
        clone._load_from_db()
        clone._loading = False
        
        memo[id(self)] = clone
        return clone

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
