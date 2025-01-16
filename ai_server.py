import os
import requests
from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv  # Import dotenv
from datetime import datetime, timedelta
from flask_cors import CORS
import openai
from utils import calculate_lstm_predictions  # Import the function
# Load environment variables from .env file
load_dotenv()
# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection using environment variables
DBNAME = os.getenv('dbname')  # Updated variable name
POSTGRES_USER = os.getenv('postgres_user')  # Updated variable name
POSTGRES_PASSWORD = os.getenv('postgres_password')  # Updated variable name
POSTGRES_HOST = os.getenv('postgres_host')  # Updated variable name
OPENAI_API_KEY = os.getenv('openai_api_key')  # Updated variable name
OPENAI_API_URL = os.getenv('openai_api_url')

# Construct the database URI
DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{DBNAME}'
engine = create_engine(DATABASE_URI)

# Set your OpenAI API key
openai.api_key = OPENAI_API_KEY

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        # Extract data sent by the application
        #price_trends = data.get('priceTrends', [])
        volatility = data.get('volatility')
        support_resistance = data.get('supportResistance', {})
        support = support_resistance.get('support')
        resistance = support_resistance.get('resistance')

        # Generate a summary of open and close prices for the prompt
        '''trend_summary = ", ".join(
            [f"Open: {entry['open']}, Close: {entry['close']}" for entry in price_trends]
        )'''

        # Construct a prompt for ChatGPT
        #- Price Trends (Open/Close): {trend_summary}
        prompt = f"""
        Given the following data:
        
        - Volatility: {volatility}
        - Support Level: {support}
        - Resistance Level: {resistance}

        Provide an analytical insight for investors. Include risk levels (low, moderate, high) and suggestions.
        """

        # Prepare the HTTP request payload
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4",  # Use "gpt-3.5-turbo" if you're using GPT-3.5
            "messages": [
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }

        # Send the HTTP POST request
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Parse the response JSON
        response_json = response.json()  # Parse JSON from the response
        insights = response_json["choices"][0]["message"]["content"]
        return jsonify({'insights': insights})
    except requests.exceptions.RequestException as e:
        # Handle HTTP request errors
        return jsonify({'error': f"HTTP Request failed: {str(e)}"}), 500
    except Exception as e:
        # Handle other errors
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run the server on port 5001
