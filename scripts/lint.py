#!/usr/bin/env python3
"""
Wiki Lint - Quality checks for LLM Wiki v2
Checks: orphans, broken links, stale confidence, missing fields, contradictions
"""
import os
import re
import sys
import yaml
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

WIKI_ROOT = Path(os.path.expanduser("~/wiki"))

# --- Parsers ---

def parse_frontmatter(filepath):
    """Parse YAML frontmatter from a markdown file."""
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, content
    try:
        fm = yaml.safe_load(match.group(1))
        return fm, content
    except yaml.YAMLError as e:
        return {"_parse_error": str(e)}, content


def extract_wikilinks(content):
    """Extract all [[wikilinks]] from content."""
    return re.findall(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]", content)


def find_all_pages():
    """Find all wiki pages in concepts/ and entities/."""
    pages = {}
    for folder in ("concepts", "entities", "comparisons"):
        folder_path = WIKI_ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.glob("*.md"):
            rel = str(f.relative_to(WIKI_ROOT))
            pages[rel] = f
    return pages


# --- Checks ---

def check_missing_frontmatter(pages):
    """Pages without valid YAML frontmatter."""
    issues = []
    for rel, fpath in pages.items():
        fm, _ = parse_frontmatter(fpath)
        if fm is None:
            issues.append(("MISSING_FRONTMATTER", rel, "No YAML frontmatter found"))
        elif "_parse_error" in fm:
            issues.append(("PARSE_ERROR", rel, fm["_parse_error"]))
    return issues


def check_missing_fields(pages):
    """Pages missing required LLM Wiki v2 fields."""
    required = ["confidence", "last_confirmed", "sources_count",
                 "access_count", "supersedes", "entity_type"]
    issues = []
    for rel, fpath in pages.items():
        fm, _ = parse_frontmatter(fpath)
        if not fm or "_parse_error" in fm:
            continue
        for field in required:
            if field not in fm:
                issues.append(("MISSING_FIELD", rel, f"Missing field: {field}"))
    return issues


def check_broken_links(pages):
    """Wikilinks pointing to non-existent pages."""
    # Build set of valid page names
    valid = set()
    for rel in pages:
        name = Path(rel).stem
        valid.add(name)
    
    issues = []
    for rel, fpath in pages.items():
        _, content = parse_frontmatter(fpath)
        if content is None:
            continue
        links = extract_wikilinks(content)
        for link in links:
            if link not in valid:
                issues.append(("BROKEN_LINK", rel, f"[[{link}]] -> page not found"))
    return issues


def check_orphan_pages(pages):
    """Pages with no inbound links from other pages."""
    # Build inbound link map
    inbound = defaultdict(set)
    for rel, fpath in pages.items():
        _, content = parse_frontmatter(fpath)
        if content is None:
            continue
        name = Path(rel).stem
        links = extract_wikilinks(content)
        for link in links:
            inbound[link].add(name)
    
    issues = []
    for rel in pages:
        name = Path(rel).stem
        # index.md is not a page, skip it for orphan check
        if name == "index":
            continue
        # Also skip SCHEMA, log etc
        if name in ("SCHEMA", "log"):
            continue
        if name not in inbound or len(inbound[name]) == 0:
            issues.append(("ORPHAN_PAGE", rel, "No inbound links from other pages"))
    return issues


def check_stale_confidence(pages, decay_per_month=0.008):
    """
    Check confidence decay based on last_confirmed date.
    Decay rate: -0.05 per 6 months = ~0.0083 per month
    """
    today = date.today()
    issues = []
    
    for rel, fpath in pages.items():
        fm, _ = parse_frontmatter(fpath)
        if not fm or "_parse_error" in fm:
            continue
        
        confidence = fm.get("confidence", 0.7)
        last_confirmed = fm.get("last_confirmed")
        
        if not last_confirmed:
            issues.append(("STALE_NO_DATE", rel, "No last_confirmed date"))
            continue
        
        if isinstance(last_confirmed, str):
            try:
                lc = date.fromisoformat(last_confirmed)
            except ValueError:
                issues.append(("STALE_BAD_DATE", rel, f"Invalid date: {last_confirmed}"))
                continue
        else:
            lc = last_confirmed
        
        months_old = (today - lc).days / 30.44
        decay = months_old * decay_per_month
        adjusted = round(confidence - decay, 2)
        
        if adjusted < 0.3:
            issues.append(("CONFIDENCE_FADED", rel,
                          f"confidence {confidence} -> adjusted {adjusted} "
                          f"({int(months_old)} months since confirmed)"))
        elif adjusted < confidence - 0.1:
            issues.append(("CONFIDENCE_DECAY", rel,
                          f"confidence {confidence} -> adjusted {adjusted} "
                          f"({int(months_old)} months since confirmed)"))
    return issues


def check_contradictions(pages):
    """Find pages with same tags that might contradict each other."""
    tag_map = defaultdict(list)
    issues = []
    
    for rel, fpath in pages.items():
        fm, _ = parse_frontmatter(fpath)
        if not fm or "_parse_error" in fm:
            continue
        tags = fm.get("tags", [])
        for tag in tags:
            tag_map[tag].append(rel)
    
    # Only warn about tags with many pages (potential overlap)
    for tag, rels in tag_map.items():
        if len(rels) > 5:
            issues.append(("TAG_OVERLAP", ", ".join(rels),
                          f"Tag '{tag}' has {len(rels)} pages - check for contradictions"))
    return issues


def check_low_confidence(pages):
    """Pages with confidence below threshold."""
    issues = []
    for rel, fpath in pages.items():
        fm, _ = parse_frontmatter(fpath)
        if not fm or "_parse_error" in fm:
            continue
        confidence = fm.get("confidence")
        if confidence is not None and confidence < 0.5:
            issues.append(("LOW_CONFIDENCE", rel, f"confidence={confidence}"))
    return issues


def check_entity_type(pages):
    """Pages missing entity_type."""
    issues = []
    for rel, fpath in pages.items():
        fm, _ = parse_frontmatter(fpath)
        if not fm or "_parse_error" in fm:
            continue
        et = fm.get("entity_type")
        if not et:
            issues.append(("NO_ENTITY_TYPE", rel, "entity_type not set"))
    return issues


# --- Auto-fix ---

def fix_stale_confidence(pages):
    """Auto-adjust confidence based on decay."""
    today = date.today()
    fixed = 0
    decay_per_month = 0.0083
    
    for rel, fpath in pages.items():
        fm, content = parse_frontmatter(fpath)
        if not fm or "_parse_error" in fm:
            continue
        
        confidence = fm.get("confidence", 0.7)
        last_confirmed = fm.get("last_confirmed")
        if not last_confirmed:
            continue
        
        if isinstance(last_confirmed, str):
            try:
                lc = date.fromisoformat(last_confirmed)
            except ValueError:
                continue
        else:
            continue
        
        months_old = (today - lc).days / 30.44
        decay = months_old * decay_per_month
        adjusted = round(max(0.0, confidence - decay), 2)
        
        if adjusted != confidence:
            # Update frontmatter
            old_line = f"confidence: {confidence}"
            new_line = f"confidence: {adjusted}"
            new_content = content.replace(old_line, new_line, 1)
            fpath.write_text(new_content, encoding="utf-8")
            fixed += 1
    
    return fixed


# --- Report ---

SEVERITY = {
    "PARSE_ERROR": "CRITICAL",
    "MISSING_FRONTMATTER": "CRITICAL",
    "MISSING_FIELD": "HIGH",
    "NO_ENTITY_TYPE": "HIGH",
    "BROKEN_LINK": "HIGH",
    "CONFIDENCE_FADED": "MEDIUM",
    "ORPHAN_PAGE": "MEDIUM",
    "LOW_CONFIDENCE": "MEDIUM",
    "STALE_NO_DATE": "MEDIUM",
    "STALE_BAD_DATE": "MEDIUM",
    "CONFIDENCE_DECAY": "LOW",
    "TAG_OVERLAP": "LOW",
}


def run_all_checks(fix=False):
    """Run all checks and return report."""
    pages = find_all_pages()
    
    all_issues = []
    all_issues.extend(check_missing_frontmatter(pages))
    all_issues.extend(check_missing_fields(pages))
    all_issues.extend(check_entity_type(pages))
    all_issues.extend(check_broken_links(pages))
    all_issues.extend(check_orphan_pages(pages))
    all_issues.extend(check_stale_confidence(pages))
    all_issues.extend(check_low_confidence(pages))
    all_issues.extend(check_contradictions(pages))
    
    # Sort by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_issues.sort(key=lambda x: severity_order.get(SEVERITY.get(x[0], "LOW"), 99))
    
    # Auto-fix if requested
    fixed_count = 0
    if fix:
        fixed_count = fix_stale_confidence(pages)
    
    return all_issues, len(pages), fixed_count


def main():
    fix_mode = "--fix" in sys.argv
    issues, total_pages, fixed = run_all_checks(fix=fix_mode)
    
    print(f"Wiki Lint Report — {date.today().isoformat()}")
    print(f"{'='*50}")
    print(f"Total pages: {total_pages}")
    print(f"Issues found: {len(issues)}")
    if fix_mode:
        print(f"Auto-fixed: {fixed}")
    print()
    
    if not issues:
        print("All checks passed!")
        return 0
    
    # Group by severity
    by_severity = defaultdict(list)
    for check, target, msg in issues:
        sev = SEVERITY.get(check, "LOW")
        by_severity[sev].append((check, target, msg))
    
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        items = by_severity.get(sev, [])
        if not items:
            continue
        print(f"[{sev}] ({len(items)} issues)")
        for check, target, msg in items:
            print(f"  {check}: {target}")
            print(f"    -> {msg}")
        print()
    
    return 1 if by_severity.get("CRITICAL") or by_severity.get("HIGH") else 0


if __name__ == "__main__":
    sys.exit(main())
