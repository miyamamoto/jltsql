#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze the encoding issue with JV-Link data."""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Simulate what happens with Shift-JIS data through pywin32
print("=== Shift-JIS Encoding Analysis ===")
print()

# Example: The horse name "エルデュクラージュ" in Shift-JIS
# This is a hypothetical reconstruction
horse_name = "エルデュクラージュ"
sjis_bytes = horse_name.encode('cp932')
print(f"Original: {horse_name}")
print(f"Shift-JIS bytes: {sjis_bytes.hex()}")

# What happens if pywin32 treats BSTR as UTF-16-LE (which it does)
# Each pair of bytes is treated as a UTF-16 code unit
print()
print("=== If pywin32 decodes as UTF-16-LE ===")
try:
    decoded_utf16 = sjis_bytes.decode('utf-16-le', errors='replace')
    print(f"UTF-16-LE decode: {repr(decoded_utf16)}")
    # Then encoding back to latin-1 would fail for most chars
    try:
        re_encoded = decoded_utf16.encode('latin-1', errors='replace')
        print(f"Re-encoded latin-1: {re_encoded.hex()}")
    except:
        print("Cannot encode back to latin-1")
except Exception as e:
    print(f"Error: {e}")

# What SHOULD happen: Each byte is a separate code point
print()
print("=== Correct approach: Each byte as separate code point ===")
correct_str = ''.join(chr(b) for b in sjis_bytes)
print(f"Each byte as code point: {repr(correct_str)}")
recovered = correct_str.encode('latin-1')
print(f"Recovered bytes: {recovered.hex()}")
decoded = recovered.decode('cp932')
print(f"Final decoded: {decoded}")

# Check if the problem is odd-byte Shift-JIS sequences
print()
print("=== Byte-by-byte analysis ===")
print("Shift-JIS bytes:", end=" ")
for i, b in enumerate(sjis_bytes):
    print(f"{b:02x}", end=" ")
print()

# Check for high bytes that might cause issues
print("Bytes > 0x7F (need multi-byte handling):", end=" ")
high_bytes = [f"{i}:{b:02x}" for i, b in enumerate(sjis_bytes) if b > 0x7f]
print(high_bytes)
