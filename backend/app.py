import io
import os
import sys
import pickle
import atexit
from pathlib import Path

import cv2
import numpy as np
import torch
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image
from sklearn.preprocessing import StandardScaler

# Get the absolute path to the root directory
ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Model files with absolute paths
CNN_MODEL_PATH = MODELS_DIR / "kepler_1d_cnn_model.pth"
CNN_SCALER_PATH = MODELS_DIR / "cnn_scaler.pkl"
XGB_MODEL_PATH = MODELS_DIR / "xgboost_model.pkl"
XGB_SCALER_PATH = MODELS_DIR / "xgb_scaler.pkl"

# Initialize Flask app with correct paths
app = Flask(__name__,
            static_folder=str(ROOT_DIR / 'frontend' / 'static'),
            template_folder=str(ROOT_DIR / 'frontend' / 'templates'))

# CNN Model
class Kepler1DCNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = torch.nn.Conv1d(1, 16, kernel_size=5, padding=2)
        self.bn1 = torch.nn.BatchNorm1d(16)
        self.conv2 = torch.nn.Conv1d(16, 32, kernel_size=5, padding=2)
        self.bn2 = torch.nn.BatchNorm1d(32)
        self.conv3 = torch.nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.bn3 = torch.nn.BatchNorm1d(64)
        self.pool = torch.nn.MaxPool1d(2)
        self.fc1 = torch.nn.Linear(64 * 1598, 128)
        self.fc2 = torch.nn.Linear(128, 2)

    def forward(self, x):
        x = torch.relu(self.bn1(self.conv1(x)))
        x = self.pool(x)
        x = torch.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        x = torch.relu(self.bn3(self.conv3(x)))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def load_models():
    """Load all required models and scalers with error handling."""
    models = {}
    try:
        # Load CNN model
        if not CNN_MODEL_PATH.exists():
            raise FileNotFoundError(f"CNN model not found at {CNN_MODEL_PATH}")
        
        cnn_model = Kepler1DCNN()
        cnn_model.load_state_dict(torch.load(str(CNN_MODEL_PATH), map_location='cpu'))
        cnn_model.eval()
        models['cnn'] = cnn_model
        
        # Load XGBoost model
        if not XGB_MODEL_PATH.exists():
            raise FileNotFoundError(f"XGBoost model not found at {XGB_MODEL_PATH}")
        
        with open(XGB_MODEL_PATH, 'rb') as f:
            models['xgb'] = pickle.load(f)
            
        # Load scalers
        scalers = {}
        for name, path in [('cnn', CNN_SCALER_PATH), ('xgb', XGB_SCALER_PATH)]:
            if path.exists():
                with open(path, 'rb') as f:
                    scalers[name] = pickle.load(f)
            else:
                print(f"Warning: {name} scaler not found at {path}")
        models['scalers'] = scalers
        
        return models
        
    except Exception as e:
        print(f"Error loading models: {str(e)}")
        sys.exit(1)

# Load models when the application starts
models = load_models()

# Initialize default scalers if not found
cnn_scaler = models['scalers'].get('cnn', StandardScaler())
xgb_scaler = models['scalers'].get('xgb', StandardScaler())

def preprocess_image(image_file):
    """Preprocess the uploaded image file."""
    try:
        # Read image file
        image = Image.open(io.BytesIO(image_file.read()))
        image = np.array(image.convert('L'))  # Convert to grayscale
        return image
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

def predict_with_cnn(image):
    """Make prediction using CNN model."""
    try:
        # Preprocess image and convert to tensor
        flux = image_to_flux(image)
        flux = cnn_scaler.transform(flux.reshape(1, -1))
        flux_tensor = torch.FloatTensor(flux).unsqueeze(0)  # Add batch and channel dims
        
        # Make prediction
        with torch.no_grad():
            outputs = models['cnn'](flux_tensor)
            _, predicted = torch.max(outputs, 1)
            probabilities = torch.softmax(outputs, dim=1)
            
        return {
            'prediction': int(predicted[0]),
            'confidence': {
                'exoplanet': float(probabilities[0][1]) * 100,
                'no_exoplanet': float(probabilities[0][0]) * 100
            }
        }
    except Exception as e:
        raise ValueError(f"Prediction error: {str(e)}")

def predict_with_xgboost(features):
    """Make prediction using XGBoost model."""
    try:
        # Scale features
        features_scaled = xgb_scaler.transform([features])
        # Make prediction
        prediction = models['xgb'].predict_proba(features_scaled)[0]
        return {
            'is_exoplanet': bool(prediction[1] > 0.5),
            'prediction': float(prediction[1]),
            'confidence': float(max(prediction)) * 100
        }
    except Exception as e:
        raise ValueError(f"XGBoost prediction error: {str(e)}")

@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory(str(ROOT_DIR / 'frontend'), 'index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'models_loaded': {
            'cnn': 'cnn' in models,
            'xgb': 'xgb' in models
        }
    })

@app.route('/api/predict/image', methods=['POST'])
def predict_image():
    """Endpoint for image-based prediction using CNN."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Preprocess image
        image = preprocess_image(file)
        
        # Make prediction
        result = predict_with_cnn(image)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/features', methods=['POST'])
def predict_features():
    """Endpoint for feature-based prediction using XGBoost."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required features
        required_features = ['feature1', 'feature2', 'feature3']  # Update with actual feature names
        if not all(feature in data for feature in required_features):
            return jsonify({'error': 'Missing required features'}), 400
            
        # Convert features to list in the correct order
        features = [float(data[feature]) for feature in required_features]
        
        # Make prediction
        result = predict_with_xgboost(features)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/<path:path>')
def serve_any(path):
    """Serve static files from frontend directory."""
    try:
        # Try to serve from static directory first
        return send_from_directory(str(ROOT_DIR / 'frontend' / 'static'), path)
    except:
        try:
            # If not found in static, try to serve from root frontend directory
            return send_from_directory(str(ROOT_DIR / 'frontend'), path)
        except:
            return jsonify({'error': 'File not found'}), 404

def save_scalers():
    """Save the current state of scalers."""
    try:
        if hasattr(cnn_scaler, 'n_samples_seen_') and cnn_scaler.n_samples_seen_ > 0:
            with open(CNN_SCALER_PATH, 'wb') as f:
                pickle.dump(cnn_scaler, f)
        if hasattr(xgb_scaler, 'n_samples_seen_') and xgb_scaler.n_samples_seen_ > 0:
            with open(XGB_SCALER_PATH, 'wb') as f:
                pickle.dump(xgb_scaler, f)
    except Exception as e:
        print(f"Error saving scalers: {e}")

# Register cleanup function
atexit.register(save_scalers)

if __name__ == '__main__':
    # Start the server
    port = int(os.environ.get('PORT', 3000))
    print(f"Starting server on port {port}...")
    print(f"Root directory: {ROOT_DIR}")
    print(f"Models directory: {MODELS_DIR}")
    print(f"Static files: {app.static_folder}")
    
    app.run(host='0.0.0.0', port=port, debug=True)