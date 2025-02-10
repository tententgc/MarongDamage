from flask import Flask, request, jsonify
from pop_score import get_poptotal_by_dname
from detection_image import call_model

# Initialize Flask application
app = Flask(__name__)

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        # Get JSON payload from request
        data = request.get_json()

        # Extract required fields
        image_path = data.get('image_path')
        model_name = data.get('model_name')
        city_name = data.get('city_name')

        # Validate request payload
        if not all([image_path, model_name, city_name]):
            return jsonify({"error": "Missing required fields: 'image_path', 'model_name', 'city_name'"}), 400

        # Get population score
        pop_score = get_poptotal_by_dname(city_name)

        # Get model detection results
        damage_score, class_detected = call_model(model_name, image_path)

        # Return response
        return jsonify({
            "class_detected": class_detected,
            "damage_score": damage_score,
            "pop_score": pop_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
