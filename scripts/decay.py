#!/usr/bin/env python3
"""
Wiki Decay - Apply confidence retention decay to wiki pages.
Run periodically (weekly recommended) to decay unaccessed pages.
"""
import os
import re
import sys
import yaml
from pathlib import Path
from datetime import date, timedelta

WIKI_ROOT = Path(os.path.expanduser("~/wiki"))

# Decay rates per month
DECAY_RATES = {
    "concept": 0.008,       # -0.05 per 6 months
    "regulation": 0.004,    # -0.02 per 6 months (slower)
    "document": 0.008,
    "institution": 0.002,   # very slow (institutions rarely change)
    "company": 0.006,
    "procedure": 0.003,     # procedural memory decays slowly
    "person": 0.008,
}

# Reinforcement: confidence boost on access
REINFORCE_ON_ACCESS = 0.05


def apply_decay(dry_run=False):
    """Apply confidence decay to all pages based on last_confirmed."""
    today = date.today()
    results = {"decayed": [], "archived": [], "unchanged": []}
    
    for folder in ("concepts", "entities"):
        fpath = WIKI_ROOT / folder
        if not fpath.exists():
            continue
        for md_file in fpath.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            
            # Parse frontmatter
            match = re.match(r'^(---\n.*?\n---\n)(.*)', content, re.DOTALL)
            if not match:
                continue
            try:
                fm = yaml.safe_load(re.search(r'^---\n(.*?)\n---', match.group(1), re.DOTALL).group(1))
            except:
                continue
            
            confidence = fm.get("confidence", 0.7)
            entity_type = fm.get("entity_type", "concept")
            last_confirmed_str = fm.get("last_confirmed")
            last_accessed_str = fm.get("last_accessed")
            
            if not last_confirmed_str:
                results["unchanged"].append(md_file.name)
                continue
            
            try:
                last_confirmed = date.fromisoformat(str(last_confirmed_str))
            except ValueError:
                results["unchanged"].append(md_file.name)
                continue
            
            # Calculate months since last confirmation
            months_since = (today - last_confirmed).days / 30.44
            
            # Get decay rate
            decay_rate = DECAY_RATES.get(entity_type, 0.008)
            
            # Calculate decay
            decay = months_since * decay_rate
            
            # Apply reinforcement if recently accessed
            if last_accessed_str:
                try:
                    last_accessed = date.fromisoformat(str(last_accessed_str))
                    days_since_access = (today - last_accessed).days
                    if days_since_access < 30:
                        # Recent access reduces decay
                        decay *= 0.5
                except ValueError:
                    pass
            
            new_confidence = round(max(0.0, confidence - decay), 2)
            
            if new_confidence < 0.1:
                # Archive
                if not dry_run:
                    archive_dir = WIKI_ROOT / "_archive"
                    archive_dir.mkdir(exist_ok=True)
                    archive_path = archive_dir / md_file.name
                    md_file.rename(archive_path)
                results["archived"].append(f"{md_file.name} (confidence: {confidence} -> {new_confidence})")
            elif new_confidence != confidence:
                # Update confidence
                if not dry_run:
                    new_content = content.replace(
                        f"confidence: {confidence}", 
                        f"confidence: {new_confidence}", 1
                    )
                    md_file.write_text(new_content, encoding="utf-8")
                results["decayed"].append(f"{md_file.name}: {confidence} -> {new_confidence}")
            else:
                results["unchanged"].append(md_file.name)
    
    return results


def reinforce_page(name):
    """Reinforce a page's confidence (called on access)."""
    today = date.today().isoformat()
    
    for folder in ("concepts", "entities"):
        fpath = WIKI_ROOT / folder / f"{name}.md"
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            
            # Bump confidence
            match = re.search(r'confidence: (\d+\.?\d*)', content)
            if match:
                old_conf = float(match.group(1))
                new_conf = min(1.0, round(old_conf + REINFORCE_ON_ACCESS, 2))
                content = content.replace(
                    f"confidence: {old_conf}",
                    f"confidence: {new_conf}", 1
                )
            
            # Update last_confirmed and last_accessed
            content = re.sub(r'last_confirmed: \S+', f'last_confirmed: {today}', content)
            content = re.sub(r'last_accessed: \S+', f'last_accessed: {today}', content)
            content = re.sub(r'access_count: (\d+)', 
                lambda m: f'access_count: {int(m.group(1)) + 1}', content)
            
            fpath.write_text(content, encoding="utf-8")
            return True
    return False


def main():
    dry_run = "--dry-run" in sys.argv
    
    print(f"Wiki Decay — {date.today().isoformat()}")
    if dry_run:
        print("(DRY RUN - no changes)")
    print()
    
    results = apply_decay(dry_run=dry_run)
    
    print(f"Decayed:  {len(results['decayed'])}")
    print(f"Archived: {len(results['archived'])}")
    print(f"Unchanged: {len(results['unchanged'])}")
    
    if results["decayed"]:
        print("\nDecayed pages:")
        for item in results["decayed"]:
            print(f"  ~ {item}")
    
    if results["archived"]:
        print("\nArchived pages:")
        for item in results["archived"]:
            print(f"  x {item}")
    
    # Rebuild graph if pages were archived
    if results["archived"] and not dry_run:
        print("\nRebuilding graph...")
        sys.path.insert(0, str(WIKI_ROOT / "scripts"))
        from graph import rebuild_graph
        n_ent, n_rel = rebuild_graph()
        print(f"  Graph: {n_ent} entities, {n_rel} relations")


if __name__ == "__main__":
    main()
