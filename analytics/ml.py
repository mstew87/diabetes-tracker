import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from tracker.models import GlucoseReading
from datetime import datetime, timedelta

def predict_next_glucose(user, hours_ahead=2):
    """
    Predict glucose level for a user in a given number of hours using linear regression.
    
    Parameters:
    user (User): The user to predict for
    hours_ahead (int): How many hours into the future to predict
    
    Returns:
    dict: Prediction results with predicted value and confidence
    """
    # Get at least 20 readings
    readings = GlucoseReading.objects.filter(user=user).order_by('-timestamp')[:50]
    
    if readings.count() < 20:
        return {
            'success': False,
            'message': 'Not enough data for prediction. Need at least 20 readings.',
            'prediction': None
        }
    
    # Convert to DataFrame
    data = []
    for reading in readings:
        # Extract hour as a feature
        hour = reading.timestamp.hour
        # Extract features from model
        data.append({
            'glucose': reading.glucose_level,
            'timestamp': reading.timestamp,
            'hour': hour,
            'carbs': reading.carbs or 0,  # Replace None with 0
            'insulin': reading.insulin or 0,  # Replace None with 0
            'reading_time': reading.reading_time,
        })
    
    df = pd.DataFrame(data)
    
    # Add time-based features
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Create one-hot encoding for reading_time
    reading_time_dummies = pd.get_dummies(df['reading_time'], prefix='time')
    df = pd.concat([df, reading_time_dummies], axis=1)
    
    # Add lag features (previous glucose readings)
    df['glucose_lag1'] = df['glucose'].shift(-1)
    df['glucose_lag2'] = df['glucose'].shift(-2)
    
    # Drop rows with NaN values (from shift operation)
    df = df.dropna()
    
    # Features and target
    X = df.drop(['glucose', 'timestamp', 'reading_time'], axis=1)
    y = df['glucose']
    
    # Split data
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    except ValueError:
        return {
            'success': False,
            'message': 'Not enough data for train/test split.',
            'prediction': None
        }
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    # Prepare prediction data
    last_reading = readings.first()
    next_timestamp = datetime.now() + timedelta(hours=hours_ahead)
    next_hour = next_timestamp.hour
    
    # Determine likely reading_time based on hour
    if 5 <= next_hour < 8:
        reading_time = GlucoseReading.FASTING
    elif 8 <= next_hour < 10:
        reading_time = GlucoseReading.BEFORE_BREAKFAST
    elif 10 <= next_hour < 12:
        reading_time = GlucoseReading.AFTER_BREAKFAST
    elif 12 <= next_hour < 14:
        reading_time = GlucoseReading.BEFORE_LUNCH
    elif 14 <= next_hour < 17:
        reading_time = GlucoseReading.AFTER_LUNCH
    elif 17 <= next_hour < 19:
        reading_time = GlucoseReading.BEFORE_DINNER
    elif 19 <= next_hour < 22:
        reading_time = GlucoseReading.AFTER_DINNER
    elif 22 <= next_hour or next_hour < 5:
        reading_time = GlucoseReading.BEDTIME
    else:
        reading_time = GlucoseReading.OTHER
    
    # Create prediction feature vector
    pred_data = {
        'hour': next_hour,
        'carbs': last_reading.carbs or 0,
        'insulin': last_reading.insulin or 0,
        'day_of_week': next_timestamp.weekday(),
        'is_weekend': 1 if next_timestamp.weekday() >= 5 else 0,
        'glucose_lag1': last_reading.glucose_level,
        'glucose_lag2': readings[1].glucose_level if len(readings) > 1 else last_reading.glucose_level,
    }
    
    # Add one-hot encoding for reading_time
    for code, _ in GlucoseReading.READING_TIME_CHOICES:
        pred_data[f'time_{code}'] = 1 if code == reading_time else 0
    
    # Convert to DataFrame with same columns as training data
    pred_df = pd.DataFrame([pred_data])
    
    # Ensure pred_df has the same columns as X_train (in the same order)
    pred_df = pred_df.reindex(columns=X.columns, fill_value=0)
    
    # Scale the prediction data
    pred_scaled = scaler.transform(pred_df)
    
    # Make prediction
    prediction = model.predict(pred_scaled)[0]
    
    # Calculate confidence (simplified - based on model score)
    score = model.score(scaler.transform(X_test), y_test)
    confidence = max(0, min(100, score * 100))  # Convert to percentage, clamped between 0-100
    
    return {
        'success': True,
        'prediction': round(prediction, 1),
        'confidence': round(confidence, 1),
        'expected_time': reading_time,
        'timestamp': next_timestamp,
    } 