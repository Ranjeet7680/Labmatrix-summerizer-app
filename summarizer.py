import requests
import os
import warnings
import re

warnings.filterwarnings('ignore')

HF_API_KEY = os.environ.get("HF_API_KEY", "")
HF_API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"

class TextSummarizer:
    def __init__(self):
        print("🧠 Using Hugging Face Inference API for summarization...")
        self.headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

    def summarize(self, text, length='medium'):
        if not text or len(text.strip()) == 0:
            return "No text to summarize."

        words = text.split()
        word_count = len(words)

        if word_count < 50:
            return text

        # Length params
        length_params = {
            'short':  {'max_length': min(100, word_count // 4), 'min_length': min(30, word_count // 8)},
            'medium': {'max_length': min(200, word_count // 3), 'min_length': min(50, word_count // 6)},
            'long':   {'max_length': min(400, word_count // 2), 'min_length': min(100, word_count // 4)},
        }
        params = length_params.get(length, length_params['medium'])

        # Chunk if too long (HF model max ~1024 chars)
        max_chunk = 900
        chunks = self._chunk_text(text, max_chunk)
        summaries = []

        for chunk in chunks:
            try:
                if HF_API_KEY:
                    # Use Hugging Face Inference API
                    payload = {
                        "inputs": chunk,
                        "parameters": {
                            "max_length": params['max_length'] // max(len(chunks), 1),
                            "min_length": params['min_length'] // max(len(chunks), 1),
                            "do_sample": False
                        }
                    }
                    response = requests.post(HF_API_URL, headers=self.headers, json=payload, timeout=30)
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        summaries.append(result[0].get('summary_text', ''))
                    elif isinstance(result, dict) and 'error' in result:
                        # Fallback: extractive summary
                        summaries.append(self._extractive_summary(chunk, params['max_length']))
                    else:
                        summaries.append(self._extractive_summary(chunk, params['max_length']))
                else:
                    # No API key — use simple extractive summarization
                    summaries.append(self._extractive_summary(chunk, params['max_length']))
            except Exception as e:
                print(f"Error: {e}")
                summaries.append(self._extractive_summary(chunk, params['max_length']))

        return ' '.join(filter(None, summaries))

    def _extractive_summary(self, text, max_words=150):
        """Simple extractive summarizer — no ML needed"""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if not sentences:
            return text
        # Score sentences by position and length
        scored = []
        for i, sent in enumerate(sentences):
            words = len(sent.split())
            if words < 5:
                continue
            score = 1.0 / (i + 1) + min(words, 30) / 30.0
            scored.append((score, sent))
        scored.sort(reverse=True)
        
        result = []
        word_total = 0
        for _, sent in scored:
            words = sent.split()
            if word_total + len(words) > max_words:
                break
            result.append(sent)
            word_total += len(words)
        
        # Restore original order
        result_set = set(result)
        ordered = [s for s in sentences if s in result_set]
        return ' '.join(ordered) if ordered else sentences[0]

    def _chunk_text(self, text, max_chars):
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        chunks = []
        current = []
        current_len = 0
        for sent in sentences:
            if current_len + len(sent) > max_chars and current:
                chunks.append(' '.join(current))
                current = [sent]
                current_len = len(sent)
            else:
                current.append(sent)
                current_len += len(sent) + 1
        if current:
            chunks.append(' '.join(current))
        return chunks or [text]
