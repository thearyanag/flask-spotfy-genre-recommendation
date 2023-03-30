import pandas as pd
import librosa
from sklearn.preprocessing import MinMaxScaler
import joblib


def getmetadata2(filepath):
    # Load data from CSV file
    data = pd.read_csv('features_3_sec.csv')

    if not data.empty:
        # Remove filename column
        data = data.drop('filename', axis=1)

        # Extract features from WAV file
        new_music_path = filepath
        new_music, sr = librosa.load(new_music_path)
        new_features = librosa.feature.mfcc(y=new_music, sr=sr, n_mfcc=58)

        # Format features in the same way as CSV data
        new_features = new_features.T  # Transpose to match shape of CSV data
        
        # Extract features from CSV data
        features = data.iloc[:, :-1].values
        labels = data.iloc[:, -1].values
        
        # Scale features to common range
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_features = scaler.fit_transform(features)
        new_scaled_features = scaler.transform(new_features)  # Scale using same scaler as CSV data
        new_scaled_features = new_scaled_features.reshape(1, -1)[:, :scaled_features.shape[1]] # Reshape to match shape of CSV data
        loaded_model = joblib.load("classifier.sav")
        predicted_genre = loaded_model.predict(new_scaled_features)[0]
        print(f"Predicted genre: {predicted_genre}")
        return predicted_genre
    else:
        print("Error: CSV file is empty or cannot be found.")

