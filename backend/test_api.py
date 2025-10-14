import requests
import json
from pathlib import Path

def test_health():
    print("Testing /health endpoint...")
    response = requests.get('http://localhost:5000/health')
    print(f"Status Code: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_image_prediction(image_path):
    print(f"\nTesting /predict/image with {image_path}...")
    try:
        with open(image_path, 'rb') as img:
            files = {'image': img}
            response = requests.post('http://localhost:5000/predict/image', files=files)
        print(f"Status Code: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_feature_prediction():
    print("\nTesting /predict/features with sample data...")
    data = {
        'koi_period': 10.3,
        'koi_duration': 2.5,
        'koi_fpflag_nt': 0,
        'koi_fpflag_ss': 0,
        'koi_fpflag_co': 0,
        'koi_fpflag_ec': 0,
        'koi_depth': 1000.5,
        'koi_prad': 1.2,
        'koi_sma': 0.5,
        'koi_impact': 0.3,
        'koi_ror': 0.01,
        'koi_steff': 5000,
        'koi_srad': 1.0,
        'koi_smass': 1.0,
        'koi_slogg': 4.5,
        'koi_smet': 0.0,
        'koi_teq': 2500,
        'koi_model_snr': 10.5,
        'koi_num_transits': 10
    }
    
    try:
        response = requests.post('http://localhost:5000/predict/features', json=data)
        print(f"Status Code: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # First, test the health endpoint
    if not test_health():
        print("Health check failed. Make sure the server is running.")
        exit(1)
    
    # Test image prediction (provide a path to a test image)
    test_image = input("Enter path to test image (or press Enter to skip): ").strip('"')
    if test_image and Path(test_image).exists():
        test_image_prediction(test_image)
    
    # Test feature prediction
    test_feature_prediction()
