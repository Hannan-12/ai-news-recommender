# prompt.py

SUMMARIZATION_PROMPT = """
Please provide a concise summary of the following news article in 2-3 sentences:

{article_text}

Summary:
"""

CATEGORIZATION_PROMPT = """
Please categorize the following news article into one of these categories:
- technology
- business
- health
- science
- entertainment
- politics
- sports
- world

Title: {title}
Description: {description}

Return only the category name, nothing else.
"""