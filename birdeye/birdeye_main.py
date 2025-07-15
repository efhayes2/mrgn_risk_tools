import requests

# url = 'https://public-api.birdeye.so/defi/v3/token/exit-liquidity?address=So11111111111111111111111111111111111111112'
#
# headers = {
#     'accept': 'application/json',
#     'x-chain': 'base',
#     'X-API-KEY': '0d455dc9e38a4f6b9a4869003a30db78'
# }
#
# response = requests.get(url, headers=headers)
#
# print(response.text)

import requests
import time

TokenAddressLookup = {
    "SOL": "So11111111111111111111111111111111111111112",
    "bbSOL": "Bybit2vBJGhPF52GBdNaQfUJ6ZpThSgHBobjWZpLPb4B",
    "BNSOL": "BNso1VUJnh4zcfpZa6986Ea66P6TCp59hvtNJ8b1X85",
    "bonkSOL": "BonK1YhkXEGLZzwtcvRTip3gAL9nCeQD7ppZBLXhtTs",
    "bSOL": "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1",
    "compassSOL": "Comp4ssDzXcLeu2MnLuGNNFC4cmLPMng8qWHPvzAMU1h",
    "ezSOL": "ezSoL6fY1PVdJcJsUpe5CM3xkfmy3zoVCABybm5WtiC",
    "hSOL": "he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A",
    "INF": "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm",
    "JitoSOL": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",
    "JSOL": "7Q2afV64in6N6SeZsAAB81TJzwDoD6zpqmHkzi9Dcavn",
    "jucySOL": "jucy5XJ76pHVvtPZb5TKRcGQExkwit2P5s4vY8UzmpC",
    "jupSOL": "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v",
    "LST": "LSTxxxnJzKDFSLr4dUkPcmCf5VyryEqzPLz5j4bpxFp",
    "mSOL": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
    "picoSOL": "picobAEvs6w7QEknPce34wAE4gknZA9v5tTonnmHYdX"
}

headers = {
        'accept': 'application/json',
        'x-chain': 'solana',
        'X-API-KEY': '0d455dc9e38a4f6b9a4869003a30db78'
}


for symbol, address in TokenAddressLookup.items():
    url = f"https://public-api.birdeye.so/defi/v3/token/exit-liquidity?address={address}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"\n📦 {symbol} ({address}):")
        print(data)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data for {symbol}: {e}")

    # Optional: Avoid rate limits
    time.sleep(1)  # Add delay if needed
