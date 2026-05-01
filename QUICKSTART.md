# 🚀 Quick Start Guide

## ⚠️ Important: First Time Setup

### Issue Fix Kiya Gaya:
✅ JAX dependency conflict resolved
✅ Lighter model (DistilBART) use kar rahe hain for faster loading

## 📦 Installation (Step-by-Step)

### 1. Dependencies Install Karein
```bash
pip install -r requirements.txt
```

### 2. App Run Karein
```bash
python app.py
```

**⏳ First Time**: Model download hoga (~300MB), 2-3 minutes lagenge
**⚡ Next Time**: Instantly start hoga (model cached rahega)

### 3. Browser Mein Open Karein
```
http://localhost:5000
```

## 🎯 Agar Model Load Nahi Ho Raha

### Option 1: Manual Model Download (Recommended)
```python
# Run this once to pre-download model
python -c "from transformers import pipeline; pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')"
```

### Option 2: Use Even Lighter Model
Edit `summarizer.py`, line 13:
```python
# Change to:
self.model = pipeline("summarization", model="t5-small")
```

### Option 3: Use Simple Extractive Summarization (No Download)
Create `summarizer_simple.py`:
```python
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from collections import Counter

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class TextSummarizer:
    def summarize(self, text, length='medium'):
        sentences = sent_tokenize(text)
        
        # Length mapping
        num_sentences = {
            'short': max(2, len(sentences) // 4),
            'medium': max(3, len(sentences) // 3),
            'long': max(5, len(sentences) // 2)
        }
        
        # Simple scoring based on word frequency
        words = text.lower().split()
        word_freq = Counter(words)
        
        # Score sentences
        sentence_scores = {}
        for sentence in sentences:
            for word in sentence.lower().split():
                if word in word_freq:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_freq[word]
                    else:
                        sentence_scores[sentence] += word_freq[word]
        
        # Get top sentences
        top_sentences = sorted(sentence_scores.items(), 
                              key=lambda x: x[1], 
                              reverse=True)[:num_sentences[length]]
        
        # Return in original order
        summary = ' '.join([s[0] for s in top_sentences])
        return summary
```

Then in `app.py`, change import:
```python
from summarizer_simple import TextSummarizer  # Instead of from summarizer
```

## 🔧 Troubleshooting

### Error: "Failed to import transformers"
```bash
pip uninstall jax jaxlib -y
pip install ml_dtypes==0.2.0
```

### Error: "Out of Memory"
Use lighter model or simple extractive summarizer (Option 3 above)

### Error: "Connection timeout"
Check internet connection (model download ke liye)

## 📊 Model Comparison

| Model | Size | Speed | Quality | Download |
|-------|------|-------|---------|----------|
| t5-small | 60MB | ⚡⚡⚡ | ⭐⭐ | Fast |
| distilbart-cnn-12-6 | 300MB | ⚡⚡ | ⭐⭐⭐ | Medium |
| bart-large-cnn | 1.6GB | ⚡ | ⭐⭐⭐⭐ | Slow |
| Simple Extractive | 0MB | ⚡⚡⚡⚡ | ⭐ | None |

## ✅ Verification

App successfully start hone par ye dikhega:
```
🧠 Loading summarization model...
✅ Model loaded successfully!
🚀 SmartSummarizer AI is starting...
📍 Open: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

## 🎉 Ready to Use!

1. Open browser: `http://localhost:5000`
2. Upload PDF ya text paste karein
3. Summary length select karein
4. Click "Summarize"
5. Done! 🎯

---

**Need Help?** Check README.md for detailed documentation
