from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio
import json
import os

from stock_analyzer_gemini.main import analyze_stock

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv(override=True)

@app.route('/analyze_stock', methods=['get'])
def analyze_stock_endpoint():
    """Endpoint to clean up files created during the interview process."""
    result = analyze_stock('AAPL')
    try:
        with open('../../output/investment_advice.md', 'r', encoding='utf-8') as file:
            content = file.read()
        # Return content as JSON string with a key, for example "content"
        return jsonify({"analysis": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)