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
    
    # Remove trailing dots and spaces (Windows doesn't allow these)
    text = text.rstrip('._')
    
    # Ensure we still have a valid filename after stripping
    if not text or len(text) == 0:
        return 'unnamed'
    
    # Windows reserved names that cannot be used
    reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                     'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                     'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
    
    if text.upper() in reserved_names:
        text = f'_{text}'
    
    return text


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