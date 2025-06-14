from flask import Flask, jsonify
from scraper_utils import scrape_url

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    url = "https://help.gohighlevel.com/support/home"
    content = scrape_url(url)
    return jsonify({"content": content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)