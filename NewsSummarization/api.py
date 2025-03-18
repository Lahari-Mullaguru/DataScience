from flask import Flask, request, jsonify, send_from_directory
from utils import process_company_news
import os

app = Flask(__name__)

# Serve static files (audio)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Endpoint to fetch news for a company
@app.route('/fetch_news', methods=['POST'])
def fetch_news_endpoint():
    data = request.json
    company_name = data.get('company')
    
    if not company_name:
        return jsonify({"error": "Company name is required"}), 400
    
    try:
        result = process_company_news(company_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True)
