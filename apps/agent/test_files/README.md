# OCR Test Files

This directory contains test files for the OCR Agent functionality.

## Files Description

### Images

- **`test_lab.png`** - Sample laboratory results image with medical data
- **`simple_test.png`** - Simple test image for basic OCR functionality

### PDFs

- **`test_lab.pdf`** - Sample laboratory results PDF with medical data

### Text Files

- **`test_lab.txt`** - Source text used to generate the test_lab.pdf
- **`small_test.txt`** - Small text file for testing

## Usage

These files can be used to test the OCR Agent functionality:

```bash
# Test with PNG image
curl -X POST http://localhost:3000/chat/ocr \
  -H "Authorization: Bearer test-token" \
  -F "file=@test_files/test_lab.png"

# Test with PDF
curl -X POST http://localhost:3000/chat/ocr \
  -H "Authorization: Bearer test-token" \
  -F "file=@test_files/test_lab.pdf"
```

## Expected Results

The OCR Agent should:

1. Extract text from the uploaded files
2. Analyze the medical content using GPT-4
3. Return structured analysis in Portuguese
4. Provide recommendations and alerts if needed

## File Types Supported

- **Images**: PNG, JPG, JPEG
- **Documents**: PDF
- **Maximum size**: 10MB
