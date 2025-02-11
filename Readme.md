
## Technologies Used
- **Flask** (API backend)
- **YOLO (Ultralytics)** (Object detection)
- **OpenCV & PIL** (Image processing)
- **Firebase Storage** (Image hosting)
- **Requests & NumPy** (Data handling)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/incident-detection-api.git
cd incident-detection-api
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Firebase
- Download the **Firebase Admin SDK JSON** file from Firebase Console.
- Save it as `firebase_service_key.json` in the project root.

### 4. Run the API Server
```bash
python main.py
```
or 
### Install with Docker 
```bash
docker compose up -d -build
```

The server will start at `http://0.0.0.0:8000`.

## API Usage

### **Endpoint: `/process-image`**
- **Method:** `POST`
- **Request Body (JSON):**
```json
{
    "case_id": "12345",
    "image_path": "https://example.com/image.jpg",  
    "model_name": "road",  
    "city_name": "Bangkok"
}

```

Obtional  can adding 
```json
 "latitude": "100",
 "longtitude": "50" 
```
- **Response:**
```json
{
    "case_id": "12345",
    "class_detected": ["Cracks", "Potholes"],
    "damage_score": 9,
    "pop_score": 500000,
    "processed_image_url": "https://firebasestorage.googleapis.com/..."
}
```

### **Using Local Images**
```json
{
    "case_id": "67890",
    "image_path": "/path/to/local/image.jpg",  
    "model_name": "bridge",  
    "city_name": "Chiang Mai"
}
```

## Project Structure
```
incident-detection-api/
├── main.py                   # Flask API server
├── detection_image.py        # YOLO model processing & Firebase upload
├── pop_score.py              # Population impact calculation
├── firebase_service_key.json # Firebase authentication (DO NOT SHARE)
├── requirements.txt          # Required dependencies
└── README.md                 # Project documentation
```


# Hellos


