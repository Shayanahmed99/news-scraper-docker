import re
from flask import Flask, jsonify, request
from scraper import get_first_article
from summarizer import summarize

app = Flask(__name__)

REGISTRATION = "FA23-BDS-037"
NEWS_SOURCE = "Ars Technica"
PORT = 7000


@app.route("/", methods=["GET"])
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>News Scraper API</title></head>
    <body>
        <h1>News Scraper API</h1>
        <p>Registration Number: {REGISTRATION}</p>
        <p>News Source: {NEWS_SOURCE}</p>
        <p>API Port: {PORT}</p>
    </body>
    </html>
    """


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/get", methods=["GET"])
def get_news():
    keyword = request.args.get("keyword", "").strip()

    if not keyword:
        return jsonify({"error": "Please provide a keyword"}), 400

    try:
        article = get_first_article(keyword)
        article_summary = summarize(article["article_text"])

        return jsonify({
            "registration": REGISTRATION,
            "newssource": NEWS_SOURCE,
            "keyword": keyword,
            "url": article["url"],
            "summary": article_summary
        })

    except Exception:
        app.logger.exception("News scraping failed")
        return jsonify({
            "error": "Could not retrieve an article"
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
