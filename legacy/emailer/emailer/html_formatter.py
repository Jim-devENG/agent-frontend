"""
HTML email formatting utilities
"""
from typing import Optional


class HTMLEmailFormatter:
    """Format plain text emails as HTML"""
    
    @staticmethod
    def format_as_html(
        plain_text: str,
        business_name: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> str:
        """
        Convert plain text email to HTML format
        
        Args:
            plain_text: Plain text email body
            business_name: Name of the business (for personalization)
            sender_name: Name of the sender
            
        Returns:
            HTML formatted email
        """
        # Convert line breaks to HTML
        html_body = plain_text.replace('\n', '<br>')
        
        # Convert paragraphs (double line breaks)
        paragraphs = html_body.split('<br><br>')
        formatted_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para:
                formatted_paragraphs.append(f'<p style="margin: 0 0 16px 0; line-height: 1.6; color: #333333;">{para}</p>')
        
        html_content = '\n'.join(formatted_paragraphs)
        
        # Wrap in professional email template
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px 0;">
                <table role="presentation" style="width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="padding: 40px 40px 20px 40px;">
                            <div style="color: #333333; font-size: 16px; line-height: 1.6;">
                                {html_content}
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px 40px 40px 40px; border-top: 1px solid #eeeeee;">
                            <p style="margin: 0; font-size: 12px; color: #999999; text-align: center;">
                                {f'Best regards,<br>{sender_name}' if sender_name else 'Best regards'}
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html_template.strip()
    
    @staticmethod
    def format_simple_html(plain_text: str) -> str:
        """
        Simple HTML formatting (minimal styling)
        
        Args:
            plain_text: Plain text email body
            
        Returns:
            Simple HTML formatted email
        """
        html_body = plain_text.replace('\n', '<br>')
        paragraphs = html_body.split('<br><br>')
        formatted_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para:
                formatted_paragraphs.append(f'<p>{para}</p>')
        
        return '\n'.join(formatted_paragraphs)

