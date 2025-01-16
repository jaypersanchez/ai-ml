import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras import metrics
from sklearn.preprocessing import MinMaxScaler

def calculate_lstm_predictions(close_prices):
    """
    Generate LSTM predictions for cryptocurrency prices.
    """
    # Prepare data for prediction
    scaler = MinMaxScaler()
    scaled_prices = scaler.fit_transform(close_prices.values.reshape(-1, 1))

    look_back = 30
    X = [scaled_prices[i:i + look_back] for i in range(len(scaled_prices) - look_back)]
    X = np.array(X)

    # Load the pre-trained LSTM model with custom_objects
    model_path = os.path.join(os.path.dirname(__file__), 'lstm_model.h5')
    print(f"Loading model from: {model_path}")
    model = load_model(model_path, custom_objects={'mse': metrics.MeanSquaredError()})

    # Generate predictions
    predictions = model.predict(X)
    predictions = scaler.inverse_transform(predictions)  # Scale back to original range

    # Return as a list
    return predictions.flatten().tolist()