"""Test script to debug TXT file processing."""

import io

from services.document_parser import extract_text, extract_text_from_txt

# Test 1: Simulate Streamlit's BytesIO upload
print("Test 1: BytesIO object (simulating Streamlit upload)")
test_content = b"Hello, this is a test document.\nWith multiple lines.\nLine 3 here."
test_file = io.BytesIO(test_content)
result = extract_text_from_txt(test_file)
print(f"Result: {result[:100]}...")
print(f"Success: {'Error' not in result}\n")

# Test 2: String content
print("Test 2: StringIO object")
test_file2 = io.StringIO("Hello world\nTest content")
try:
    result2 = extract_text_from_txt(test_file2)
    print(f"Result: {result2}")
except Exception as e:
    print(f"Error: {e}\n")

# Test 3: Test the router function
print("\nTest 3: Using extract_text router with .txt file")
test_file3 = io.BytesIO(b"Router test content\nLine 2")
result3 = extract_text(test_file3, "test.txt")
print(f"Result: {result3}")
print(f"Success: {'Error' not in result3}")

print("\n✅ All tests completed")
