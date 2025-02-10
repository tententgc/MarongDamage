from flask import Flask, request, jsonify
from pop_score import get_poptotal_by_dname
from detection_image import call_model


app = Flask(__name__)

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        data = request.get_json()

        
        image_path = data.get('image_path')
        model_name = data.get('model_name')
        city_name = data.get('city_name')
        latitude = data.get('latitude')
        longtitude = data.get('longtitude')

        
        # not adding the latitude and longtitude to must required
        if not all([image_path, model_name, city_name]):
            return jsonify({"error": "Missing required fields: 'image_path', 'model_name', 'city_name'"}), 400

       
        pop_score = get_poptotal_by_dname(city_name)

        
        damage_score, class_detected = call_model(model_name, image_path)

        
        return jsonify({
            "class_detected": class_detected,
            "damage_score": damage_score,
            "pop_score": pop_score,
            "latitude" : latitude, 
            "longtitude": longtitude
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
