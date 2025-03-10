from pathlib import Path
import pandas as pd
from firebase_admin import credentials, storage
import io
from dotenv import load_dotenv
import os

load_dotenv()
BUCKET_NAME = os.getenv("STORAGE_BUCKET")
CSV_FILE_PATH = Path("databma-bkk-people.csv")


def download_csv_from_firebase() -> pd.DataFrame:
    bucket = storage.bucket(BUCKET_NAME)
    blob = bucket.blob(str(CSV_FILE_PATH))


    if not blob.exists():
        raise FileNotFoundError(f"CSV file not found in Firebase Storage: {CSV_FILE_PATH}")

   
    csv_data = blob.download_as_text()
    df = pd.read_csv(io.StringIO(csv_data))
    
    df.columns = df.columns.str.strip().str.lower()

    return df

def score_popularity(value: int):
    if value > 170000:
        return 5
    elif 97010 <= value <= 170000:
        return 4
    elif 57010 <= value < 97010:
        return 3
    elif 26010 <= value < 57010:
        return 2
    else:
        return 1

def get_population_score(district_name: str):
    df = download_csv_from_firebase()

    if "d_name" not in df.columns or "pop_total" not in df.columns:
        raise ValueError("CSV file must contain 'd_name' and 'pop_total' columns")

    df["pop_total"] = df["pop_total"].astype(str).str.replace(",", "").astype(int)
    filtered_row = df[df["d_name"] == district_name]

    if filtered_row.empty:
        return 0  # Return 0 if district not found
    
    return score_popularity(filtered_row.iloc[0]["pop_total"])