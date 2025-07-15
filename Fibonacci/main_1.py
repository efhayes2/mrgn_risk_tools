import requests
import os
import json

# === Config ===
token = 'LST'
interval = '10m'  # interpreted as 1 day
lookback = '14'  # last 10 intervals (days)

# === API Request ===
url = f'https://docs.fibonacci.fi/api/slippage/solana/{token}/aggs'
params = {
    'interval': interval,
    'lookback': lookback
}
headers = {
    'accept': '*/*',
    'Authorization': 'Bearer 3ZdDHi3cyGKRhhZ6ZjC4SuFo'
}

response = requests.get(url, headers=headers, params=params)

# === Handle Response ===
if response.status_code == 200:
    data = response.json()

    print(f"Market Depth Data for {token} (last {lookback} intervals of {interval}):")
    print(f"Total records pulled: {len(data['slippage'])}")

    print_it = False
    if print_it:
        print(data)

    # Ensure directory exists
    os.makedirs(r'C:\data', exist_ok=True)

    # Construct dynamic filename
    filename = f"{token}_market_depth_{interval}_{lookback}d.json"
    filepath = os.path.join(r'C:\data', filename)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved data to: {filepath}")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    print(response.text)
