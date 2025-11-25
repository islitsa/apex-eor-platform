"""
Query Pinecone instance for detailed content samples
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone

def main():
    print("=" * 80)
    print("PINECONE DETAILED CONTENT SAMPLES")
    print("=" * 80)

    # Initialize knowledge base
    kb = DesignKnowledgeBasePinecone()

    # Get full content for key items
    print("\n[1] NAVIGATION PATTERNS")
    print("-" * 80)
    nav_results = kb.query("navigation hierarchy drill-down", top_k=3)
    for i, item in enumerate(nav_results, 1):
        print(f"\n{i}. {item['title']} (score: {item['score']:.3f})")
        print(f"   Category: {item['category']}")
        print(f"   Content preview (first 500 chars):")
        print(f"   {item['content'][:500]}...")
        print()

    print("\n[2] MATERIAL DESIGN 3 COMPONENTS")
    print("-" * 80)
    m3_results = kb.query("Material Design 3", top_k=3, category="component")
    for i, item in enumerate(m3_results, 1):
        print(f"\n{i}. {item['title']} (score: {item['score']:.3f})")
        print(f"   Category: {item['category']}")
        print(f"   Content preview (first 500 chars):")
        print(f"   {item['content'][:500]}...")
        print()

    print("\n[3] DESIGN PRINCIPLES")
    print("-" * 80)
    principles = kb.query("design principles best practices", top_k=3, category="principle")
    for i, item in enumerate(principles, 1):
        print(f"\n{i}. {item['title']} (score: {item['score']:.3f})")
        print(f"   Category: {item['category']}")
        print(f"   Content preview (first 500 chars):")
        print(f"   {item['content'][:500]}...")
        print()

    print("\n[4] INTERACTION PATTERNS")
    print("-" * 80)
    interactions = kb.query("button actions click interactions", top_k=3, category="interaction")
    for i, item in enumerate(interactions, 1):
        print(f"\n{i}. {item['title']} (score: {item['score']:.3f})")
        print(f"   Category: {item['category']}")
        print(f"   Content preview (first 500 chars):")
        print(f"   {item['content'][:500]}...")
        print()

    print("\n[5] LAYOUT GUIDELINES")
    print("-" * 80)
    layouts = kb.query("layout grid spacing dashboard", top_k=3, category="layout")
    for i, item in enumerate(layouts, 1):
        print(f"\n{i}. {item['title']} (score: {item['score']:.3f})")
        print(f"   Category: {item['category']}")
        print(f"   Content preview (first 500 chars):")
        print(f"   {item['content'][:500]}...")
        print()

    print("\n[6] FULL CATEGORY LIST")
    print("-" * 80)
    # Query all items and collect unique categories
    all_items = kb.query("design", top_k=67)  # Get all 67 items
    categories = {}
    for item in all_items:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item['title'])

    print(f"\nFound {len(categories)} unique categories:")
    for cat, titles in sorted(categories.items()):
        print(f"\n  {cat} ({len(titles)} items):")
        for title in titles[:5]:  # Show first 5
            print(f"    - {title}")
        if len(titles) > 5:
            print(f"    ... and {len(titles) - 5} more")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
