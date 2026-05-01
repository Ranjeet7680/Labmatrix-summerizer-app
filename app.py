from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import fitz  # PyMuPDF
import os
import io
import re
from summarizer import TextSummarizer

app = Flask(__name__)
CORS(app)

# Initialize summarizer (uses HF API — no local model download)
summarizer = TextSummarizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    try:
        data = request.json
        text = data.get('text', '')
        length = data.get('length', 'medium')  # short, medium, long

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        summary = summarizer.summarize(text, length)

        return jsonify({
            'success': True,
            'summary': summary,
            'original_length': len(text.split()),
            'summary_length': len(summary.split())
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files allowed'}), 400

        # Check file size (max 10MB)
        file_data = file.read()
        if len(file_data) > 10 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'File too large (max 10MB)'}), 400

        # Extract text from PDF in-memory (no disk write — Vercel compatible)
        text = extract_text_from_pdf_bytes(file_data)

        if not text or len(text.strip()) == 0:
            return jsonify({'success': False, 'error': 'No text found in PDF. It might be an image-based PDF.'}), 400

        return jsonify({
            'success': True,
            'text': text,
            'word_count': len(text.split())
        })

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return jsonify({'success': False, 'error': f'Error processing PDF: {str(e)}'}), 500


def extract_text_from_pdf_bytes(pdf_bytes):
    """Extract text from PDF bytes in-memory using PyMuPDF"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            text += page_text + "\n\n"

        doc.close()

        # Clean up text
        text = text.strip()
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)

        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


if __name__ == '__main__':
    print("🚀 SmartSummarizer AI is starting...")
    print("📍 Open: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
