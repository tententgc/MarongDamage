import torch
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage
import io

cred = credentials.Certificate("marong-a42b2-firebase-adminsdk-fbsvc-dd6c55f88a.json") 
firebase_admin.initialize_app(cred, {"storageBucket": "marong-a42b2.firebasestorage.app"}) 

def model_select(text_value): 
    return f"weight/{text_value}.pt"

def detect_objects(image_np, model):
    """Runs YOLO detection on an in-memory image."""
    result = model.predict(image_np, save_conf=True, show=True)
    img_result = result[0].plot()  # Get annotated image as numpy array

    detected_classes = []
    if result[0].masks is not None:
        for counter, detection in enumerate(result[0].masks.data):
            cls_id = int(result[0].boxes[counter].cls.item()) 
            cls_name = model.names[cls_id]                    
            detected_classes.append(cls_name)                

    return img_result, detected_classes

def upload_to_firebase(image_np, case_id):
    """Uploads image directly to Firebase Storage without saving locally."""
    
    bucket = storage.bucket()
    blob = bucket.blob(f"output_images/output_{case_id}.jpg")

    # Convert numpy array to bytes
    _, buffer = cv2.imencode(".jpg", image_np)
    image_bytes = io.BytesIO(buffer)

    # Upload image bytes to Firebase
    blob.upload_from_file(image_bytes, content_type="image/jpeg")

    # Get the public URL
    return blob.public_url

def score_credit(class_values, model_name): 
    condition_dataset = {
        "road": {"value":5, "case":{ "Cracks":4, "Patch": 3, "Potholes": 2, "Surface_Defects":1 }},
        "bridge": {"value":3.5,"case":{
            "น้ำท่วมขัง": 2, "พื้นผิวสะพานเสื่อมสภาพ พื้นสะพานลื่น": 1, "ราวสะพานชำรุด ชิ้นส่วนเสียหาย": 3,
            "สะพานทรุด": 5, "สิ่งกีดขวางบนสะพาน": 1, "โครงสร้างสะพานแตกร้าว": 4, "ไฟส่องสว่างบนสะพานไม่ทำงาน":3 }},
        "footpath":{"value":2.5, "case": {
            "Crackedcracked sidewalk": 5, "Garbage on the sidewalk": 1, "Obstructions on the sidewalk": 3,
            "Roughuneven pavement": 2, "Trees or plants on the sidewalk"  : 2, "collapsed sidewalk" : 3 }},
        "wire":{"value": 1 , "case":{ 
            "Broken-or-tilted-electric-pole": 5, "Electrical-wires-across-trees": 2, "Tangled-wires": 3,
            "damaged-electrical-control-system": 4, "damaged-wire": 4, "loose-fallen-slack-wire": 3 }}
    }

    condition_score = condition_dataset[model_name]["value"]
    casedetect_score = sum(condition_dataset[model_name]["case"].get(class_value, 0) for class_value in class_values)
    return condition_score + casedetect_score

def call_model(model_name, image_np, case_id):
    """Processes an in-memory image using YOLO and uploads results to Firebase."""
    model = YOLO(model_select(model_name))
    
    # Run detection
    image_np, classes_detected = detect_objects(image_np, model)

    # Upload image to Firebase and get the URL
    firebase_url = upload_to_firebase(image_np, case_id)

    # Compute damage score
    damage_score = score_credit(classes_detected, model_name)

    return {
        "damage_score": damage_score,
        "classes_detected": classes_detected,
        "image_url": firebase_url  # ✅ Firebase-hosted image link
    }
