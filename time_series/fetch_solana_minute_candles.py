from utils.tokenDict import token_name_to_address_dict

import datetime
import json
import os
import pandas as pd
import requests
import time


start_time = time.time()

# bSol, LST, mSOL, Wrapped Sol, BNSOL, bbSOL
token = 'hSOL'
token_address = token_name_to_address_dict[token]

# === CONFIG ===
API_KEY = 'befde4ed-e89c-4302-a7c0-5714d3774c5f'
URL = f'https://data.solanatracker.io/chart/{token_address}'
HEADERS = {'x-api-key': API_KEY}
TYPE = '15s'         # candle length
LIMIT = 4000 if TYPE == '15s' else 1000


CSV_FILE = 'c:/data/crypto/prices/' + token + '_' + TYPE + '_ohlcv_backward.csv'

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

batch = []
empty_batch_count = 0
# === MAIN LOOP ===
while True:
    if current_end <= MIN_START:
        print("✅ Reached MIN_START timestamp.")
        break

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
        empty_batch_count += 1
        start_str = datetime.datetime.utcfromtimestamp(current_start).isoformat() + "Z"
        end_str = datetime.datetime.utcfromtimestamp(current_end).isoformat() + "Z"
        print(f"⚠️ Empty batch #{empty_batch_count} for range {start_str} → {end_str}")

        if empty_batch_count >= 3:
            print("🚪 Exiting after 3 empty batches.")
            break
        time.sleep(2)
        current_end -= LIMIT * 60  # still move back in time to avoid stalling
        continue
    else:
        empty_batch_count = 0  # reset on success

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

reached = datetime.datetime.utcfromtimestamp(current_end).isoformat() + "Z"
print(f"🎉 Done! Reached {reached}")


end_time = time.time()
elapsed = end_time - start_time

# Format 1: Raw seconds
print(f"⏱️ Elapsed time: {elapsed:.2f} seconds")

# Format 2: HH:MM:SS
h, m = divmod(int(elapsed), 3600)
m, s = divmod(m, 60)
print(f"⏳ Elapsed time: {h:02d}:{m:02d}:{s:02d}")
