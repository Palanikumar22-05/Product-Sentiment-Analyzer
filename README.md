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
Frontend
cd frontend
npm install
npm start


The frontend runs on http://localhost:3000 by default.

The backend runs on http://127.0.0.1:5000.

Usage

Enter a product name in the search box.

Fetch reviews from Amazon, Flipkart, or both.

View sentiment analysis and recommendation summary.

Check the pie chart for overall sentiment distribution.

Notes / Legal

Respect Website Terms: This project scrapes data for personal or educational use only. Users must comply with the Terms of Service of Amazon and Flipkart.

No commercial usage: Do not use this project to mass scrape or sell data.

Responsible usage: Use the project responsibly and avoid making too many automated requests.

pip install -r requirements.txt
python app.py
