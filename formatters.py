"""
HTML and Markdown formatters for Telegram messages
"""

import html
import re


def process_telegram_formatting(text):
    """Process Telegram formatting like **bold**, `code`, etc."""
    if not text:
        return ""
    
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


def message_to_markdown(message):
    """Convert a Telegram message to Markdown format."""
    md_content = []
    
    # Header with metadata
    md_content.append(f"# Message {message.id}\n")
    md_content.append(f"**Date:** {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if message.forward:
        if message.forward.from_name:
            md_content.append(f"**Forwarded from:** {message.forward.from_name}\n")
        md_content.append(f"**Originally sent:** {message.forward.date.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    md_content.append("\n---\n\n")
    
    # Message text
    if message.text:
        md_content.append(message.text)
        md_content.append("\n")
    
    # Media information
    if message.media:
        md_content.append(f"\n**Media Type:** {type(message.media).__name__}\n")
        
        if hasattr(message.media, 'caption') and message.media.caption:
            md_content.append(f"\n**Caption:** {message.media.caption}\n")
    
    # Web page preview
    if message.web_preview:
        md_content.append(f"\n**Link:** [{message.web_preview.title}]({message.web_preview.url})\n")
    
    return ''.join(md_content)


def message_to_html(message):
    """Convert a Telegram message to HTML format that matches Telegram's appearance."""
    html_parts = []
    
    # Start HTML document
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Message {}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .chat-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #1e2832;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .chat-header {{
            background: #2b5278;
            padding: 15px 20px;
            color: #ffffff;
            font-weight: 500;
            font-size: 16px;
            border-bottom: 1px solid #3d5980;
        }}
        .message-bubble {{
            background: #2f3c4c;
            margin: 12px 20px;
            padding: 12px 16px;
            border-radius: 12px;
            border-top-left-radius: 4px;
            position: relative;
            max-width: 85%;
        }}
        .message-content {{
            color: #ffffff;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .message-time {{
            color: #8596a8;
            font-size: 12px;
            margin-top: 8px;
            text-align: right;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .message-forward {{
            color: #64b5ef;
            font-size: 13px;
            margin-bottom: 8px;
            padding-left: 12px;
            border-left: 3px solid #64b5ef;
        }}
        .message-media {{
            margin-top: 8px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            font-size: 12px;
            color: #8596a8;
        }}
        .message-link {{
            color: #64b5ef;
            text-decoration: none;
            border-bottom: 1px solid rgba(100, 181, 239, 0.3);
        }}
        .message-link:hover {{
            border-bottom-color: #64b5ef;
        }}
        .bold {{
            font-weight: 600;
        }}
        .code {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .code-block {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 8px 0;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            Saved Messages
        </div>
        <div class="message-bubble">
""".format(message.id))
    
    # Forward information
    if message.forward:
        html_parts.append('            <div class="message-forward">\n')
        if message.forward.from_name:
            html_parts.append(f'                Forwarded from {html.escape(message.forward.from_name)}\n')
        else:
            html_parts.append('                Forwarded message\n')
        html_parts.append('            </div>\n')
    
    # Message content with Telegram formatting
    if message.text:
        # Process Telegram formatting
        formatted_text = process_telegram_formatting(message.text)
        html_parts.append('            <div class="message-content">\n')
        html_parts.append(f'                {formatted_text}\n')
        html_parts.append('            </div>\n')
    
    # Media information
    if message.media:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                📎 {html.escape(type(message.media).__name__)}\n')
        
        if hasattr(message.media, 'caption') and message.media.caption:
            caption_formatted = process_telegram_formatting(message.media.caption)
            html_parts.append(f'<br>                {caption_formatted}\n')
        
        html_parts.append('            </div>\n')
    
    # Web page preview
    if message.web_preview:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                🔗 <a href="{html.escape(message.web_preview.url)}" class="message-link" target="_blank">{html.escape(message.web_preview.title or message.web_preview.url)}</a>\n')
        html_parts.append('            </div>\n')
    
    # Message time and link
    html_parts.append('            <div class="message-time">\n')
    # Add link to original message in Telegram
    telegram_link = f'tg://openmessage?user_id=me&message_id={message.id}'
    html_parts.append(f'                <a href="{telegram_link}" class="message-link" style="font-size: 11px; opacity: 0.7;">🔗</a>\n')
    html_parts.append(f'                <span>{html.escape(message.date.strftime("%H:%M"))}</span>\n')
    html_parts.append('            </div>\n')
    
    # Close HTML
    html_parts.append("""        </div>
    </div>
</body>
</html>""")
    
    return ''.join(html_parts)


async def message_to_html_with_media(message, media_filename):
    """Convert a Telegram message to HTML format with media support."""
    html_parts = []
    
    # Start HTML document (same as before)
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Message {}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .chat-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #1e2832;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .chat-header {{
            background: #2b5278;
            padding: 15px 20px;
            color: #ffffff;
            font-weight: 500;
            font-size: 16px;
            border-bottom: 1px solid #3d5980;
        }}
        .message-bubble {{
            background: #2f3c4c;
            margin: 12px 20px;
            padding: 12px 16px;
            border-radius: 12px;
            border-top-left-radius: 4px;
            position: relative;
            max-width: 85%;
        }}
        .message-content {{
            color: #ffffff;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .message-time {{
            color: #8596a8;
            font-size: 12px;
            margin-top: 8px;
            text-align: right;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .message-forward {{
            color: #64b5ef;
            font-size: 13px;
            margin-bottom: 8px;
            padding-left: 12px;
            border-left: 3px solid #64b5ef;
        }}
        .message-media {{
            margin-top: 8px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            font-size: 12px;
            color: #8596a8;
        }}
        .message-image {{
            margin-top: 8px;
            border-radius: 8px;
            overflow: hidden;
        }}
        .message-image img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .message-link {{
            color: #64b5ef;
            text-decoration: none;
            border-bottom: 1px solid rgba(100, 181, 239, 0.3);
        }}
        .message-link:hover {{
            border-bottom-color: #64b5ef;
        }}
        .bold {{
            font-weight: 600;
        }}
        .code {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .code-block {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 8px 0;
            overflow-x: auto;
        }}
        .post-link {{
            background: rgba(100, 181, 239, 0.1);
            border: 1px solid rgba(100, 181, 239, 0.3);
            border-radius: 8px;
            padding: 8px;
            margin-top: 8px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            Saved Messages
        </div>
        <div class="message-bubble">
""".format(message.id))
    
    # Forward information
    if message.forward:
        html_parts.append('            <div class="message-forward">\n')
        if message.forward.from_name:
            html_parts.append(f'                Forwarded from {html.escape(message.forward.from_name)}\n')
        else:
            html_parts.append('                Forwarded message\n')
        html_parts.append('            </div>\n')
    
    # Message content with Telegram formatting
    if message.text:
        # Process Telegram formatting
        formatted_text = process_telegram_formatting(message.text)
        html_parts.append('            <div class="message-content">\n')
        html_parts.append(f'                {formatted_text}\n')
        html_parts.append('            </div>\n')
    
    # Media (images, videos, etc.)
    if media_filename:
        html_parts.append('            <div class="message-image">\n')
        html_parts.append(f'                <img src="{media_filename}" alt="Message media" loading="lazy">\n')
        html_parts.append('            </div>\n')
    elif message.media:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                📎 {html.escape(type(message.media).__name__)}\n')
        
        if hasattr(message.media, 'caption') and message.media.caption:
            caption_formatted = process_telegram_formatting(message.media.caption)
            html_parts.append(f'<br>                {caption_formatted}\n')
        
        html_parts.append('            </div>\n')
    
    # Web page preview
    if message.web_preview:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                🔗 <a href="{html.escape(message.web_preview.url)}" class="message-link" target="_blank">{html.escape(message.web_preview.title or message.web_preview.url)}</a>\n')
        html_parts.append('            </div>\n')
    
    # Add original post link if it's forwarded from a public channel
    if message.forward and hasattr(message.forward, 'from_id') and message.forward.from_id:
        try:
            # Try to create a public link for channels/groups
            if hasattr(message.forward.from_id, 'channel_id'):
                channel_id = message.forward.from_id.channel_id
                post_id = getattr(message.forward, 'channel_post', message.id)
                # This is a simplified approach - in reality you'd need to know the channel username
                html_parts.append('            <div class="post-link">\n')
                html_parts.append(f'                🔗 <a href="https://t.me/c/{channel_id}/{post_id}" class="message-link" target="_blank">View original post</a>\n')
                html_parts.append('            </div>\n')
        except:
            pass
    
    # Message time and link
    html_parts.append('            <div class="message-time">\n')
    # Add link to original message in Telegram (works in Telegram apps)
    telegram_link = f'tg://openmessage?user_id=me&message_id={message.id}'
    html_parts.append(f'                <a href="{telegram_link}" class="message-link" style="font-size: 11px; opacity: 0.7;">📱</a>\n')
    html_parts.append(f'                <span>{html.escape(message.date.strftime("%H:%M"))}</span>\n')
    html_parts.append('            </div>\n')
    
    # Close HTML
    html_parts.append("""        </div>
    </div>
</body>
</html>""")
    
    return ''.join(html_parts)