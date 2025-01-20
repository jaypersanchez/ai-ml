import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from flask_cors import CORS
import psycopg2

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

@app.route('/api/price_trends', methods=['GET'])
def price_trends():
    """Fetch price trends for a given coin_id."""
    coin_id = request.args.get('coin_id')
    timeframe = request.args.get('timeframe', 'month')

    # Your existing logic to fetch price trends...

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ensure the server listens on port 5001