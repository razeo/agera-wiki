#!/usr/bin/env python3
"""
Wiki Graph - Knowledge graph operations for LLM Wiki v2
Provides entity lookup, relation traversal, and graph queries.
"""
import json
import os
from pathlib import Path
from collections import defaultdict

WIKI_ROOT = Path(os.path.expanduser("~/wiki"))
GRAPH_DIR = WIKI_ROOT / "graph"


def load_entities():
    """Load entities from graph/entities.json."""
    fpath = GRAPH_DIR / "entities.json"
    if not fpath.exists():
        return {}
    with open(fpath, encoding="utf-8") as f:
        return json.load(f)


def load_relations():
    """Load relations from graph/relations.json."""
    fpath = GRAPH_DIR / "relations.json"
    if not fpath.exists():
        return []
    with open(fpath, encoding="utf-8") as f:
        return json.load(f)


def get_entity(name):
    """Get entity by name."""
    entities = load_entities()
    return entities.get(name)


def get_relations(name, direction="outbound"):
    """Get all relations for an entity."""
    relations = load_relations()
    return [r for r in relations if r["source"] == name and r["direction"] == direction]


def get_connected(name, depth=1):
    """
    Get all entities connected to 'name' within 'depth' hops.
    Returns dict of {entity_name: {distance, relation_type}}.
    """
    relations = load_relations()
    entities = load_entities()
    
    # Build adjacency
    adj = defaultdict(list)
    for r in relations:
        adj[r["source"]].append((r["target"], r["type"]))
    
    visited = {}
    queue = [(name, 0, "self")]
    
    while queue:
        current, dist, rel_type = queue.pop(0)
        if current in visited:
            continue
        if dist > depth:
            continue
        visited[current] = {"distance": dist, "relation": rel_type}
        
        if current in adj:
            for target, rtype in adj[current]:
                if target not in visited:
                    queue.append((target, dist + 1, rtype))
    
    # Remove self
    visited.pop(name, None)
    return visited


def find_paths(source, target, max_depth=3):
    """Find all paths between two entities."""
    relations = load_relations()
    
    adj = defaultdict(list)
    for r in relations:
        adj[r["source"]].append((r["target"], r["type"]))
    
    paths = []
    
    def dfs(current, path, visited):
        if current == target:
            paths.append(path[:])
            return
        if len(path) >= max_depth:
            return
        for next_node, rtype in adj.get(current, []):
            if next_node not in visited:
                visited.add(next_node)
                path.append((next_node, rtype))
                dfs(next_node, path, visited)
                path.pop()
                visited.remove(next_node)
    
    dfs(source, [(source, "self")], {source})
    return paths


def graph_stats():
    """Return graph statistics."""
    entities = load_entities()
    relations = load_relations()
    
    # Only outbound for stats
    outbound = [r for r in relations if r["direction"] == "outbound"]
    
    type_count = defaultdict(int)
    for e in entities.values():
        type_count[e["type"]] += 1
    
    rel_count = defaultdict(int)
    for r in outbound:
        rel_count[r["type"]] += 1
    
    # Find most connected entities
    conn_count = defaultdict(int)
    for r in outbound:
        conn_count[r["source"]] += 1
        conn_count[r["target"]] += 1
    
    top_connected = sorted(conn_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Orphan check (no inbound)
    inbound_targets = set(r["target"] for r in outbound)
    orphans = [name for name in entities if name not in inbound_targets]
    
    return {
        "total_entities": len(entities),
        "total_relations": len(outbound),
        "entity_types": dict(type_count),
        "relation_types": dict(rel_count),
        "top_connected": top_connected,
        "orphans": orphans,
    }


def rebuild_graph():
    """Rebuild graph from wiki pages. Use after adding new pages."""
    import re
    import yaml
    
    entities = {}
    relations = []
    
    for folder in ("concepts", "entities"):
        fpath = WIKI_ROOT / folder
        if not fpath.exists():
            continue
        for f in fpath.glob("*.md"):
            rel = str(f.relative_to(WIKI_ROOT))
            content = f.read_text(encoding="utf-8")
            
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                continue
            try:
                fm = yaml.safe_load(match.group(1))
            except:
                continue
            
            name = f.stem
            entities[name] = {
                "name": name,
                "title": fm.get("title", name),
                "type": fm.get("entity_type", "concept"),
                "file": rel,
                "tags": fm.get("tags", []),
                "confidence": fm.get("confidence", 0.7),
            }
            
            wikilinks = re.findall(r'\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]', content)
            for link in wikilinks:
                relations.append({
                    "source": name,
                    "target": link,
                    "type": "vezan_za",
                    "direction": "outbound",
                })
    
    # Add reverse
    reverse = [
        {"source": r["target"], "target": r["source"], "type": r["type"], "direction": "inbound"}
        for r in relations
    ]
    
    GRAPH_DIR.mkdir(exist_ok=True)
    with open(GRAPH_DIR / "entities.json", "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)
    with open(GRAPH_DIR / "relations.json", "w", encoding="utf-8") as f:
        json.dump(relations + reverse, f, indent=2, ensure_ascii=False)
    
    return len(entities), len(relations)


if __name__ == "__main__":
    import sys
    
    if "--rebuild" in sys.argv:
        n_ent, n_rel = rebuild_graph()
        print(f"Graph rebuilt: {n_ent} entities, {n_rel} relations")
    elif "--stats" in sys.argv:
        stats = graph_stats()
        print(f"Entities: {stats['total_entities']}")
        print(f"Relations: {stats['total_relations']}")
        print(f"\nEntity types:")
        for t, c in sorted(stats['entity_types'].items()):
            print(f"  {t}: {c}")
        print(f"\nRelation types:")
        for t, c in sorted(stats['relation_types'].items()):
            print(f"  {t}: {c}")
        print(f"\nMost connected:")
        for name, count in stats['top_connected']:
            print(f"  {name}: {count} connections")
        print(f"\nOrphan entities (no inbound): {len(stats['orphans'])}")
        for o in stats['orphans']:
            print(f"  {o}")
    elif "--connected" in sys.argv:
        idx = sys.argv.index("--connected")
        if idx + 1 < len(sys.argv):
            name = sys.argv[idx + 1]
            connected = get_connected(name, depth=2)
            print(f"Connected to '{name}':")
            for ent, info in sorted(connected.items(), key=lambda x: x[1]["distance"]):
                print(f"  [{info['distance']}] {ent} ({info['relation']})")
        else:
            print("Usage: graph.py --connected <entity_name>")
    else:
        print("Usage: graph.py [--rebuild|--stats|--connected <name>]")
