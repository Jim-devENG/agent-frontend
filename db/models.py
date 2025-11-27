"""
Database models for the Autonomous Art Outreach Scraper
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class ScrapedWebsite(Base):
    """Model for scraped websites"""
    __tablename__ = "scraped_websites"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, index=True)
    title = Column(String)
    description = Column(Text)
    website_type = Column(String)  # gallery, portfolio, instagram, tiktok, behance, dribbble, pinterest, website
    category = Column(String)  # art, tech_blog, nft, mothers_tech, interior_design, unknown
    raw_html = Column(Text)  # Raw HTML content
    extra_metadata = Column(JSON)  # Additional scraped data
    status = Column(String, default="pending")  # pending, processed, failed
    is_art_related = Column(Boolean, default=False)  # Whether site is art-related or in target categories
    # Quality metrics
    domain_authority = Column(Integer)  # 0-100
    quality_score = Column(Integer)  # 0-100
    estimated_traffic = Column(JSON)  # Traffic metrics
    ssl_valid = Column(Boolean, default=False)
    domain_age_days = Column(Integer, nullable=True)
    has_valid_dns = Column(Boolean, default=False)
    meets_quality_threshold = Column(Boolean, default=False)  # Whether site meets quality criteria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contacts = relationship("Contact", back_populates="website")
    outreach_emails = relationship("OutreachEmail", back_populates="website")


class Contact(Base):
    """Model for extracted contacts (emails, social links, phone numbers)"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("scraped_websites.id"), nullable=False)
    email = Column(String, index=True)
    phone_number = Column(String, index=True)
    social_platform = Column(String)  # instagram, tiktok, behance, dribbble, pinterest, twitter, facebook, linkedin, youtube, snapchat
    social_url = Column(String)
    contact_page_url = Column(String)
    name = Column(String)
    role = Column(String)  # artist, gallery_owner, curator, etc.
    source = Column(String)  # hunter_io, html, footer, header, contact_form, javascript, etc.
    extra_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    website = relationship("ScrapedWebsite", back_populates="contacts")
    outreach_emails = relationship("OutreachEmail", back_populates="contact")


class ContactForm(Base):
    """Model for detected contact forms"""
    __tablename__ = "contact_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("scraped_websites.id"), nullable=False)
    form_url = Column(String, nullable=False)  # URL where form was found
    form_action = Column(String)  # Form action URL
    form_method = Column(String, default="post")  # Form method (get/post)
    form_fields = Column(JSON)  # List of form fields
    is_contact_form = Column(Boolean, default=True)
    extra_metadata = Column(JSON)  # Additional form metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    website = relationship("ScrapedWebsite", backref="contact_forms")


class OutreachEmail(Base):
    """Model for generated and sent outreach emails"""
    __tablename__ = "outreach_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("scraped_websites.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    recipient_email = Column(String, nullable=False, index=True)
    status = Column(String, default="draft")  # draft, sent, failed, bounced
    ai_model_used = Column(String)  # gpt-4, gemini-pro
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    extra_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    website = relationship("ScrapedWebsite", back_populates="outreach_emails")
    contact = relationship("Contact", back_populates="outreach_emails")


class ScrapingJob(Base):
    """Model for tracking scraping jobs"""
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, nullable=False)  # website_scrape, email_extraction, etc.
    target_url = Column(String)
    status = Column(String, default="pending")  # pending, running, completed, failed
    result = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ActivityLog(Base):
    """Model for real-time activity logging"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(String, nullable=False, index=True)  # scrape, extract, email, job
    message = Column(Text, nullable=False)
    status = Column(String, default="info")  # info, success, warning, error
    website_id = Column(Integer, ForeignKey("scraped_websites.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("scraping_jobs.id"), nullable=True)
    extra_data = Column(JSON)  # Additional context (counts, URLs, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    website = relationship("ScrapedWebsite", backref="activity_logs")
    job = relationship("ScrapingJob", backref="activity_logs")


class AppSettings(Base):
    """Model for application settings and automation control"""
    __tablename__ = "app_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmailTemplate(Base):
    """Model for customizable email templates"""
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Template name/identifier
    category = Column(String, index=True)  # art_gallery, interior_decor, etc. or "default"
    subject_template = Column(Text, nullable=False)  # Subject line template with variables
    body_template = Column(Text, nullable=False)  # Body template with variables
    is_active = Column(Boolean, default=True)  # Whether this template is active
    is_default = Column(Boolean, default=False)  # Whether this is the default for category
    variables = Column(JSON)  # Available variables: {business_name, recipient_name, etc.}
    description = Column(Text)  # Template description
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DiscoveredWebsite(Base):
    """Model for discovered websites (from search engines, before scraping)"""
    __tablename__ = "discovered_websites"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, index=True)
    title = Column(String)  # Title from search result
    snippet = Column(Text)  # Description/snippet from search result
    source = Column(String)  # duckduckgo, google, bing, seed_list, manual
    search_query = Column(String)  # The query that found this website
    category = Column(String)  # Predicted category based on search query
    is_scraped = Column(Boolean, default=False, index=True)  # Whether this has been scraped
    scraped_website_id = Column(Integer, ForeignKey("scraped_websites.id"), nullable=True)  # Link to scraped website if exists
    discovery_metadata = Column(JSON)  # Additional discovery data (rank, search position, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    scraped_website = relationship("ScrapedWebsite", foreign_keys=[scraped_website_id])
