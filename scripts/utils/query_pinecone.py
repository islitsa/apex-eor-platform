"""
Query Pinecone instance and summarize what's stored there
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
    print("PINECONE KNOWLEDGE BASE SUMMARY")
    print("=" * 80)

    # Initialize knowledge base
    kb = DesignKnowledgeBasePinecone()

    # Get stats
    print("\n[1/3] Getting index statistics...")
    stats = kb.get_stats()

    print(f"\nINDEX STATS:")
    print(f"  Index name: {kb.index_name}")
    print(f"  Namespace: {kb.namespace}")
    print(f"  Dimension: {stats.get('dimension', 'unknown')}")
    print(f"  Total vectors: {stats.get('total_vectors', 0)}")

    if 'namespaces' in stats and stats['namespaces']:
        print(f"\n  Namespaces breakdown:")
        for ns, ns_stats in stats['namespaces'].items():
            print(f"    - {ns}: {ns_stats.get('vector_count', 0)} vectors")

    # Query for different categories to see what's stored
    print("\n" + "=" * 80)
    print("[2/3] Querying by category...")
    print("=" * 80)

    categories_to_check = [
        ("pattern", "UX patterns and navigation"),
        ("component", "UI components"),
        ("principle", "design principles"),
        ("constraint", "Gradio constraints"),
        ("accessibility", "accessibility guidelines"),
        ("layout", "layout guidelines"),
        ("color", "color and typography"),
        ("interaction", "user interactions"),
        ("data-viz", "data visualization"),
        ("dashboard", "dashboard design")
    ]

    category_results = {}

    for category, description in categories_to_check:
        print(f"\nQuerying category: {category} ({description})...")
        results = kb.query(
            query_text=category,
            top_k=10,
            category=category
        )

        if results:
            print(f"  Found {len(results)} items:")
            category_results[category] = results
            for i, item in enumerate(results[:5], 1):  # Show top 5
                print(f"    {i}. [{item['score']:.3f}] {item['title']}")
                if len(item['title']) < 50:  # Show content preview for short titles
                    preview = item['content'][:100].replace('\n', ' ')
                    print(f"       {preview}...")
        else:
            print(f"  No items found for category: {category}")

    # General queries to see what types of content exist
    print("\n" + "=" * 80)
    print("[3/3] Sample queries to understand content...")
    print("=" * 80)

    sample_queries = [
        "navigation master-detail drill-down hierarchy",
        "Gradio component limitations",
        "Material Design 3 color palette",
        "dashboard layout best practices",
        "data table pagination",
        "accessibility WCAG",
        "interactive file explorer",
        "button actions and interactions"
    ]

    for query_text in sample_queries:
        print(f"\nQuery: '{query_text}'")
        results = kb.query(query_text, top_k=3)

        if results:
            print(f"  Top {len(results)} matches:")
            for i, item in enumerate(results, 1):
                print(f"    {i}. [{item['score']:.3f}] {item['title']} (category: {item['category']})")
        else:
            print("  No matches")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_items = sum(len(results) for results in category_results.values())

    print(f"\nTotal unique items found across categories: {total_items}")
    print(f"\nCategories with content:")
    for category, results in sorted(category_results.items(), key=lambda x: len(x[1]), reverse=True):
        if results:
            print(f"  - {category}: {len(results)} items")

    print("\nKnowledge base appears to contain:")
    if category_results.get('pattern'):
        print("  * UX/UI patterns (navigation, master-detail, etc.)")
    if category_results.get('component'):
        print("  * Component guidelines and templates")
    if category_results.get('principle'):
        print("  * Design principles and best practices")
    if category_results.get('constraint'):
        print("  * Gradio-specific constraints and limitations")
    if category_results.get('accessibility'):
        print("  * Accessibility standards (WCAG, ARIA)")
    if category_results.get('layout'):
        print("  * Layout and spacing guidelines")
    if category_results.get('color'):
        print("  * Color palettes and typography")
    if category_results.get('data-viz'):
        print("  * Data visualization principles")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
