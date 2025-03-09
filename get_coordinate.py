import requests
from requests.auth import HTTPBasicAuth
from geopy.distance import geodesic
from dotenv import load_dotenv
import os

load_dotenv()

def get_coordinate(case_id):
    base_url = os.getenv("BASE_URL")
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    auth = HTTPBasicAuth(username, password)
    

    response = requests.get(f"{base_url}/api/overview/all", auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch case details: {response.status_code}")
    all_cases = response.json()


    for case in all_cases.get("data", {}).get("toMap", []):
        if case.get("case_id") == case_id:
            coordinates = case.get("location", {}).get("coordinates")
            if coordinates:
                return {"case_id": case_id, "coordinates": tuple(map(float, coordinates))}  # Convert to (latitude, longitude)
    
    return None

def get_all_coordinates():
    base_url = "http://localhost:8080"
    auth = HTTPBasicAuth("msaidmin@gmail.com", "hashed_password_2")
    
   
    response = requests.get(f"{base_url}/api/overview/all", auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch all cases: {response.status_code}")
    all_cases = response.json()
    
    
    coordinates_list = []
    for case in all_cases.get("data", {}).get("toMap", []):
        coordinates = case.get("location", {}).get("coordinates")
        if coordinates:
            coordinates_list.append({"case_id": case.get("case_id"), "coordinates": tuple(map(float, coordinates))})
    
    return coordinates_list

def find_nearby_coordinates(case_id, radius_km=1.0):
    target_case = get_coordinate(case_id)
    if not target_case:
        raise Exception("Target case coordinates not found")
    
    target_coord = target_case["coordinates"]
    all_cases = get_all_coordinates()
    
    nearby_cases = [case for case in all_cases if case["case_id"] != case_id and geodesic(target_coord, case["coordinates"]).km <= radius_km]
    
    return nearby_cases
