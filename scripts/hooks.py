#!/usr/bin/env python3
"""
Wiki Hooks - Session hooks for LLM Wiki v2 lifecycle.
Call these from AI agent or cron jobs.
"""
import os
import sys
import json
from pathlib import Path
from datetime import date

WIKI_ROOT = Path(os.path.expanduser("~/wiki"))
sys.path.insert(0, str(WIKI_ROOT / "scripts"))


def on_query(entity_name):
    """
    Hook: When a wiki page is queried/accessed.
    Updates access_count, last_accessed, bumps confidence.
    """
    from decay import reinforce_page
    return reinforce_page(entity_name)


def on_session_end(session_summary=None):
    """
    Hook: End of AI session.
    Compress session into observations, update access tracking.
    """
    from search import load_pages
    from decay import reinforce_page
    
    if not session_summary:
        return {"status": "no_summary"}
    
    # Simple: just log that session happened
    log_path = WIKI_ROOT / "scripts" / ".session_log.json"
    log = []
    if log_path.exists():
        try:
            log = json.loads(log_path.read_text())
        except:
            log = []
    
    log.append({
        "date": date.today().isoformat(),
        "summary_length": len(session_summary),
    })
    
    # Keep only last 100 entries
    log = log[-100:]
    log_path.write_text(json.dumps(log, indent=2))
    
    return {"status": "ok", "sessions_logged": len(log)}


def on_new_fact(entity_name, fact_text, source="session"):
    """
    Hook: When a new fact is discovered about an entity.
    Updates confidence if fact confirms existing knowledge.
    """
    from decay import reinforce_page
    
    # Reinforce the entity
    reinforce_page(entity_name)
    
    # Log the fact
    facts_log = WIKI_ROOT / "scripts" / ".facts_log.json"
    log = []
    if facts_log.exists():
        try:
            log = json.loads(facts_log.read_text())
        except:
            log = []
    
    log.append({
        "date": date.today().isoformat(),
        "entity": entity_name,
        "fact": fact_text[:200],
        "source": source,
    })
    
    log = log[-500:]
    facts_log.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    
    return {"status": "ok"}


def on_contradiction(entity_name, old_claim, new_claim):
    """
    Hook: When new information contradicts existing knowledge.
    Decreases confidence, logs for review.
    """
    import re
    import yaml
    
    today = date.today().isoformat()
    
    for folder in ("concepts", "entities"):
        fpath = WIKI_ROOT / folder / f"{entity_name}.md"
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            
            # Decrease confidence
            match = re.search(r'confidence: (\d+\.?\d*)', content)
            if match:
                old_conf = float(match.group(1))
                new_conf = max(0.0, round(old_conf - 0.2, 2))
                content = content.replace(
                    f"confidence: {old_conf}",
                    f"confidence: {new_conf}", 1
                )
                content = re.sub(r'last_confirmed: \S+', f'last_confirmed: {today}', content)
                fpath.write_text(content, encoding="utf-8")
            
            break
    
    # Log contradiction
    contra_log = WIKI_ROOT / "scripts" / ".contradictions.json"
    log = []
    if contra_log.exists():
        try:
            log = json.loads(contra_log.read_text())
        except:
            log = []
    
    log.append({
        "date": today,
        "entity": entity_name,
        "old_claim": old_claim[:200],
        "new_claim": new_claim[:200],
        "resolved": False,
    })
    
    log = log[-200:]
    contra_log.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    
    return {"status": "ok", "confidence_decreased": True}


def weekly_maintenance():
    """
    Hook: Run weekly maintenance.
    - Confidence decay
    - Graph rebuild
    - Lint check
    """
    from decay import apply_decay
    from graph import rebuild_graph
    from lint import run_all_checks
    
    print("=== Weekly Wiki Maintenance ===\n")
    
    # 1. Decay
    print("1. Confidence decay...")
    decay_results = apply_decay(dry_run=False)
    print(f"   Decayed: {len(decay_results['decayed'])}, Archived: {len(decay_results['archived'])}")
    
    # 2. Rebuild graph
    print("2. Rebuild graph...")
    n_ent, n_rel = rebuild_graph()
    print(f"   Graph: {n_ent} entities, {n_rel} relations")
    
    # 3. Lint
    print("3. Lint check...")
    issues, total, _ = run_all_checks(fix=False)
    high = [i for i in issues if i[0] in ("MISSING_FRONTMATTER", "BROKEN_LINK", "MISSING_FIELD")]
    print(f"   Total issues: {len(issues)} (high: {len(high)})")
    
    # 4. Clear old session/facts logs (keep last 30 days)
    print("4. Cleanup old logs...")
    for log_name in (".session_log.json", ".facts_log.json", ".contradictions.json"):
        log_path = WIKI_ROOT / "scripts" / log_name
        if log_path.exists():
            try:
                log = json.loads(log_path.read_text())
                cutoff = date.today().isoformat()[:7]  # current month
                log = [e for e in log if e.get("date", "").startswith(cutoff)]
                log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False))
            except:
                pass
    
    print("\nDone!")
    return {
        "decayed": len(decay_results['decayed']),
        "archived": len(decay_results['archived']),
        "entities": n_ent,
        "issues": len(issues),
    }


if __name__ == "__main__":
    if "--weekly" in sys.argv:
        weekly_maintenance()
    elif "--query" in sys.argv:
        # usage: hooks.py --query entity_name
        entity = sys.argv[2] if len(sys.argv) > 2 else ""
        print(on_query(entity))
    elif "--new-fact" in sys.argv:
        # usage: hooks.py --new-fact entity_name "fact text"
        entity = sys.argv[2] if len(sys.argv) > 2 else ""
        fact = sys.argv[3] if len(sys.argv) > 3 else ""
        print(on_new_fact(entity, fact))
    elif "--contradiction" in sys.argv:
        # usage: hooks.py --contradiction entity_name "old" "new"
        entity = sys.argv[2] if len(sys.argv) > 2 else ""
        old_claim = sys.argv[3] if len(sys.argv) > 3 else ""
        new_claim = sys.argv[4] if len(sys.argv) > 4 else ""
        print(on_contradiction(entity, old_claim, new_claim))
    elif "--session-end" in sys.argv:
        # usage: hooks.py --session-end "summary"
        summary = sys.argv[2] if len(sys.argv) > 2 else ""
        print(on_session_end(summary))
    else:
        print("Usage: hooks.py --weekly")
        print("       hooks.py --query entity_name")
        print("       hooks.py --new-fact entity_name 'fact text'")
        print("       hooks.py --contradiction entity_name 'old' 'new'")
        print("       hooks.py --session-end 'summary'")
