# Email Template System

## Overview

The email template system automatically adapts email formats based on:
- **Website Category**: art_gallery, interior_decor, home_tech, mom_blogs, nft_tech, editorial_media, holiday_family
- **Social Media Platform**: Instagram, TikTok, Behance, Dribbble, Pinterest, etc.
- **Website Context**: Description, metadata, and detected content

## How It Works

### 1. Template-Based Generation (Default)

When `use_ai=false`, the system uses pre-defined templates that adapt based on:

- **Category-specific templates**: Each category has unique subject lines and body templates
- **Social media context**: If a contact has social links, the intro adapts to mention their platform
- **Personalization**: Templates include placeholders for:
  - Business name
  - Recipient name
  - Business context (from description/social media)
  - Personalized intro (based on platform/category)
  - Specific offer (tailored to category)

### 2. AI-Based Generation

When `use_ai=true`, the system uses OpenAI or Gemini with:
- Website description and metadata
- Detected category and art style
- Social media platform information
- Business context

## Usage

### API Endpoint

```http
POST /api/v1/emails/generate?website_id=123&contact_id=456&use_ai=false
```

**Query Parameters:**
- `website_id` (required): ID of the scraped website
- `contact_id` (optional): ID of the contact (for social media context)
- `use_ai` (optional, default: true): Use AI or templates
- `provider` (optional): 'openai' or 'gemini' (only if use_ai=true)

### Example Response

```json
{
  "subject": "Collaboration Opportunity for Art Gallery Name",
  "body": "Hello Team,\n\nI hope this message finds you well...",
  "context": {
    "business_name": "Art Gallery Name",
    "business_context": "your gallery's collection",
    "recipient_name": "Team",
    "personalized_intro": "Your gallery's curation and artist selection is impressive.",
    "specific_offer": "I'd love to discuss potential art collaborations...",
    "category": "art_gallery"
  },
  "website_id": 123,
  "contact_id": 456,
  "method": "template",
  "category": "art_gallery",
  "social_platform": "instagram"
}
```

## Template Categories

### Art Gallery
- Subject: "Collaboration Opportunity for {business_name}"
- Focus: Art collaborations, exhibitions, cross-promotion

### Interior Decor
- Subject: "Design Partnership Opportunity"
- Focus: Design partnerships, product collaborations

### Home Tech
- Subject: "Tech Innovation Partnership"
- Focus: Tech partnerships, product reviews, innovation

### Mom Blogs
- Subject: "Content Collaboration Opportunity"
- Focus: Content collaborations, sponsored posts, brand partnerships

### NFT Tech
- Subject: "NFT/Web3 Collaboration"
- Focus: NFT collaborations, digital art partnerships, Web3 initiatives

### Editorial Media
- Subject: "Media Partnership Opportunity"
- Focus: Editorial partnerships, content collaborations, media opportunities

### Holiday/Family
- Subject: "Family-Focused Collaboration"
- Focus: Family content collaborations

## Customization

Templates can be customized in `ai/email_templates.py`:

1. **Add new categories**: Add entries to `self.templates` dictionary
2. **Modify subject lines**: Update `subject_templates` array
3. **Change body format**: Modify `body_template` string
4. **Adjust personalization**: Update `_generate_personalized_intro()` method
5. **Customize offers**: Modify `_generate_specific_offer()` method

## Integration with Scraping

When a website is scraped:
1. Website category is automatically detected
2. Contacts are extracted (including social media links)
3. Email templates adapt based on:
   - Website category
   - Social media platforms found
   - Website description and content

This ensures emails are always contextually relevant to the business being contacted.

