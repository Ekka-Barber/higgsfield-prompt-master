"""
Higgsfield Prompt Master — Package
===================================
The ultimate GPT Image 2 prompt reference and generation tool.
Built from 8,596 real prompts from youmind.com.

Usage:
    from higgsfield_prompt import HiggsfieldPromptMaster
    
    hpm = HiggsfieldPromptMaster()
    results = hpm.search("dashboard glassmorphism", limit=5)
    guide = hpm.category_guide("App / Web Design")
    prompt = hpm.generate_prompt("SaaS dashboard", "App / Web Design", "JSON")
"""

from .higgsfield_prompt import (
    HiggsfieldPromptMaster,
    Prompt,
    search_prompts,
    get_templates,
    analyze_patterns,
    generate_prompt,
    random_prompt,
)

__version__ = "1.0.0"
__author__ = "Hermes Agent"
__corpus_size__ = 8596
__gpt_image_2_count__ = 7213
__nano_banana_count__ = 1362

__all__ = [
    "HiggsfieldPromptMaster",
    "Prompt",
    "search_prompts",
    "get_templates", 
    "analyze_patterns",
    "generate_prompt",
    "random_prompt",
]