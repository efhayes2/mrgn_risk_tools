from utils.database_writer import DatabaseWriter
from utils.tokenDict import get_token_name_from_address

import json
import math
import pandas as pd
from datetime import datetime, timezone


def parse_market_depth(data, writer, token):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    depth_data = data["depth_data"]

    # Estimate mid price
    overlapping = [d for d in depth_data if d.get("support", 0) > 0 and d.get("resistance", 0) > 0]
    if overlapping:
        market_price = sum(d["price"] for d in overlapping) / len(overlapping)
    else:
        prices = [d["price"] for d in depth_data]
        market_price = (min(prices) + max(prices)) / 2

    market_rows = []
    bucket_map = {}

    for entry in depth_data:
        bucket_price = entry["price"]

        # Drop records beyond ±6% of mid
        if abs(bucket_price / market_price - 1) > 0.06:
            continue

        support = entry.get("support", 0)
        resistance = entry.get("resistance", 0)

        market_rows.append({
            "token": token,
            "timestamp": timestamp,
            "bucket_price": bucket_price,
            "support": support,
            "resistance": resistance
        })

        # Bucket by 20 basis points
        bp = round((bucket_price / market_price - 1) * 10000)
        bucket = int(math.floor(bp / 20.0) * 20)

        if bucket not in bucket_map:
            bucket_map[bucket] = {
                "bucket_price": bucket_price,
                "support_in_bucket": 0,
                "resistance_in_bucket": 0
            }

        bucket_map[bucket]["support_in_bucket"] += support
        bucket_map[bucket]["resistance_in_bucket"] += resistance

    slippage_rows = []
    cumulative_support = 0
    cumulative_resistance = 0

    for bp in sorted(bucket_map):
        row = bucket_map[bp]
        support = row["support_in_bucket"]
        resistance = row["resistance_in_bucket"]
        cumulative_support += support
        cumulative_resistance += resistance

        slippage_rows.append({
            "token": token,
            "market_price": market_price,
            "timestamp": timestamp,
            "bp_from_mid": bp,
            "bucket_price": row["bucket_price"],
            "support_in_bucket": support,
            "cumulative_support": cumulative_support,
            "resistance_in_bucket": resistance,
            "cumulative_resistance": cumulative_resistance
        })

    market_df = pd.DataFrame(market_rows)
    slippage_df = pd.DataFrame(slippage_rows)

    # writer.insert_into_market_depth(market_df)
    writer.insert_into_slippage_buckets(slippage_df)




# Example usage:
if __name__ == "__main__":


    # token_address = "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn"  # JitoSOL token address
    # token_address = "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So" # mSOL token address
    token_address= "Bybit2vBJGhPF52GBdNaQfUJ6ZpThSgHBobjWZpLPb4B"
    token1 = get_token_name_from_address(token_address)


    # token = 'jitoSol'
    # file_path = "c:/users/ehayes/downloads/" + token1 + "_sample.json"
    file_path = "c:/data/" + token1 + "_sample.json"

    # file_path = "c:/data/mSol_sample.json"
    with open(file_path, 'r') as f:
        data1 = json.load(f)


    writer1 = DatabaseWriter()
    parse_market_depth(data1, writer1, token1)
