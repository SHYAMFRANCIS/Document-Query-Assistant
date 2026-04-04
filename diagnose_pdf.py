"""Diagnostic script to test PDF processing."""

import sys
from pathlib import Path

import PyPDF2


def diagnose_pdf(file_path: str):
    """Diagnose PDF processing issues."""
    print(f"\n{'='*60}")
    print("PDF Diagnostic Report")
    print(f"File: {file_path}")
    print(f"{'='*60}\n")

    # Check if file exists
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return

    # Check file size
    file_size = path.stat().st_size
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")

    # Check file extension
    if not file_path.lower().endswith('.pdf'):
        print("❌ File extension is not .pdf")
        return

    print("✅ File extension: .pdf")

    # Try to read file
    try:
        with open(file_path, 'rb') as f:
            # Check PDF header
            header = f.read(5)
            if header.startswith(b'%PDF'):
                print(f"✅ Valid PDF header: {header.decode('ascii', errors='ignore')}")
            else:
                print(f"❌ Invalid PDF header: {header}")
                return

            # Try to read with PyPDF2
            f.seek(0)
            try:
                pdf_reader = PyPDF2.PdfReader(f)
                print("✅ PyPDF2 can read the file")

                # Check if encrypted
                if pdf_reader.is_encrypted:
                    print("❌ PDF is ENCRYPTED - requires password")
                    print("   Solution: Remove password protection and try again")
                    return

                # Get page count
                num_pages = len(pdf_reader.pages)
                print(f"📄 Number of pages: {num_pages}")

                # Try to extract text from each page
                print(f"\n{'─'*60}")
                print("Text Extraction Results:")
                print(f"{'─'*60}")

                total_text = ""
                successful_pages = 0
                failed_pages = []
                empty_pages = []

                for i in range(min(num_pages, 10)):  # Test first 10 pages
                    try:
                        page = pdf_reader.pages[i]
                        text = page.extract_text()

                        if text and text.strip():
                            total_text += text + "\n"
                            successful_pages += 1
                            if i < 3:  # Show preview of first 3 pages
                                preview = text[:100].replace('\n', ' ')
                                print(f"✅ Page {i+1}: {preview}...")
                        else:
                            empty_pages.append(i+1)
                            print(f"⚠️  Page {i+1}: No text extracted")

                    except Exception as e:
                        failed_pages.append((i+1, str(e)))
                        print(f"❌ Page {i+1}: Error - {str(e)[:50]}")

                # Summary
                print(f"\n{'='*60}")
                print("Summary:")
                print(f"{'='*60}")
                print(f"✅ Successful pages: {successful_pages}")
                print(f"⚠️  Empty pages: {len(empty_pages)} (pages: {empty_pages[:5]})")
                print(f"❌ Failed pages: {len(failed_pages)} (pages: {[p[0] for p in failed_pages[:5]]})")

                if total_text:
                    word_count = len(total_text.split())
                    char_count = len(total_text)
                    print("\n📊 Total text extracted:")
                    print(f"   - Words: {word_count:,}")
                    print(f"   - Characters: {char_count:,}")
                    print("\n✅ PDF can be processed successfully!")
                else:
                    print("\n❌ No text could be extracted")
                    print("\nPossible reasons:")
                    print("   1. PDF contains scanned images (no text layer)")
                    print("   2. PDF uses complex formatting/fonts")
                    print("   3. PDF is corrupted")
                    print("\nSolutions:")
                    print("   1. Use OCR software to extract text first")
                    print("   2. Convert PDF to TXT/DOCX format")
                    print("   3. Copy text manually and save as .txt file")

            except Exception as e:
                print("❌ PyPDF2 cannot read this PDF")
                print(f"   Error: {str(e)}")
                print("\nPossible reasons:")
                print("   1. PDF version is too new/old")
                print("   2. PDF is corrupted")
                print("   3. PDF uses unsupported features")

    except Exception as e:
        print(f"❌ Cannot read file: {str(e)}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        # Try to find the file in current directory
        import glob
        pdf_files = glob.glob("*DATA*ANALYTICS*.pdf")
        if pdf_files:
            pdf_file = pdf_files[0]
        else:
            pdf_files = glob.glob("*.pdf")
            if pdf_files:
                pdf_file = pdf_files[0]
            else:
                print("❌ No PDF file specified or found")
                sys.exit(1)

    diagnose_pdf(pdf_file)
