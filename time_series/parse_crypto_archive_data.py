import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt


# === Config ===
root = r'C:\data\crypto\crypto_archive\inputs'
file_name = "mSOL_1m_ohlcv_backward.csv"
input_file = os.path.join(root, file_name)

file_name = "mSOL_1m_ohlcv_backward_processed.csv"
output_file = os.path.join(root, file_name)


# output_file = r"C:\data\crypto\crypto_archive\solana_ohlc_minute_bars_start_1_1_24_v2.csv"
histogram_file = output_file.replace(".csv", "_returns_histogram.png")
outliers_file = output_file.replace(".csv", "_returns_histogram_outliers.png")

# === Load and Parse Data ===
ohlc_rows = []
with open(input_file, "r") as file:
    for line in file:
        parts = line.strip().split("|")
        if len(parts) < 5:
            continue
        unix_ts = int(parts[0])
        utc_time = datetime.datetime.fromtimestamp(unix_ts, tz=datetime.UTC)
        open_, high, low, close = map(float, parts[1:5])
        ohlc_rows.append([utc_time, open_, high, low, close])

# === Create DataFrame ===
df = pd.DataFrame(ohlc_rows, columns=["timestamp", "open", "high", "low", "close"])
df.set_index("timestamp", inplace=True)

# === Drop rows before Selected Date ===
cutoff = datetime.datetime(2024, 7, 1, tzinfo=datetime.UTC)
df = df[df.index >= cutoff]

# === Compute minute return ===
df["return"] = df["close"].pct_change()

# === Save cleaned data ===
os.makedirs(os.path.dirname(output_file), exist_ok=True)
df.to_csv(output_file)

# === Histogram: Full Returns ===
plt.figure(figsize=(10, 6))
df["return"].hist(bins=100, color='steelblue', edgecolor='black')
plt.title("Histogram of 1-Minute Returns (All)")
plt.xlabel("Return")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()
plt.savefig(histogram_file)
plt.show()

# === Histogram: Outliers >1% or <-1% ===
outliers = df[(df["return"] > 0.01) | (df["return"] < -0.01)]

plt.figure(figsize=(10, 6))
outliers["return"].hist(bins=100, color='crimson', edgecolor='black')
plt.title("Histogram of Outlier Returns (>|1%|)")
plt.xlabel("Return")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()
plt.savefig(outliers_file)
plt.show()

# === Print top/bottom 10 returns with timestamps ===
print("\n📈 Top 10 1-Minute Returns:")
print(df["return"].nlargest(10).to_frame())

print("\n📉 Bottom 10 1-Minute Returns:")
print(df["return"].nsmallest(10).to_frame())
