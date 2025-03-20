import torch
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime
import io
from dotenv import load_dotenv
import os

load_dotenv()
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")

cred = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})

def get_model_path(model_name: str):
    """Returns the model path based on the given model name."""
    return f"weight/{model_name}.pt"

def detect_objects(image_np: np.ndarray, model: YOLO,threshold: float = 0.5): 
    """Runs YOLO object detection on an image array."""
    results = model.predict(image_np, save_conf=True, show=True)
    processed_image = results[0].plot()
    
    detected_classes = []
    if results[0].masks is not None:
        for index, _ in enumerate(results[0].masks.data):
            class_id = int(results[0].boxes[index].cls.item())
            confidence = results[0].boxes[index].conf.item()
            
            if confidence >= threshold:
                class_name = model.names[class_id]
                detected_classes.append((class_name, confidence))

    return processed_image, detected_classes

def upload_image_to_firebase(image_np: np.ndarray, case_id: str, format: str = "jpg") -> str:

    if format.lower() not in ["jpg", "png", "webp"]:
        raise ValueError("Unsupported format. Use 'jpg', 'png', or 'webp'.")

    bucket = storage.bucket()
    
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    filename = f"output_images/output_{case_id}_{timestamp}.{format}"
    blob = bucket.blob(filename)

    # Encode image in specified format
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95] if format == "jpg" else []
    success, buffer = cv2.imencode(f".{format}", image_np, encode_param)
    
    if not success:
        raise RuntimeError(f"Failed to encode image as {format}")

    image_bytes = io.BytesIO(buffer)

    blob.upload_from_file(image_bytes, content_type=f"image/{format}")
    blob.make_public()

    return blob.public_url

def calculate_damage_score(detected_classes: list, model_name: str):
    condition_data = {
        "Road_Damage": {"value": 5, "cases": {"Cracks": 4, "Patch": 3, "Potholes": 2, "Surface_Defects": 1}},
        "Overpass_Damage": {"value": 3.5, "cases": {
            "น้ำท่วมขัง": 2, "พื้นผิวสะพานเสื่อมสภาพ พื้นสะพานลื่น": 1, "ราวสะพานชำรุด ชิ้นส่วนเสียหาย": 3,
            "สะพานทรุด": 5, "สิ่งกีดขวางบนสะพาน": 1, "โครงสร้างสะพานแตกร้าว": 4, "ไฟส่องสว่างบนสะพานไม่ทำงาน": 3}},
        "Damaged_Sidewalk": {"value": 2.5, "cases": {
            "Crackedcracked sidewalk": 5, "Garbage on the sidewalk": 1, "Obstructions on the sidewalk": 3,
            "Roughuneven pavement": 2, "Trees or plants on the sidewalk": 2, "collapsed sidewalk": 3}},
        "Wire_Damage": {"value": 1, "cases": {
            "Broken-or-tilted-electric-pole": 5, "Electrical-wires-across-trees": 2, "Tangled-wires": 3,
            "damaged-electrical-control-system": 4, "damaged-wire": 4, "loose-fallen-slack-wire": 3}}
    }

    base_score = condition_data.get(model_name, {}).get("value", 0)
    case_score = sum(condition_data[model_name]["cases"].get(cls, 0) for cls in detected_classes)
    
    return base_score + case_score

def process_image_with_model(model_name: str, image_np: np.ndarray, case_id: str):
    """Loads the YOLO model, detects objects, uploads the processed image, and calculates a damage score."""
    model = YOLO(get_model_path(model_name))

    processed_image, detected_classes = detect_objects(image_np, model)

    image_url = upload_image_to_firebase(processed_image, case_id)
    damage_score = calculate_damage_score(detected_classes, model_name)

    if detected_classes == []:
        detected_classes = ["No damage detected"]

    print(damage_score, detected_classes, image_url) 
    
    return {
        "damage_score": damage_score,
        "classes_detected": detected_classes,
        "image_url": image_url
    }


