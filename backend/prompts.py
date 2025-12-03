# backend/prompts.py
IMAGE_PROMPT_TEMPLATE = """
Create a high-quality advertising background suitable for showcasing a product for {brand_name}.
Style: {tone}.
This must be a clean, premium background with studio lighting and negative space for product placement.
Do NOT include text or logos.
"""

CAPTION_SYSTEM_PROMPT = (
    "You are a senior marketing copywriter for premium brands. Keep captions minimal, 8-14 words, "
    "no emojis, no hashtags. Include a subtle CTA such as 'Shop now' or 'Tap to buy'."
)

CAPTION_USER_PROMPT = """
Brand: {brand_name}
Tone: {tone}
Generate exactly {count} distinct, short, premium ad captions in English.
Return only a JSON array of strings.
"""
