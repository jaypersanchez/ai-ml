import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from flask_cors import CORS
import numpy as np

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection using environment variables
DBNAME = os.getenv('dbname')
POSTGRES_USER = os.getenv('postgres_user')
POSTGRES_PASSWORD = os.getenv('postgres_password')
POSTGRES_HOST = os.getenv('postgres_host')

# Construct the database URI
DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{DBNAME}'
engine = create_engine(DATABASE_URI)

@app.route('/api/get_coin_id', methods=['GET'])
def get_coin_id():
    """Fetch the coin_id based on the coin name."""
    coin_name = request.args.get('name')
    if not coin_name:
        return jsonify({'error': 'Coin name is required.'}), 400

    with engine.connect() as connection:
        query = text("SELECT coin_id FROM coin_mapping WHERE name ILIKE :name")
        result = connection.execute(query, {"name": coin_name}).fetchone()

    if result:
        return jsonify({'coin_id': result[0]})
    else:
        return jsonify({'error': 'Coin not found.'}), 404

'''This is the price trends endpoint requires data to be trained in order to predict trends'''
@app.route('/api/price_trends', methods=['GET'])
def price_trends():
    """Fetch price trends for a given coin_id."""
    coin_id = request.args.get('coin_id')
    timeframe = request.args.get('timeframe', 'month')

    if not coin_id:
        return jsonify({'error': 'coin_id is required.'}), 400

    try:
        with engine.connect() as connection:
            # Query to fetch price trends from the crypto_data table
            query = text("""
                SELECT timestamp, open, high, low, close
                FROM crypto_data
                WHERE coin_id = :coin_id
            """)
            result = connection.execute(query, {"coin_id": coin_id, "timeframe": timeframe}).fetchall()

            # Format the result into a list of dictionaries
            historical_data = [
                {
                    "timestamp": row[0].isoformat(),
                    "open": row[1],
                    "high": row[2],
                    "low": row[3],
                    "close": row[4]
                }
                for row in result
            ]

            return jsonify({"historical_data": historical_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/volatility', methods=['GET'])
def volatility():
    """Calculate volatility for a given coin_id."""
    coin_id = request.args.get('coin_id')
    timeframe = request.args.get('timeframe', 'month')

    if not coin_id:
        return jsonify({'error': 'coin_id is required.'}), 400

    try:
        with engine.connect() as connection:
            # Query to fetch closing prices from the crypto_data table
            query = text("""
                SELECT close
                FROM crypto_data
                WHERE coin_id = :coin_id
                """)
            result = connection.execute(query, {"coin_id": coin_id, "timeframe": timeframe}).fetchall()

            # Extract closing prices into a list
            closing_prices = [row[0] for row in result]

            if len(closing_prices) < 2:
                return jsonify({'error': 'Not enough data to calculate volatility.'}), 400

            # Calculate volatility (standard deviation of returns)
            returns = np.diff(closing_prices) / closing_prices[:-1]  # Calculate returns
            volatility = np.std(returns)  # Standard deviation of returns

            return jsonify({'volatility': volatility})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ensure the server listens on port 5001