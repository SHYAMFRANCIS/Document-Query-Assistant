"""Simple test to verify TXT extraction works."""

import io
from services.document_parser import extract_text_from_txt, extract_text

# Test 1: Simple string content
print("Test 1: StringIO with simple text")
test1 = io.StringIO("Hello world\nThis is a test document.\nLine 3.")
try:
    result1 = extract_text_from_txt(test1)
    print(f"✅ Success: {result1[:50]}...\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 2: Bytes content
print("Test 2: BytesIO with UTF-8 text")
test2 = io.BytesIO(b"Hello world\nThis is a test document.\nLine 3.")
try:
    result2 = extract_text_from_txt(test2)
    print(f"✅ Success: {result2[:50]}...\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 3: Router with .txt extension
print("Test 3: extract_text router with .txt file")
test3 = io.BytesIO(b"Router test content\nLine 2\nLine 3")
try:
    result3 = extract_text(test3, "test.txt")
    print(f"✅ Success: {result3[:50]}...\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

print("✅ All manual tests completed")
