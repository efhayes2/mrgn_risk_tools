# LIKELY TO BE DEPRECATED
# fetch_solana_minute_candles.py does this job


import os
import time
import requests
import pandas as pd
import datetime
import json

# === CONFIG ===
API_KEY = 'befde4ed-e89c-4302-a7c0-5714d3774c5f'
CSV_FILE = 'c:/data/jito_solana_1min_ohlcv_backward.csv'
TOKEN = 'So11111111111111111111111111111111111111112'  # SOL
URL = f'https://data.solanatracker.io/chart/{TOKEN}'
HEADERS = {'x-api-key': API_KEY}
TYPE = '1m'         # 1-minute candles
LIMIT = 1000        # fetch 1000 minutes per batch (~16.7 hours)

# Set end time to July 23, 2025 @ midnight UTC
INITIAL_END = int(datetime.datetime(2025, 7, 23, 0, 0).timestamp())
# Stop at Jan 1, 2025 @ midnight UTC
MIN_START = int(datetime.datetime(2025, 1, 1, 0, 0).timestamp())

# === Determine Start Point ===
if os.path.exists(CSV_FILE):
    df_existing = pd.read_csv(CSV_FILE, parse_dates=['timestamp'])  # ✅ parse timestamp correctly
    first_ts = int(df_existing['timestamp'].min().timestamp())
    print(f"Resuming from {datetime.datetime.fromtimestamp(first_ts)}")
    current_end = first_ts - 1
else:
    current_end = INITIAL_END
    print(f"Starting backward fetch from {datetime.datetime.fromtimestamp(current_end)}")

# === MAIN LOOP ===
while current_end > MIN_START:
    current_start = max(current_end - (LIMIT * 60), MIN_START)

    params = {
        'type': TYPE,
        'time_from': current_start,
        'time_to': current_end,
        'removeOutliers': 'false'
    }

    try:
        response = requests.get(URL, headers=HEADERS, params=params)
        response.raise_for_status()
        parsed = json.loads(response.text)
        batch = parsed.get("oclhv", [])
    except Exception as e:
        print(f"API error: {e}")
        time.sleep(10)
        continue

    if not batch:
        print("No more data returned. Exiting.")
        break

    df = pd.DataFrame(batch)
    df['timestamp'] = pd.to_datetime(df['time'], unit='s', utc=True)
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.sort_values('timestamp', inplace=True)

    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE, parse_dates=['timestamp'])
        df_combined = pd.concat([df, df_existing], ignore_index=True)
        df_combined.drop_duplicates(subset='timestamp', inplace=True)
        df_combined.sort_values('timestamp', inplace=True)
        df_combined.to_csv(CSV_FILE, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

    print(f"✅ Saved {len(df)} candles: {df['timestamp'].iloc[0]} → {df['timestamp'].iloc[-1]}")

    # Step back to the next chunk
    current_end = int(df['timestamp'].iloc[0].timestamp()) - 1
    time.sleep(1)

print("🎉 Done! Reached Jan 1, 2025.")
