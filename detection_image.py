import torch
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os

def model_select(text_value): 
    map_model = f"weight/{text_value}.pt"
    return map_model

def detect_objects(image_path, output_path, model):

    result = model.predict(image_path, save_conf=True, show=True)
    img_result = result[0].plot()
    

    cv2.imwrite(output_path, img_result)

    detected_classes = []

    if result[0].masks is not None:
        for counter, detection in enumerate(result[0].masks.data):
            cls_id = int(result[0].boxes[counter].cls.item()) 
            cls_name = model.names[cls_id]                    
            detected_classes.append(cls_name)                
    return detected_classes

def score_credit(class_values, model_name): 
    condition_dataset = {"road": {"value":5, "case":{ 
        "Cracks":4, 
        "Patch": 3,
        "Potholes": 2,
        "Surface_Defects":1,
        }}, 

        "bridge": {"value":3.5,"case":{
            "น้ำท่วมขัง": 2,
            "พื้นผิวสะพานเสื่อมสภาพ พื้นสะพานลื่น": 1,
            "ราวสะพานชำรุด ชิ้นส่วนเสียหาย": 3,
            "สะพานทรุด": 5,
            "สิ่งกีดขวางบนสะพาน": 1,
            "โครงสร้างสะพานแตกร้าว": 4,
            "ไฟส่องสว่างบนสะพานไม่ทำงาน":3
            }},
        "footpath":{"value":2.5, "case": {
            "Crackedcracked sidewalk": 5,
            "Garbage on the sidewalk": 1, 
            "Obstructions on the sidewalk": 3,
            "Roughuneven pavement": 2,
            "Trees or plants on the sidewalk"  : 2, 
            "collapsed sidewalk" : 3         
            }},
        "wire":{"value": 1 , "case":{ 
            "Broken-or-tilted-electric-pole": 5, 
            "Electrical-wires-across-trees": 2,
            "Tangled-wires": 3,
            "damaged-electrical-control-system": 4, 
            "damaged-wire": 4, 
            "loose-fallen-slack-wire": 3
            }}}
    condition_score = condition_dataset[model_name]["value"]
    casedetect_score = 0
    for class_value in class_values:
        casedetect_score += condition_dataset[model_name]["case"].get(class_value, 0) 
        
    damage_score = condition_score + casedetect_score
    return damage_score



output_path = "output.jpg"  

def call_model(model_name,image_path):
    model = YOLO(model_select(model_name))
    classes_detected = detect_objects(image_path,output_path,model)
    damage_score = score_credit(classes_detected, model_name)
    return damage_score,classes_detected
