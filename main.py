from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "API activa."

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        [s.decompose() for s in soup(["script", "style", "noscript"])]
        text = soup.get_text(separator=' ', strip=True)
        return jsonify({"text": text[:10000]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500