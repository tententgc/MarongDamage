from flask import Flask, request, jsonify
import requests
import io
import numpy as np
import cv2
from PIL import Image
from datetime import datetime
from pop_score import get_population_score
from detection_image import process_image_with_model
from get_coordinate import find_nearby_coordinates
from dotenv import load_dotenv
import os
import json

class ImageProcessorAPI:
    def __init__(self):
        load_dotenv()
        self.app = Flask(__name__)
        self.base_url = os.getenv("BASE_URL")
        self.username = os.getenv("API_USERNAME")
        self.password = os.getenv("API_PASSWORD")
        self.setup_routes()
    
    def setup_routes(self):
        self.app.route('/process-image', methods=['POST'])(self.process_image)
    
    def load_image(self, image_path):
        """Loads an image from a local path or URL into a NumPy array."""
        try:
            if image_path.startswith("http"):  
                response = requests.get(image_path, stream=True)
                response.raise_for_status()
                image_bytes = io.BytesIO(response.content)  
                image = Image.open(image_bytes).convert("RGB")  
            else:  
                image = Image.open(image_path).convert("RGB")
            return np.array(image)  
        except Exception as e:
            raise RuntimeError(f"Failed to load image: {str(e)}")
    
    def process_image(self):
        try:
            data = request.get_json()
            case_id = data.get('case_id')
            image_path = data.get('image_url')
            model_name = data.get('model_name')
            city_name = data.get('city_name')

            if not all([case_id, model_name, city_name, image_path]):
                return jsonify({"error": "Missing required fields: 'case_id', 'model_name', 'city_name', 'image_path'"}), 400
            
            image_np = self.load_image(image_path)
            result = process_image_with_model(model_name, image_np, case_id)
        
            pop_score = get_population_score(city_name)
            print(result["damage_score"], pop_score)
            result["damage_score"] += pop_score

            update_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        
            update_data = {
                "caseid": case_id, 
                "damaged_value": result["damage_score"],
                "picture_done": result["image_url"],  
                "detail_detect": result["classes_detected"],
                "update_at": update_at
            }
           
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            auth = (self.username, self.password)
            api_url =  f"{self.base_url}/api/myreport/updateCase"
            update_response = requests.put(api_url, data=update_data, headers=headers, auth=auth)

            if update_response.status_code != 200:
                return jsonify({"error": "Failed to update case", "details": update_response.text}), update_response.status_code

            return jsonify(update_response.json()), update_response.status_code 
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def run(self, host='0.0.0.0', port=8000, debug=True):
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    api = ImageProcessorAPI()
    api.run()