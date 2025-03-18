from flask import Flask, request, jsonify, send_from_directory
from utils import generate_report
import os

app = Flask(__name__)

# Route to serve static files (e.g., generated audio)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# API endpoint to generate the news sentiment report
@app.route('/generate_report', methods=['POST'])
def generate_report_api():
    data = request.get_json()
    if not data or 'company' not in data:
        return jsonify({'error': 'Please provide a company name in JSON with key "company".'}), 400
    
    company_name = data['company']
    report = generate_report(company_name)
    return jsonify(report)

# A simple index route with instructions
@app.route('/')
def index():
    return (
        "News Summarization and Text-to-Speech API.<br>"
        "Use the POST /generate_report endpoint with JSON payload: { 'company': 'Tesla' }"
    )

if __name__ == '__main__':
    # Ensure the static directory exists for TTS audio files
    if not os.path.exists('static'):
        os.makedirs('static')
    # Run the Flask app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
