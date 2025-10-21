# backend/app.py
import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob
from scraper import scrape_amazon, scrape_flipkart

# Optional: set MONGO_URI environment variable to use MongoDB caching.
# If not set, fallback to a local cache file: backend/cache.json

MONGO_URI = os.environ.get("MONGO_URI")
CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.json")

app = Flask(__name__)
CORS(app)

# --- simple cache helpers (Mongo if available, else local file) ---
use_mongo = False
mongo_client = None
db = None
if MONGO_URI:
    try:
        from pymongo import MongoClient
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # test connection
        mongo_client.server_info()
        db = mongo_client.get_database()
        use_mongo = True
        print("Using MongoDB for caching")
    except Exception as e:
        print("Warning: can't connect to MongoDB, falling back to file cache:", e)
        use_mongo = False


def read_cache_file():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def write_cache_file(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("cache write error:", e)


def cache_get(product_key, source_key):
    if use_mongo and db:
        coll = db.get_collection("product_cache")
        doc = coll.find_one({"product_key": product_key, "source": source_key})
        if doc:
            return doc.get("reviews", []), doc.get("last_scraped", 0)
        return [], 0
    else:
        data = read_cache_file()
        key = f"{product_key}||{source_key}"
        return data.get(key, {}).get("reviews", []), data.get(key, {}).get("last_scraped", 0)


def cache_set(product_key, source_key, reviews):
    now = int(time.time())
    if use_mongo and db:
        coll = db.get_collection("product_cache")
        coll.update_one(
            {"product_key": product_key, "source": source_key},
            {"$set": {"reviews": reviews, "last_scraped": now}},
            upsert=True
        )
    else:
        data = read_cache_file()
        key = f"{product_key}||{source_key}"
        data[key] = {"reviews": reviews, "last_scraped": now}
        write_cache_file(data)


# --- sentiment / recommendation helpers ---
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"


def get_overall_recommendation(reviews):
    pos = sum(1 for r in reviews if r["sentiment"] == "positive")
    neg = sum(1 for r in reviews if r["sentiment"] == "negative")
    neu = sum(1 for r in reviews if r["sentiment"] == "neutral")
    total = len(reviews) or 1

    pos_pct = (pos / total) * 100
    neg_pct = (neg / total) * 100
    neu_pct = (neu / total) * 100

    # business logic for recommendation
    if pos_pct >= 55:
        label = "positive"
        text = "👍 Recommended: Majority of reviews are positive."
    elif neg_pct >= 45:
        label = "negative"
        text = "⚠️ Not recommended: Significant negative feedback."
    else:
        label = "neutral"
        text = "ℹ️ Mixed: Reviews are mixed — consider carefully."

    return {
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "total": total,
        "positive_pct": round(pos_pct, 2),
        "neutral_pct": round(neu_pct, 2),
        "negative_pct": round(neg_pct, 2),
        "label": label,
        "recommendation_text": text
    }


# --- combined scrape that uses cache (valid for 12 hours by default) ---
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", 60 * 60 * 12))


def fetch_reviews_for(product, source):
    """
    Returns list of review texts (deduped) for given product and source.
    source: 'amazon' | 'flipkart' | 'both'
    """
    product_key = product.strip().lower()
    all_texts = []

    sources = []
    if source == "both":
        sources = ["amazon", "flipkart"]
    else:
        sources = [source]

    for s in sources:
        cached, last = cache_get(product_key, s)
        age = int(time.time()) - last
        if cached and age < CACHE_TTL_SECONDS:
            # use cached
            all_texts.extend(cached)
            continue

        # do real scrape
        try:
            if s == "amazon":
                scraped = scrape_amazon(product, limit=25)
            elif s == "flipkart":
                scraped = scrape_flipkart(product, limit=25)
            else:
                scraped = []
        except Exception as e:
            print(f"Scrape error for {s}:", e)
            scraped = []

        # store in cache (even if empty)
        cache_set(product_key, s, scraped)
        all_texts.extend(scraped)

    # dedupe preserving order
    seen = set()
    deduped = []
    for t in all_texts:
        if t and t not in seen:
            seen.add(t)
            deduped.append(t)

    return deduped


@app.route("/api/reviews", methods=["GET"])
def api_reviews():
    product = request.args.get("product", "").strip()
    source = request.args.get("source", "both").strip().lower()
    if not product:
        return jsonify({"error": "product param required"}), 400
    if source not in ("amazon", "flipkart", "both"):
        return jsonify({"error": "source must be amazon|flipkart|both"}), 400

    texts = fetch_reviews_for(product, source)

    # analyze sentiments
    reviews = []
    for t in texts:
        s = analyze_sentiment(t)
        reviews.append({"review": t, "sentiment": s})

    summary = get_overall_recommendation(reviews)

    return jsonify({"summary": summary, "reviews": reviews})


if __name__ == "__main__":
    app.run(debug=True)