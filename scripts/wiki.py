#!/usr/bin/env python3
"""
wiki - CLI for LLM Wiki v2
Usage: wiki <command> [args]

Commands:
  search <query>     Search wiki pages (confidence-weighted BM25)
  graph <name>       Show connected entities for given page
  graph --stats      Show graph statistics
  lint               Run quality checks
  lint --fix         Run checks and auto-fix confidence decay
  rebuild            Rebuild knowledge graph from pages
  top [N]            Show most accessed pages
  ingest             Process new files in raw/ folder
  decay              Apply confidence decay (--dry-run for preview)
  maintenance        Run weekly maintenance (decay + rebuild + lint)
"""
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.expanduser("~/wiki/scripts"))

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd == "search":
        if not args:
            print("Usage: wiki search <query>")
            sys.exit(1)
        import search as search_mod
        results = search_mod.search(" ".join(args))
        if not results:
            print(f"No results for: {' '.join(args)}")
            sys.exit(0)
        print(f"Search: '{' '.join(args)}' — {len(results)} results\n")
        for i, r in enumerate(results, 1):
            conf_bar = "#" * int(r["confidence"] * 10)
            print(f"{i}. {r['title']}")
            print(f"   score={r['score']:.3f}  confidence={r['confidence']} [{conf_bar}]  type={r['entity_type']}")
            print(f"   tags: {', '.join(r['tags'][:5])}")
            print(f"   file: {r['file']}")
            print()
        if results:
            search_mod.update_access(results[0]["name"])
    
    elif cmd == "graph":
        import graph as graph_mod
        if not args or args[0] == "--stats":
            stats = graph_mod.graph_stats()
            print(f"Entities: {stats['total_entities']}")
            print(f"Relations: {stats['total_relations']}")
            print(f"\nEntity types:")
            for t, c in sorted(stats['entity_types'].items()):
                print(f"  {t}: {c}")
            print(f"\nMost connected:")
            for name, count in stats['top_connected']:
                print(f"  {name}: {count} connections")
            print(f"\nOrphan entities: {len(stats['orphans'])}")
        else:
            name = args[0]
            connected = graph_mod.get_connected(name, depth=2)
            if not connected:
                print(f"No connections found for: {name}")
            else:
                print(f"Connected to '{name}':")
                for ent, info in sorted(connected.items(), key=lambda x: x[1]["distance"]):
                    print(f"  [{info['distance']}] {ent} ({info['relation']})")
    
    elif cmd == "lint":
        import lint as lint_mod
        fix_mode = "--fix" in args
        issues, total_pages, fixed = lint_mod.run_all_checks(fix=fix_mode)
        print(f"Wiki Lint — {total_pages} pages, {len(issues)} issues")
        if fix_mode:
            print(f"Auto-fixed: {fixed}")
        print()
        if not issues:
            print("All checks passed!")
        else:
            sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            issues.sort(key=lambda x: sev_order.get(lint_mod.SEVERITY.get(x[0], "LOW"), 99))
            for check, target, msg in issues:
                sev = lint_mod.SEVERITY.get(check, "LOW")
                print(f"  [{sev}] {check}: {target}")
                print(f"    -> {msg}")
    
    elif cmd == "rebuild":
        import graph as graph_mod
        n_ent, n_rel = graph_mod.rebuild_graph()
        print(f"Graph rebuilt: {n_ent} entities, {n_rel} relations")
    
    elif cmd == "top":
        import search as search_mod
        pages = search_mod.load_pages()
        n = int(args[0]) if args else 10
        sorted_pages = sorted(pages.items(), key=lambda x: x[1]["access_count"], reverse=True)[:n]
        print(f"Top {n} most accessed pages:")
        for name, page in sorted_pages:
            print(f"  {page['access_count']:3d}x  {page['title']} (confidence={page['confidence']})")
    
    elif cmd == "ingest":
        import auto_ingest
        results = auto_ingest.ingest_new_files()
        print(f"Created: {len(results['created'])}, Skipped: {len(results['skipped'])}, Errors: {len(results['errors'])}")
        for p in results["created"]:
            print(f"  + {p}")
    
    elif cmd == "decay":
        import decay
        dry_run = "--dry-run" in args
        results = decay.apply_decay(dry_run=dry_run)
        print(f"Decayed: {len(results['decayed'])}, Archived: {len(results['archived'])}, Unchanged: {len(results['unchanged'])}")
        for item in results["decayed"]:
            print(f"  ~ {item}")
    
    elif cmd == "maintenance":
        import hooks
        hooks.weekly_maintenance()
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
