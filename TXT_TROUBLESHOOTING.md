# 📝 TXT File Processing Troubleshooting Guide

## Common Issues & Solutions

### Issue: "Failed to process [filename].txt"

---

## 🔍 Step 1: Click "View error details"

When you see the error, click the **"🔍 View error details"** expandable section. This will show you the **exact error message**.

---

## 🔧 Step 2: Match Your Error to These Solutions

### Error: "Error extracting text from TXT: ..."

**Cause:** File reading or encoding issue

**Solutions:**

1. **Verify the file is actually a text file**
   - Open it in Notepad (Windows) or any text editor
   - If it opens and you can read the text → Good
   - If it shows garbled characters → It's not a real TXT file

2. **Check file isn't empty**
   - Open the file
   - Make sure there's actual text content
   - File size should be > 0 bytes

3. **Check file encoding**
   - Open in Notepad
   - File → Save As
   - Change encoding to **UTF-8**
   - Save and try uploading again

4. **Remove special characters**
   - Remove any weird symbols or formatting
   - Keep it plain text only

---

### Error: "No text could be extracted from the TXT file"

**Cause:** File is empty or only contains whitespace

**Solutions:**

1. **Add content to the file**
   - Open in Notepad
   - Add some text
   - Save and upload again

2. **Check for hidden formatting**
   - Select all text (Ctrl+A)
   - Copy (Ctrl+C)
   - Paste into a new Notepad file
   - Save with a new name
   - Try uploading the new file

---

### Error: "Unexpected file type for TXT extraction"

**Cause:** Streamlit is passing the file in an unexpected format

**Solutions:**

1. **Try a different browser**
   - Sometimes browser file handling varies

2. **Rename the file**
   - Change extension from `.TXT` to `.txt` (lowercase)
   - Remove spaces/special chars from filename
   - Example: `AD23421_DATA_ANALYTICS_LAB_MANUAL.txt`

3. **Create a fresh copy**
   - Open original file
   - Select all text (Ctrl+A)
   - Copy (Ctrl+C)
   - Open Notepad
   - Paste (Ctrl+V)
   - Save as new file with simple name
   - Upload the new file

---

## ✅ Step 3: Quick Test

Create a simple test file:

1. Open Notepad
2. Type: `Hello, this is a test document.`
3. Save as: `test.txt`
4. Upload to the app

**If this works:** Your original file has formatting/encoding issues
**If this fails:** There's an app configuration issue

---

## 🎯 For Your Specific File: "AD23421 _DATA ANALYTICS LAB MANUAL.txt"

### Recommended Steps:

1. **Open the file in Notepad**
   ```
   Right-click file → Open with → Notepad
   ```

2. **Check if you can read the content**
   - ✅ If YES → Content is good, might be encoding issue
   - ❌ If NO (garbled text) → Need to re-export/convert

3. **Re-save with UTF-8 encoding**
   ```
   Notepad → File → Save As
   - Encoding: UTF-8
   - File name: ad23421_data_analytics_manual.txt
   - Click Save
   ```

4. **Try uploading the new file**

---

## 🔄 Alternative: Convert from Source

If the TXT file was converted from a PDF or Word doc:

### From PDF:
- Use [iLovePDF](https://www.ilovepdf.com/pdf_to_text)
- Upload PDF → Convert to TXT → Download
- Upload the new TXT file

### From Word/DOCX:
- Open in Word
- File → Save As
- Choose "Plain Text (.txt)"
- Upload the TXT file

---

## 📊 File Requirements

| Property | Requirement |
|----------|-------------|
| **Extension** | `.txt` (lowercase) |
| **Size** | > 0 bytes, < 10 MB |
| **Encoding** | UTF-8 or Latin-1 |
| **Content** | Plain text only |
| **Format** | No special formatting |

---

## 🐛 Still Not Working?

### Enable Debug Logging

Run the app with debug output:

```bash
cd D:\dev\st_point\Document-Query-Assistant
uv run streamlit run app.py
```

Then check the terminal/console output when you upload. You should see:
```
INFO - Processing file: test.txt, size: 1,234 bytes
INFO - Successfully extracted 1,234 characters from TXT
```

Or an error message with details.

### Share the Error Message

If it still fails:
1. Click "🔍 View error details"
2. Copy the exact error message
3. Check what it says
4. The error message will tell you exactly what's wrong

---

## 💡 Pro Tips

1. **Keep filenames simple**
   - Use lowercase
   - Replace spaces with underscores
   - No special characters
   - Example: `lab_manual.txt`

2. **Always use UTF-8 encoding**
   - Most compatible
   - Supports all characters
   - Standard for web apps

3. **Test with small files first**
   - Create a simple 10-word TXT file
   - Upload to verify the app works
   - Then try your actual file

---

**Good luck! The improved error messages should now tell you exactly what's wrong.** 🎉
