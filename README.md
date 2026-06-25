# sentiment-lens-analysis
# 🔍 Sentiment Lens

A sentiment analysis web app built with **Python**, **Streamlit**, and **TextBlob**.

## ✨ Features

- Detects **Positive / Negative / Neutral** sentiment
- Shows **Polarity** (–1 to +1) and **Subjectivity** (0 to 1) scores
- **Sentence-level breakdown** for multi-sentence input
- **Word-level polarity chips** — each word colour-coded
- One-click **example sentences** to demo the app
- **Session history** of past analyses

## 🛠 Tech Stack

| Layer | Tool |
|-------|------|
| UI | Streamlit |
| NLP | TextBlob + NLTK |
| Language | Python 3.11 |

## 🚀 Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/sentiment-lens.git
cd sentiment-lens
pip install -r requirements.txt
python -m textblob.download_corpora
streamlit run app.py
```

## 🌐 Live Demo

[Click here to try it →](https://YOUR_APP.streamlit.app)

## 📸 Screenshot

<!-- Add a screenshot after deploying -->

## 📄 License

MIT
