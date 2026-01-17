"""
Test script for email generation with Gemini
"""
from ai.email_generator import EmailGenerator
from utils.logging_config import setup_logging

# Setup logging
setup_logging()

# Initialize generator
generator = EmailGenerator()

# Example context
context = {
    "website_summary": "A contemporary art gallery featuring digital art and NFT collections",
    "art_style": "art_gallery",
    "category": "art_gallery",
    "description": "Contemporary art gallery showcasing digital art, NFTs, and modern installations",
    "metadata": {
        "title": "Modern Art Gallery",
        "keywords": ["art", "gallery", "digital art", "NFT"]
    }
}

# Generate email
print("Generating outreach email with Gemini...")
print(f"Business: Modern Art Gallery")
print(f"URL: https://example-gallery.com")
print("\n" + "="*50 + "\n")

result = generator.generate_outreach_email(
    business_name="Modern Art Gallery",
    website_url="https://example-gallery.com",
    context=context,
    provider="gemini"
)

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print("SUBJECT:")
    print(result["subject"])
    print("\n" + "-"*50 + "\n")
    print("BODY:")
    print(result["body"])

