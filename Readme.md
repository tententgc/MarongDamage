
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
  
### 5. config the env
```bash
API_USERNAME=
API_PASSWORD=
BASE_URL=
CREDENTIALS_PATH=
STORAGE_BUCKET=
```

### 5. Run the API Server
```bash
python main.py
```
or 
### Install with Docker (currently have problem with network) 
```bash
docker compose up -d -build
```

The server will start at `http://0.0.0.0:8000`.

## API Usage

### **Endpoint: `/process-image`**
- **Method:** `POST`
- **Port:** `8000`
- **Request Body (JSON):**
```required```
```json
{
    "case_id" : "4",
    "image_url": "image/road1.jpg",
    "model_name": "Road_Damage", 
    "city_name": "เขตห้วยขวาง", 

}

```

Obtional  can adding 
```json
 "latitude": "100",
 "longtitude": "50" 
```
- **Response to database:**
```json
{
    "data": {
        "caseId": 4,
        "damaged_value": "9",
        "detail_detect": "Surface_Defects",
        "picture_done": "https://storage.googleapis.com/marong-a42b2.firebasestorage.app/output_images/output_4_2025-03-10T01%3A57%3A09.866.jpg",
        "status": "waiting",
        "updateAt": "2025-03-10T01:57:15.425"
    },
    "statusCode": "200",
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

### **Endpoint: `/group_case`**
- **Method:** `GET`
- **Port:** `8000`
```json
[  [
        {
            "case_id": "7",
            "category": "Wire_Damage",
            "date_closed": null,
            "date_opened": "null",
            "location": {
                "coordinates": [
                    "13.722347",
                    "101"
                ],
                "description": "location detail"
            },
            "picture": "picture",
            "picture_done": null,
            "status": "Waiting"
        }
    ],
    [
        {
            "case_id": "8",
            "category": "Damaged_sidewalk",
            "date_closed": null,
            "date_opened": "null",
            "location": {
                "coordinates": [
                    "13.722347",
                    "100.562345"
                ],
                "description": "location detail"
            },
            "picture": "picture",
            "picture_done": null,
            "status": "Waiting"
        },
        {
            "case_id": "9",
            "category": "Damaged_sidewalk",
            "date_closed": null,
            "date_opened": "null",
            "location": {
                "coordinates": [
                    "13.722348",
                    "100.562345"
                ],
                "description": "location detail"
            },
            "picture": "picture",
            "picture_done": null,
            "status": "Waiting"
        }
    ]
]
```



