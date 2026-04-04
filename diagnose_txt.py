"""Diagnostic script to debug the exact TXT file processing issue."""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.document_parser import extract_text_from_txt, extract_text
import io

def diagnose_file(file_path: str):
    """Diagnose file processing issues."""
    print(f"\n{'='*60}")
    print(f"File Diagnostic Report")
    print(f"File: {file_path}")
    print(f"{'='*60}\n")
    
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # File info
    file_size = path.stat().st_size
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"📄 File extension: {path.suffix}")
    print(f"{'─'*60}")
    
    # Read raw content
    with open(file_path, 'rb') as f:
        raw_bytes = f.read()
    
    # Check if it's actually a text file
    print(f"\n📝 Content Analysis:")
    print(f"  - First 100 bytes: {raw_bytes[:100]}")
    print(f"  - Contains null bytes: {b'\\x00' in raw_bytes}")
    print(f"  - Looks like binary: {any(raw_bytes[i:i+2] == b'\\x00\\x00' for i in range(min(1000, len(raw_bytes)-1)))}")
    
    # Try different extraction methods
    print(f"\n{'─'*60}")
    print(f"Testing Extraction Methods:")
    print(f"{'─'*60}")
    
    # Method 1: Direct bytes
    print(f"\n1️⃣ Method 1: BytesIO")
    try:
        bio = io.BytesIO(raw_bytes)
        result = extract_text_from_txt(bio)
        success = "Error" not in result and "No text" not in result
        print(f"  Result: {'✅' if success else '❌'} {result[:100]}...")
        if success:
            print(f"  Extracted: {len(result)} chars, {len(result.split())} words")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    # Method 2: String
    print(f"\n2️⃣ Method 2: String decode")
    try:
        text = raw_bytes.decode('utf-8', errors='replace')
        print(f"  Decoded: {len(text)} chars")
        print(f"  First 100 chars: {text[:100]}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    # Method 3: Using router
    print(f"\n3️⃣ Method 3: extract_text router")
    try:
        bio = io.BytesIO(raw_bytes)
        result = extract_text(bio, path.name)
        success = "Error" not in result and "No text" not in result
        print(f"  Result: {'✅' if success else '❌'} {result[:100]}...")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    # Try to find the file
    search_patterns = [
        "AD23421*DATA*ANALYTICS*.txt",
        "AD23421*.txt",
        "*DATA*ANALYTICS*.txt",
        "*.txt"
    ]
    
    file_path = None
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        import glob
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            if matches:
                file_path = matches[0]
                break
    
    if not file_path:
        print("❌ No TXT file found")
        print("Usage: python diagnose_txt.py <file_path>")
        sys.exit(1)
    
    diagnose_file(file_path)
