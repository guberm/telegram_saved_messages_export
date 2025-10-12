"""
Utility functions for Telegram export
"""

import re


def sanitize_filename(text, max_length=50):
    """Create a safe filename from text."""
    if not text:
        return 'unnamed'
    
    # Remove or replace invalid characters including newlines and tabs
    invalid_chars = '<>:"/\\|?*\n\r\t'
    for char in invalid_chars:
        text = text.replace(char, '_')
    
    # Replace emojis and special characters that might cause issues
    # Remove emojis and special unicode characters
    text = re.sub(r'[^\w\s\-_.]', '_', text)
    
    # Limit length and strip whitespace
    text = text[:max_length].strip()
    
    # Replace multiple spaces/underscores with single underscore
    while '  ' in text:
        text = text.replace('  ', ' ')
    while '__' in text:
        text = text.replace('__', '_')
    
    # Replace spaces with underscores for filename safety
    text = text.replace(' ', '_')
    
    return text if text else 'unnamed'


def process_telegram_formatting(text):
    """Process Telegram formatting like **bold**, `code`, etc."""
    if not text:
        return ""
    
    import html
    # Escape HTML first
    text = html.escape(text)
    
    # Process bold text **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<span class="bold">\1</span>', text)
    
    # Process code `text`
    text = re.sub(r'`([^`]+)`', r'<span class="code">\1</span>', text)
    
    # Process code blocks ```text```
    text = re.sub(r'```(.*?)```', r'<div class="code-block">\1</div>', text, flags=re.DOTALL)
    
    # Process links (simple http/https detection)
    text = re.sub(r'(https?://[^\s]+)', r'<a href="\1" class="message-link" target="_blank">\1</a>', text)
    
    return text