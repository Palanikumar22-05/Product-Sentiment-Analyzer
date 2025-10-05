# Product Sentiment Analyzer

**Product Sentiment Analyzer** is a web application that scrapes product reviews from **Amazon** and **Flipkart**, analyzes their sentiment using **TextBlob**, and visualizes the results in a **React** dashboard with pie charts.  

This project is intended for educational purposes and personal use. It is **not meant for commercial use** or violating any website’s Terms of Service.

---

## Features

- Scrapes product reviews from Amazon and Flipkart.
- Performs sentiment analysis (positive, neutral, negative).
- Displays overall recommendation based on review sentiment.
- Frontend dashboard using React and Chart.js.
- Caches scraped data locally or via MongoDB to reduce repeated requests.

---

## Installation

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# or
source venv/bin/activate   # Linux / Mac

pip install -r requirements.txt
python app.py
