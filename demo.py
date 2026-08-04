#!/usr/bin/env python3
"""
Higgsfield Prompt Master — CLI & Examples
==========================================
Usage examples and interactive demo.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from higgsfield_prompt import HiggsfieldPromptMaster, search_prompts, get_templates, analyze_patterns, generate_prompt, random_prompt
from pathlib import Path

def demo():
    hpm = HiggsfieldPromptMaster()
    
    print("=" * 60)
    print("HIGGSFIELD PROMPT MASTER — DEMO")
    print("=" * 60)
    
    # 1. Corpus stats
    print("\n📊 CORPUS STATISTICS")
    stats = hpm.stats()
    print(f"   Total prompts: {stats['total_prompts']:,}")
    print(f"   GPT Image 2: {stats['models'].get('GPT Image 2', 0):,}")
    print(f"   Nano Banana: {stats['models'].get('Nano Banana', 0):,}")
    print(f"   Structures: {stats['structures']}")
    print(f"   Top 5 techniques: {dict(list(stats['techniques'].items())[:5])}")
    
    # 2. Category guide
    print("\n📂 CATEGORY GUIDE: App / Web Design")
    guide = hpm.category_guide("App / Web Design")
    print(f"   Total prompts: {guide['total_prompts']}")
    print(f"   Avg length: {guide['length_stats']['avg']:,} chars")
    print(f"   Structure breakdown:")
    for s in guide['structure_breakdown']:
        print(f"     {s['structure_type']}: {s['cnt']} (avg {int(s['avg_len'])} chars)")
    print(f"   Top techniques:")
    for t in guide['technique_frequency'][:5]:
        print(f"     {t['technique']}: {t['cnt']}")
    
    # 3. Search examples
    print("\n🔍 SEARCH EXAMPLES")
    
    print("\n  Search: 'glassmorphism dashboard'")
    results = hpm.search(query="glassmorphism dashboard", limit=3)
    for p in results:
        print(f"    [{p.id}] {p.title[:50]} ({p.structure_type})")
    
    print("\n  FTS Search: 'glassmorphism dashboard'")
    results = hpm.fts_search("glassmorphism dashboard", limit=3)
    for p in results:
        print(f"    [{p.id}] {p.title[:50]} ({p.structure_type})")
    
    print("\n  Filter: category=Product Marketing, structure=Template")
    results = hpm.search(category="Product Marketing", structure="Template", limit=3)
    for p in results:
        print(f"    [{p.id}] {p.title[:50]} ({p.length_chars} chars)")
    
    # 4. Generation
    print("\n✨ PROMPT GENERATION")
    
    print("\n  JSON (App / Web Design):")
    prompt = hpm.generate_prompt(
        goal="Real-time analytics dashboard with charts and metrics",
        category="App / Web Design",
        structure="JSON",
        style="Modern, glassmorphism, dark theme, purple/blue accents"
    )
    print(f"  {prompt[:300]}...")
    
    print("\n  Template (Product Marketing):")
    prompt = hpm.generate_prompt(
        goal="Wireless noise-canceling headphones",
        category="Product Marketing",
        structure="Template",
        style="Premium, minimal, studio lighting",
        aspect_ratio="4:5"
    )
    print(f"  {prompt[:300]}...")
    
    print("\n  Flat Prose (Character):")
    prompt = hpm.generate_prompt(
        goal="Cyberpunk samurai warrior",
        category="Character",
        structure="Flat prose",
        style="Neon-lit alley, rain, volumetric fog, cinematic",
        aspect_ratio="9:16"
    )
    print(f"  {prompt[:300]}...")
    
    # 5. Model comparison
    print("\n⚖️ MODEL COMPARISON: GPT Image 2 vs Nano Banana")
    comparison = hpm.compare_models("GPT Image 2", "Nano Banana")
    for model, data in comparison.items():
        print(f"\n  {model}:")
        print(f"    Structures: {data['structures']}")
        print(f"    Top techniques: {list(data['top_techniques'].keys())[:5]}")
        print(f"    Top categories: {list(data['top_categories'].keys())[:5]}")
    
    # 6. Random inspiration
    print("\n🎲 RANDOM INSPIRATION")
    for cat in ["App / Web Design", "Product Marketing", "Comic / Storyboard"]:
        p = hpm.random_prompt(category=cat)
        if p:
            print(f"  [{cat}] {p.title[:50]}")
            print(f"    {p.prompt_text[:120]}...")

if __name__ == "__main__":
    demo()