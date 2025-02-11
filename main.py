from flask import Flask, request, jsonify
import requests
import io
import numpy as np
import cv2
from PIL import Image
from pop_score import get_poptotal_by_dname
from detection_image import call_model

app = Flask(__name__)

def load_image(image_path):
    """Loads an image from a local path or URL into a NumPy array."""
    try:
        if image_path.startswith("http"):  # 🔥 If it's a URL
            response = requests.get(image_path, stream=True)
            response.raise_for_status()
            image_bytes = io.BytesIO(response.content)  
            image = Image.open(image_bytes).convert("RGB")  
        else:  # 🔥 If it's a local file path
            image = Image.open(image_path).convert("RGB")

        return np.array(image)  # Convert to NumPy for OpenCV processing
    except Exception as e:
        raise RuntimeError(f"Failed to load image: {str(e)}")

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        data = request.get_json()
        case_id = data.get('case_id')
        image_path = data.get('image_path')
        model_name = data.get('model_name')
        city_name = data.get('city_name')
        
        if not all([case_id, model_name, city_name, image_path]):
            return jsonify({"error": "Missing required fields: 'case_id', 'model_name', 'city_name', 'image_path'"}), 400
        
        # Load image (from URL or local path)
        image_np = load_image(image_path)

        # Call model (pass in-memory image)
        result = call_model(model_name, image_np, case_id)

        # Get population score
        pop_score = get_poptotal_by_dname(city_name)

        return jsonify({
            "case_id": case_id,
            "class_detected": result["classes_detected"],
            "damage_score": result["damage_score"],
            "pop_score": pop_score,
            "processed_image_url": result["image_url"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
