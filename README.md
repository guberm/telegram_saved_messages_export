# Telegram Saved Messages Exporter

Export your Telegram saved messages to individual HTML and Markdown files with date filtering options.

## Features

- ✅ Export all saved messages or filter by date
- ✅ Each message saved as both HTML and Markdown
- ✅ Preserves message metadata (date, forwarding info)
- ✅ Handles media information and captions
- ✅ Beautiful HTML formatting with CSS styling
- ✅ Safe filename generation

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install telethon
```

### 2. Get Telegram API Credentials

1. Go to https://my.telegram.org/auth
2. Log in with your phone number
3. Navigate to **"API development tools"**
4. Create a new application (if you haven't already)
5. You'll receive:
   - `api_id` (a number)
   - `api_hash` (a string)

### 3. Configure the Script

Open `telegram_export.py` and edit these lines:

```python
API_ID = 'YOUR_API_ID'          # Replace with your api_id
API_HASH = 'YOUR_API_HASH'      # Replace with your api_hash
PHONE = 'YOUR_PHONE_NUMBER'     # Replace with your phone (e.g., +1234567890)
```

### 4. First Run Authentication

The first time you run the script, Telegram will send you a verification code. Enter it when prompted.

## Usage

### Export All Saved Messages

```bash
python telegram_export.py --all
```

### Export Messages from a Specific Date

```bash
python telegram_export.py --from-date 2024-01-01
```

This will export all messages from January 1, 2024 onwards.

### Custom Output Directory

```bash
python telegram_export.py --all --output my_exports
```

Default output directory is `telegram_exports/`.

## Output Format

Each message is exported as two files:

### Filename Format
```
YYYYMMDD_HHMMSS_msgID_preview.html
YYYYMMDD_HHMMSS_msgID_preview.md
```

Example:
```
20241011_143052_msg12345_Hello_world.html
20241011_143052_msg12345_Hello_world.md
```

### HTML Files
- Beautiful, responsive design
- Styled with CSS
- Includes metadata, forward info, and media details
- Opens directly in any browser

### Markdown Files
- Clean, readable format
- Compatible with any Markdown editor
- Includes all message metadata
- Easy to import into other systems

## Examples

```bash
# Export everything
python telegram_export.py --all

# Export messages from June 2024 onwards
python telegram_export.py --from-date 2024-06-01

# Export recent messages (last month)
python telegram_export.py --from-date 2024-09-11

# Save to a different folder
python telegram_export.py --all --output backup_2024
```

## What Gets Exported

✅ Message text
✅ Date and time
✅ Message ID
✅ Forward information (who forwarded, when)
✅ Media type (photos, videos, documents, etc.)
✅ Media captions
✅ Web page previews
✅ Links

## Notes

- **First run**: You'll need to enter a verification code sent by Telegram
- **Session file**: A `telegram_session.session` file will be created to store your authentication
- **Rate limits**: The script respects Telegram's rate limits
- **Privacy**: All data is processed locally on your computer
- **Media files**: Currently exports metadata only (not the actual media files)

## Troubleshooting

### "Please configure your API credentials first!"
- Make sure you've replaced `YOUR_API_ID`, `YOUR_API_HASH`, and `YOUR_PHONE_NUMBER` in the script

### "Invalid date format"
- Use the format `YYYY-MM-DD` for dates (e.g., `2024-01-15`)

### "Could not connect to Telegram"
- Check your internet connection
- Verify your API credentials are correct
- Make sure your phone number includes the country code (e.g., `+1234567890`)

### Permission Errors
- Make sure you have write permissions in the output directory
- Try running with a different output folder using `--output`

## Security

- Keep your `api_id` and `api_hash` private
- Don't share your `telegram_session.session` file
- The session file contains your authentication token

## License

Free to use and modify for personal use.
