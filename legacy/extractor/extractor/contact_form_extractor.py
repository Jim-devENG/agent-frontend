"""
Contact form detection and extraction
"""
from typing import List, Dict
from bs4 import BeautifulSoup
import re


class ContactFormExtractor:
    """Detect and extract contact form information"""
    
    # Form-related keywords
    FORM_KEYWORDS = [
        "contact", "message", "inquiry", "reach", "connect",
        "get in touch", "send", "submit", "form", "feedback"
    ]
    
    def extract_contact_forms(self, html_content: str, base_url: str = "") -> List[Dict]:
        """
        Extract contact forms from HTML
        
        Args:
            html_content: HTML string
            base_url: Base URL for resolving relative form actions
            
        Returns:
            List of dictionaries with form information
        """
        soup = BeautifulSoup(html_content, "lxml")
        forms = []
        
        # Find all form elements
        for form in soup.find_all("form"):
            form_info = self._analyze_form(form, base_url)
            if form_info:
                forms.append(form_info)
        
        return forms
    
    def _analyze_form(self, form, base_url: str) -> Dict:
        """Analyze a form element and extract relevant information"""
        form_info = {
            "action": "",
            "method": "",
            "fields": [],
            "is_contact_form": False,
            "form_id": "",
            "form_class": ""
        }
        
        # Get form attributes
        form_info["action"] = form.get("action", "")
        form_info["method"] = form.get("method", "get").lower()
        form_info["form_id"] = form.get("id", "")
        form_info["form_class"] = " ".join(form.get("class", []))
        
        # Check if this looks like a contact form
        form_text = form.get_text().lower()
        form_html = str(form).lower()
        
        is_contact = any(
            keyword in form_text or keyword in form_html
            for keyword in self.FORM_KEYWORDS
        )
        
        form_info["is_contact_form"] = is_contact
        
        # Extract form fields
        fields = []
        for input_field in form.find_all(["input", "textarea", "select"]):
            field_info = {
                "type": input_field.get("type", input_field.name),
                "name": input_field.get("name", ""),
                "id": input_field.get("id", ""),
                "placeholder": input_field.get("placeholder", ""),
                "label": self._get_field_label(input_field, form),
                "required": input_field.has_attr("required")
            }
            fields.append(field_info)
        
        form_info["fields"] = fields
        
        # Only return if it's likely a contact form
        if is_contact or len(fields) > 0:
            return form_info
        
        return None
    
    def _get_field_label(self, field, form) -> str:
        """Get the label associated with a form field"""
        # Try to find label by 'for' attribute
        field_id = field.get("id", "")
        if field_id:
            label = form.find("label", {"for": field_id})
            if label:
                return label.get_text(strip=True)
        
        # Try to find label by name
        field_name = field.get("name", "")
        if field_name:
            label = form.find("label", string=re.compile(field_name, re.IGNORECASE))
            if label:
                return label.get_text(strip=True)
        
        # Try to find preceding label
        prev = field.find_previous_sibling("label")
        if prev:
            return prev.get_text(strip=True)
        
        return ""
    
    def has_contact_form(self, html_content: str) -> bool:
        """Check if page has a contact form"""
        forms = self.extract_contact_forms(html_content)
        return any(form.get("is_contact_form", False) for form in forms)

