import sys
import os

# Add the parent of the current directory to sys.path (i.e., project root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from token_price_record import TokenPriceRecord
from utils.database_writer import DatabaseWriter
from utils.tokenDict import get_token_address_to_name_dict


import pandas as pd
import requests
import time
import os
from datetime import datetime



def fetch_and_format_prices(token_dict: dict) -> pd.DataFrame:
    ids_param = ",".join(token_dict.keys())
    url = f"https://lite-api.jup.ag/price/v2?ids={ids_param}&showExtraInfo=true"

    response = requests.get(url)
    response.raise_for_status()
    raw_data = response.json()["data"]

    records = []
    for token_id, info in raw_data.items():
        if info is None:
            continue
        symbol = token_dict[token_id]
        price = float(info["price"])
        info = info["extraInfo"]
        record = TokenPriceRecord.from_extra_info(symbol, price, info)
        records.append(record)

    return pd.DataFrame(records)

import pandas as pd

def format_dataframe_3dp(df: pd.DataFrame) -> pd.DataFrame:
    float_cols = df.select_dtypes(include='number').columns
    pretty_df = df.copy()
    pretty_df[float_cols] = pretty_df[float_cols].round(3)
    return pretty_df



SAVE_DIR = r"C:\data"

def save_dataframe_to_csv(df, directory: str):
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jupiter_records_{timestamp}.csv"
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved: {filepath}")

def main_loop():
    token_dict = get_token_address_to_name_dict()
    db_writer = DatabaseWriter(server="Quantum-PC1\\SQLEXPRESS", database="margin_1")

    pretty_df = None
    while True:
    # for i in range(1000):
        try:
            print(f"\n[{datetime.now()}] Fetching Jupiter price data...")
            df = fetch_and_format_prices(token_dict)
            pretty_df = format_dataframe_3dp(df)

            # Convert each row of DataFrame into a TokenPriceRecord
            records = [TokenPriceRecord(**row) for row in df.to_dict(orient="records")]

            db_writer.insert_records(records)
            print(f"[{datetime.now()}] Inserted {len(records)} records into SQL Server.")

        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error during fetch or DB insert: {e}")

        time.sleep(300)


if __name__ == "__main__":
    main_loop()
    temp = 1
