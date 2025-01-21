from flask import Flask, request, jsonify
from pop_score import get_poptotal_by_dname
from detection_image import call_model

# Initialize the Flask app
app = Flask(__name__)

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        # Extract data from JSON request
        data = request.get_json()
        
        image_path = data.get('image_path')
        model_name = data.get('model_name')
        d_name = data.get('d_name')

        if not all([image_path, model_name, d_name]):
            return jsonify({"error": "Missing one or more required fields: 'image_path', 'model_name', 'd_name'"}), 400

        # Get population score
        pop_score = get_poptotal_by_dname(d_name)

        # Call model to get damage score and class detected
        damage_score, class_detected = call_model(model_name, image_path)

        # Return results as JSON
        return jsonify({
            "class_detected": class_detected,
            "damage_score": damage_score,
            "pop_score": pop_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask server
    app.run(host='0.0.0.0', port=8000, debug=True)
