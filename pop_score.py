import pandas as pd

csv_file_path = 'databma-bkk-people.csv'

def score_popular_filter(value): 
    value = int(value)
    if value > 170000:
        return 5
    elif 97010 <= value <= 170000:
        return 4
    elif 57010 <= value < 97000:
        return 3
    elif 26010 <= value < 57000:
        return 2
    elif value < 26000:
        return 1
    else:
        return None

def get_poptotal_by_dname(d_name):
    df = pd.read_csv("databma-bkk-people.csv")
    df.columns = df.columns.str.strip().str.lower()
    
    if 'd_name' in df.columns and 'pop_total' in df.columns:
        filtered_row = df[df['d_name'] == d_name]
        if not filtered_row.empty:
            return score_popular_filter(filtered_row.iloc[0]['pop_total'].replace(",",''))
        else:
            raise ValueError(f"d_name '{d_name}' not found in the CSV file")
    else:
        raise ValueError("data does not contain 'd_name' and 'poptotal' columns")


