import requests
from requests.auth import HTTPBasicAuth
from geopy.distance import geodesic
from dotenv import load_dotenv
import os
from flask import Flask, jsonify

load_dotenv()

app = Flask(__name__)

BASE_URL = os.getenv("BASE_URL")
username = os.getenv("API_USERNAME")
password = os.getenv("API_PASSWORD")

auth = (username, password)
def fetch_cases():
    """Fetch all cases from the API."""
    response = requests.get(f"{BASE_URL}/api/overview/all", auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch cases: {response.status_code}")
    return response.json().get("data", {}).get("toMap", [])

def group_cases(cases, distance_threshold=50):
    """Group cases that are within a specified distance and share the same category."""
    grouped_cases = []
    processed_cases = set()
    
    for case in cases:
        case_id = case.get("case_id")
        category = case.get("category")
        coordinates = case.get("location", {}).get("coordinates")
        
        if not coordinates or case_id in processed_cases:
            continue
        
        coordinates = tuple(map(float, coordinates))
        group = [case]  # Store full case data
        processed_cases.add(case_id)
        
        for other_case in cases:
            other_id = other_case.get("case_id")
            other_category = other_case.get("category")
            other_coordinates = other_case.get("location", {}).get("coordinates")
            
            if not other_coordinates or other_id in processed_cases or other_id == case_id:
                continue
            
            other_coordinates = tuple(map(float, other_coordinates))
            
            if other_category == category and geodesic(coordinates, other_coordinates).meters <= distance_threshold:
                group.append(other_case)  # Append full case data
                processed_cases.add(other_id)
        
        grouped_cases.append(group)
    
    return grouped_cases

def get_grouped_cases():
    """Fetch cases and return them grouped."""
    cases = fetch_cases()
    return group_cases(cases)