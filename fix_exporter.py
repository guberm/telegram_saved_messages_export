#!/usr/bin/env python3
"""Fix exporter.py by removing duplicate code"""

with open('exporter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep lines 1-256 and lines 297-end
new_lines = lines[:256] + lines[296:]

with open('exporter.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✓ Fixed exporter.py")
print(f"  Removed lines 257-296 (duplicate code)")
print(f"  Old: {len(lines)} lines")
print(f"  New: {len(new_lines)} lines")
