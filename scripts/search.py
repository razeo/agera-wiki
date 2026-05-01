#!/usr/bin/env python3
"""
Wiki Search - Confidence-weighted search engine for LLM Wiki v2
Supports BM25 keyword search, entity-aware search, and graph traversal.
"""
import os
import re
import sys
import math
import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter

WIKI_ROOT = Path(os.path.expanduser("~/wiki"))


def load_pages():
    """Load all wiki pages with frontmatter and content."""
    pages = {}
    for folder in ("concepts", "entities", "comparisons"):
        fpath = WIKI_ROOT / folder
        if not fpath.exists():
            continue
        for f in fpath.glob("*.md"):
            rel = str(f.relative_to(WIKI_ROOT))
            content = f.read_text(encoding="utf-8")
            
            match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
            if not match:
                continue
            try:
                fm = yaml.safe_load(match.group(1))
            except:
                continue
            
            body = match.group(2)
            name = f.stem
            pages[name] = {
                "file": rel,
                "title": fm.get("title", name),
                "body": body,
                "tags": fm.get("tags", []),
                "entity_type": fm.get("entity_type", "concept"),
                "confidence": fm.get("confidence", 0.7),
                "access_count": fm.get("access_count", 0),
                "last_accessed": fm.get("last_accessed"),
            }
    return pages


def tokenize(text):
    """Simple tokenizer: lowercase, split on non-alpha, remove short tokens."""
    tokens = re.findall(r'[a-zšđčćž]+', text.lower())
    return [t for t in tokens if len(t) > 2]


def bm25_search(query, pages, k1=1.5, b=0.75):
    """
    BM25 scoring algorithm.
    Returns list of (name, score) sorted by score descending.
    """
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    
    N = len(pages)
    
    # Document frequencies
    df = defaultdict(int)
    doc_tokens = {}
    doc_lens = {}
    
    for name, page in pages.items():
        tokens = tokenize(page["title"] + " " + page["body"])
        doc_tokens[name] = tokens
        doc_lens[name] = len(tokens)
        unique_tokens = set(tokens)
        for token in unique_tokens:
            df[token] += 1
    
    avg_dl = sum(doc_lens.values()) / N if N > 0 else 1
    
    scores = {}
    for name, page in pages.items():
        score = 0.0
        tokens = doc_tokens[name]
        token_counts = Counter(tokens)
        dl = doc_lens[name]
        
        for qt in query_tokens:
            if qt not in df:
                continue
            tf = token_counts.get(qt, 0)
            idf = math.log((N - df[qt] + 0.5) / (df[qt] + 0.5) + 1)
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
            score += idf * tf_norm
        
        if score > 0:
            # Weight by confidence
            confidence = page.get("confidence", 0.7)
            weighted_score = score * (0.5 + 0.5 * confidence)
            scores[name] = weighted_score
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def tag_search(query, pages):
    """Search by tags."""
    query_lower = query.lower()
    results = []
    for name, page in pages.items():
        for tag in page.get("tags", []):
            if query_lower in tag.lower() or tag.lower() in query_lower:
                results.append((name, 1.0))
                break
    return results


def entity_search(query, pages):
    """Search for entity names in wikilinks and titles."""
    query_lower = query.lower()
    results = []
    for name, page in pages.items():
        if query_lower in name.lower() or query_lower in page["title"].lower():
            results.append((name, 1.5))
    return results


def search(query, max_results=10):
    """
    Combined search: BM25 + tag + entity.
    Returns list of dicts with name, score, title, confidence, entity_type, file.
    """
    pages = load_pages()
    
    # Run all search methods
    bm25_results = dict(bm25_search(query, pages))
    tag_results = dict(tag_search(query, pages))
    entity_results = dict(entity_search(query, pages))
    
    # Merge scores (reciprocal rank fusion simplified)
    combined = defaultdict(float)
    for name, score in bm25_results.items():
        combined[name] += score
    for name, score in tag_results.items():
        combined[name] += score * 2  # boost tag matches
    for name, score in entity_results.items():
        combined[name] += score * 3  # boost entity name matches
    
    # Sort by combined score
    sorted_results = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:max_results]
    
    # Build output
    output = []
    for name, score in sorted_results:
        page = pages.get(name)
        if page:
            output.append({
                "name": name,
                "title": page["title"],
                "score": round(score, 3),
                "confidence": page["confidence"],
                "entity_type": page["entity_type"],
                "tags": page["tags"],
                "file": page["file"],
            })
    
    return output


def update_access(name):
    """Increment access_count for a page."""
    from datetime import date
    pages_dir = [WIKI_ROOT / "concepts", WIKI_ROOT / "entities"]
    today = date.today().isoformat()
    
    for folder in pages_dir:
        fpath = folder / f"{name}.md"
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            
            # Update access_count
            content = re.sub(
                r'access_count: (\d+)',
                lambda m: f"access_count: {int(m.group(1)) + 1}",
                content
            )
            # Update last_accessed
            content = re.sub(
                r'last_accessed: \S+',
                f"last_accessed: {today}",
                content
            )
            
            fpath.write_text(content, encoding="utf-8")
            return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: search.py <query>")
        print("       search.py --top [N]    (most accessed pages)")
        sys.exit(1)
    
    if sys.argv[1] == "--top":
        pages = load_pages()
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        sorted_pages = sorted(pages.items(), key=lambda x: x[1]["access_count"], reverse=True)[:n]
        print(f"Top {n} most accessed pages:")
        for name, page in sorted_pages:
            print(f"  {page['access_count']:3d}x  {page['title']} (confidence={page['confidence']})")
        return
    
    query = " ".join(sys.argv[1:])
    results = search(query)
    
    if not results:
        print(f"No results for: {query}")
        return
    
    print(f"Search: '{query}' — {len(results)} results\n")
    for i, r in enumerate(results, 1):
        conf_bar = "#" * int(r["confidence"] * 10)
        print(f"{i}. {r['title']}")
        print(f"   score={r['score']:.3f}  confidence={r['confidence']} [{conf_bar}]  type={r['entity_type']}")
        print(f"   tags: {', '.join(r['tags'][:5])}")
        print(f"   file: {r['file']}")
        print()
    
    # Update access for top result
    if results:
        update_access(results[0]["name"])


if __name__ == "__main__":
    main()
